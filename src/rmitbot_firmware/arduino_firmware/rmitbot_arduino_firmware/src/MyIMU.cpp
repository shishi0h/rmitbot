#include "MyIMU.h"

extern double quat[4];
extern double gyr[3];
extern double acc[3];
extern double quat_calib[4];
extern double gyr_calib[3];
extern double acc_calib[3];

ICM_20948_I2C myICM;

void IMUBegin()
{
    Wire.begin(I2C_SDA, I2C_SCL);
    Wire.setClock(100000);
    Wire.setTimeOut(2000);
    bool initialized = false;
    while (!initialized)
    {
        myICM.begin(Wire, 0);
        if (myICM.status != ICM_20948_Stat_Ok)
        {
            initialized = false;
        }
        else
        {
            initialized = true;
        }
    }
    bool success = true;
    success &= (myICM.initializeDMP() == ICM_20948_Stat_Ok);
    success &= (myICM.enableDMPSensor(INV_ICM20948_SENSOR_GAME_ROTATION_VECTOR) == ICM_20948_Stat_Ok);
    success &= (myICM.enableDMPSensor(INV_ICM20948_SENSOR_RAW_GYROSCOPE) == ICM_20948_Stat_Ok);
    success &= (myICM.enableDMPSensor(INV_ICM20948_SENSOR_RAW_ACCELEROMETER) == ICM_20948_Stat_Ok);
    success &= (myICM.setDMPODRrate(DMP_ODR_Reg_Quat6, 0) == ICM_20948_Stat_Ok); // Set to the maximum
    success &= (myICM.setDMPODRrate(DMP_ODR_Reg_Accel, 0) == ICM_20948_Stat_Ok); // Set to the maximum
    success &= (myICM.setDMPODRrate(DMP_ODR_Reg_Gyro, 0) == ICM_20948_Stat_Ok);  // Set to the maximum
    success &= (myICM.enableFIFO() == ICM_20948_Stat_Ok);
    success &= (myICM.enableDMP() == ICM_20948_Stat_Ok);
    success &= (myICM.resetDMP() == ICM_20948_Stat_Ok);
    success &= (myICM.resetFIFO() == ICM_20948_Stat_Ok);

    IMUCalibrate();
}

void IMUCalibrate()
{    
    for (size_t i = 0; i < 100; i++)
    {
        IMUGetData_Uncalibrated();
        quat_calib[0] += quat[0];
        quat_calib[1] += quat[1];
        quat_calib[2] += quat[2];
        quat_calib[3] += quat[3];
        gyr_calib[0] += gyr[0];
        gyr_calib[1] += gyr[1];
        gyr_calib[2] += gyr[2];
        acc_calib[0] += acc[0];
        acc_calib[1] += acc[1];
        acc_calib[2] += acc[2];
    }
    quat_calib[0] /= 100.0;
    quat_calib[1] /= 100.0;
    quat_calib[2] /= 100.0;
    quat_calib[3] /= 100.0;
    gyr_calib[0] /= 100.0;
    gyr_calib[1] /= 100.0;
    gyr_calib[2] /= 100.0;
    acc_calib[0] /= 100.0;
    acc_calib[1] /= 100.0;
    acc_calib[2] /= 100.0;

    Serial.println("IMU Calibrated");
    Serial.print("quat_calib: ");
    Serial.print(quat_calib[0], 6);
    Serial.print(", ");
    Serial.print(quat_calib[1], 6);
    Serial.print(", ");
    Serial.print(quat_calib[2], 6);
    Serial.print(", ");
    Serial.println(quat_calib[3], 6);
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
    // while (1)
    // {
    //     /* code */
    // }
    
}

void IMUGetData_Uncalibrated()
{
    icm_20948_DMP_data_t data;
    
    // 1. Flush the DMP FIFO to get the absolute newest Quaternion packet!
    myICM.readDMPdataFromFIFO(&data);
    while (myICM.status == ICM_20948_Stat_FIFOMoreDataAvail) {
        myICM.readDMPdataFromFIFO(&data);
    }

    if (myICM.status == ICM_20948_Stat_Ok) 
    {
        // Quaternion (from GAME_ROTATION_VECTOR)
        if ((data.header & DMP_header_bitmap_Quat6) > 0)
        {
            double q1 = ((double)data.Quat6.Data.Q1) / 1073741824.0; // Convert to double. Divide by 2^30
            double q2 = ((double)data.Quat6.Data.Q2) / 1073741824.0; // Convert to double. Divide by 2^30
            double q3 = ((double)data.Quat6.Data.Q3) / 1073741824.0; // Convert to double. Divide by 2^30
            double val = 1.0 - ((q1 * q1) + (q2 * q2) + (q3 * q3));
            double q0 = (val > 0.0) ? sqrt(val) : 0.0;
            double n = sqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);

            quat[0] = q1 / n;
            quat[1] = q2 / n;
            quat[2] = q3 / n;
            quat[3] = q0 / n;
        }
    }

    // 2. Hardware Gyroscope and Accelerometer (bypassing the DMP suppression bug)
    if (myICM.dataReady())
    {
        myICM.getAGMT(); // Reads perfectly aligned, zero-latency hardware registers
        
        // Gyroscope (myICM.gyrX returns degrees/s)
        constexpr float Deg2Rad = 3.1416f / 180.0f;
        gyr[0] = myICM.gyrX() * Deg2Rad;  
        gyr[1] = myICM.gyrY() * Deg2Rad;
        gyr[2] = myICM.gyrZ() * Deg2Rad;

        // Accelerometer (myICM.accX returns milli-g's)
        constexpr float G = 9.80665f;
        acc[0] = (myICM.accX() / 1000.0f) * G; 
        acc[1] = (myICM.accY() / 1000.0f) * G;
        acc[2] = (myICM.accZ() / 1000.0f) * G;
    }
}

void IMUGetData()
{
    icm_20948_DMP_data_t data;
    
    // 1. Flush the DMP FIFO to get the absolute newest Quaternion packet!
    myICM.readDMPdataFromFIFO(&data);
    while (myICM.status == ICM_20948_Stat_FIFOMoreDataAvail) {
        myICM.readDMPdataFromFIFO(&data);
    }

    if (myICM.status == ICM_20948_Stat_Ok) 
    {
        // Quaternion (from GAME_ROTATION_VECTOR)
        if ((data.header & DMP_header_bitmap_Quat6) > 0)
        {
            double q1 = ((double)data.Quat6.Data.Q1) / 1073741824.0; // Convert to double. Divide by 2^30
            double q2 = ((double)data.Quat6.Data.Q2) / 1073741824.0; // Convert to double. Divide by 2^30
            double q3 = ((double)data.Quat6.Data.Q3) / 1073741824.0; // Convert to double. Divide by 2^30
            double val = 1.0 - ((q1 * q1) + (q2 * q2) + (q3 * q3));
            double q0 = (val > 0.0) ? sqrt(val) : 0.0;
            double n = sqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);

            quat[0] = q1 / n;
            quat[1] = q2 / n;
            quat[2] = q3 / n;
            quat[3] = q0 / n;
        }
    }

    // 2. Hardware Gyroscope and Accelerometer (bypassing the DMP suppression bug)
    if (myICM.dataReady())
    {
        myICM.getAGMT(); // Reads perfectly aligned, zero-latency hardware registers
        
        // Gyroscope (myICM.gyrX returns degrees/s)
        constexpr float Deg2Rad = 3.1416f / 180.0f;
        gyr[0] = (myICM.gyrX() * Deg2Rad) - gyr_calib[0];  
        gyr[1] = (myICM.gyrY() * Deg2Rad) - gyr_calib[1];
        gyr[2] = (myICM.gyrZ() * Deg2Rad) - gyr_calib[2];

        // Accelerometer (myICM.accX returns milli-g's)
        constexpr float G = 9.80665f;
        acc[0] = (myICM.accX() / 1000.0f) * G; 
        acc[1] = (myICM.accY() / 1000.0f) * G;
        acc[2] = (myICM.accZ() / 1000.0f) * G;
    }
}