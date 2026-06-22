#include "MyIMU.h"

extern double quat[4];
extern double gyr[3];
extern double acc[3];
extern double quat_calib[4];
extern double gyr_calib[3];
extern double acc_calib[3];

ICM_20948_I2C myICM;

// Mahony AHRS variables
float Mahony_q0 = 1.0f, Mahony_q1 = 0.0f, Mahony_q2 = 0.0f, Mahony_q3 = 0.0f;
float integralFBx = 0.0f,  integralFBy = 0.0f, integralFBz = 0.0f;
unsigned long last_imu_time = 0;

void MahonyAHRSupdateIMU(float gx, float gy, float gz, float ax, float ay, float az, float dt) {
    float recipNorm;
    float halfvx, halfvy, halfvz;
    float halfex, halfey, halfez;
    float qa, qb, qc;

    // Compute feedback only if accelerometer measurement valid
    if(!((ax == 0.0f) && (ay == 0.0f) && (az == 0.0f))) {
        recipNorm = 1.0f / sqrt(ax * ax + ay * ay + az * az);
        ax *= recipNorm;
        ay *= recipNorm;
        az *= recipNorm;        

        halfvx = Mahony_q1 * Mahony_q3 - Mahony_q0 * Mahony_q2;
        halfvy = Mahony_q0 * Mahony_q1 + Mahony_q2 * Mahony_q3;
        halfvz = Mahony_q0 * Mahony_q0 - 0.5f + Mahony_q3 * Mahony_q3;
    
        halfex = (ay * halfvz - az * halfvy);
        halfey = (az * halfvx - ax * halfvz);
        halfez = (ax * halfvy - ay * halfvx);

        float twoKi = 0.0f; // 0 to disable integral
        float twoKp = 2.0f; // 2 * proportional gain

        integralFBx += twoKi * halfex * dt;
        integralFBy += twoKi * halfey * dt;
        integralFBz += twoKi * halfez * dt;
        gx += integralFBx;
        gy += integralFBy;
        gz += integralFBz;

        gx += twoKp * halfex;
        gy += twoKp * halfey;
        gz += twoKp * halfez;
    }
    
    gx *= (0.5f * dt);
    gy *= (0.5f * dt);
    gz *= (0.5f * dt);
    qa = Mahony_q0;
    qb = Mahony_q1;
    qc = Mahony_q2;
    Mahony_q0 += (-qb * gx - qc * gy - Mahony_q3 * gz);
    Mahony_q1 += (qa * gx + qc * gz - Mahony_q3 * gy);
    Mahony_q2 += (qa * gy - qb * gz + Mahony_q3 * gx);
    Mahony_q3 += (qa * gz + qb * gy - qc * gx); 
    
    recipNorm = 1.0f / sqrt(Mahony_q0 * Mahony_q0 + Mahony_q1 * Mahony_q1 + Mahony_q2 * Mahony_q2 + Mahony_q3 * Mahony_q3);
    Mahony_q0 *= recipNorm;
    Mahony_q1 *= recipNorm;
    Mahony_q2 *= recipNorm;
    Mahony_q3 *= recipNorm;
}

void IMUBegin()
{
    Wire.begin(I2C_SDA, I2C_SCL);
    Wire.setClock(400000);
    bool initialized = false;
    while (!initialized)
    {
        myICM.begin(Wire, 1);
        if (myICM.status != ICM_20948_Stat_Ok) {
            delay(500);
        } else {
            initialized = true;
        }
    }

    // Use pure, unadulterated hardware defaults. No buggy DMP.
    myICM.startupDefault();

    IMUCalibrate();
}

void IMUCalibrate()
{    
    Serial.println("Calibrating IMU... Do not move robot!");
    delay(2000); // Give the DMP time to fully settle and converge
    
    // No FIFO to flush, just wait a moment for hardware
    delay(500);

    for (size_t i = 0; i < 100; i++)
    {
        // Wait until we actually receive a fresh hardware reading!
        while (!IMUGetData_Uncalibrated()) {
            delay(5);
        }
        
        // No quaternions in hardware reads, just raw sensors
        gyr_calib[0] += gyr[0];
        gyr_calib[1] += gyr[1];
        gyr_calib[2] += gyr[2];
        acc_calib[0] += acc[0];
        acc_calib[1] += acc[1];
        acc_calib[2] += acc[2];
        
        delay(10); // Wait for fresh readings
    }
    gyr_calib[0] /= 100.0;
    gyr_calib[1] /= 100.0;
    gyr_calib[2] /= 100.0;
    acc_calib[0] /= 100.0;
    acc_calib[1] /= 100.0;
    acc_calib[2] /= 100.0;

    Serial.println("IMU Calibrated");
    Serial.print("gyr_calib: ");
    Serial.print(gyr_calib[0], 6);
    Serial.print(", ");
    Serial.print(gyr_calib[1], 6);
    Serial.print(", ");
    Serial.println(gyr_calib[2], 6);
    Serial.print("acc_calib: ");
    Serial.print(acc_calib[0], 6);
    Serial.print(", ");
    Serial.print(acc_calib[1], 6);
    Serial.print(", ");
    Serial.println(acc_calib[2], 6);
}

bool IMUGetData_Uncalibrated()
{
    if (myICM.dataReady())
    {
        myICM.getAGMT();

        constexpr float Deg2Rad = 3.1416f / 180.0f;
        gyr[0] = myICM.gyrX() * Deg2Rad;  
        gyr[1] = myICM.gyrY() * Deg2Rad;
        gyr[2] = myICM.gyrZ() * Deg2Rad;

        constexpr float G = 9.80665f;
        acc[0] = (myICM.accX() / 1000.0f) * G; 
        acc[1] = (myICM.accY() / 1000.0f) * G;
        acc[2] = (myICM.accZ() / 1000.0f) * G;
        
        return true;
    }
    return false;
}

void IMUGetData()
{
    if (IMUGetData_Uncalibrated()) 
    {
        unsigned long current_time = micros();
        float dt = (current_time - last_imu_time) / 1000000.0f;
        if (last_imu_time == 0) dt = 0.02f; // Initialize first dt
        last_imu_time = current_time;

        // Apply bias calibration
        gyr[0] -= gyr_calib[0];
        gyr[1] -= gyr_calib[1];
        gyr[2] -= gyr_calib[2];

        // Apply Mahony filter for perfect stable Quaternions
        MahonyAHRSupdateIMU(gyr[0], gyr[1], gyr[2], acc[0], acc[1], acc[2], dt);

        quat[0] = Mahony_q1;
        quat[1] = Mahony_q2;
        quat[2] = Mahony_q3;
        quat[3] = Mahony_q0;
    }
}