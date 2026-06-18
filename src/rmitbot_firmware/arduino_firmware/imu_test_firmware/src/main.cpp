#include <Arduino.h>
#include <Wire.h>
#include "ICM_20948.h"

// I2C pins from your original firmware's MySetup.h
#define I2C_SDA 23
#define I2C_SCL 22

ICM_20948_I2C myICM;

// Global IMU variables just like original firmware
double quat[4];
double gyr[3];
double acc[3];
double quat_calib[4] = {0};
double gyr_calib[3] = {0};
double acc_calib[3] = {0};

void IMUGetData_Uncalibrated()
{
    icm_20948_DMP_data_t data;
    myICM.readDMPdataFromFIFO(&data);

    // DUMP EVERYTHING!
    Serial.print("Status: ");
    Serial.print(myICM.status);
    Serial.print(" | Header: ");
    Serial.println(data.header);

    if ((myICM.status == ICM_20948_Stat_Ok) || (myICM.status == ICM_20948_Stat_FIFOMoreDataAvail)) // Was valid data available?
    {
        // Blindly extract and print gyro data without checking the header
        float z = (float)data.Raw_Gyro.Data.Z;
        constexpr float Deg2Rad = 3.1416f / 180.0f;
        constexpr float LSB_PER_DPS = 16.4f;
        gyr[2] = z / LSB_PER_DPS * Deg2Rad;
        
        Serial.print("Raw Gyro Z: ");
        Serial.print(z);
        Serial.print("  -> Calculated rad/s: ");
        Serial.println(gyr[2], 6);
    }
}

void IMUCalibrate()
{
    Serial.println("IMUCalibrate() started...");
    for (size_t i = 0; i < 100; i++)
    {
        IMUGetData_Uncalibrated();
        // I added a 10ms delay here so it doesn't capture the exact same sample 100 times instantly
        delay(10); 
    }
    Serial.println("IMUCalibrate() finished!");
}

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
            initialized = false;
        else
            initialized = true;
    }
    
    // Exactly as written in your original MyIMU.cpp
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

void setup()
{
    Serial.begin(115200);
    delay(1000); // Wait for monitor
    Serial.println("\n--- Starting test based on Original Firmware ---");
    
    IMUBegin();
}

void loop()
{
    IMUGetData_Uncalibrated();
    delay(10);
}
