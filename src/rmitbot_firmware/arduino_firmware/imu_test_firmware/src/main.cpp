#include <Arduino.h>
#include <Wire.h>
#include "ICM_20948.h"

// I2C pins from your original firmware's MySetup.h
#define I2C_SDA 23
#define I2C_SCL 22

ICM_20948_I2C myICM;

void setup()
{
    Serial.begin(115200);
    delay(1000); // Wait for monitor
    Serial.println("\n--- Starting DMP Hardware Test ---");
    
    Wire.begin(I2C_SDA, I2C_SCL);
    Wire.setClock(100000);
    Wire.setTimeOut(2000);
    bool initialized = false;
    while (!initialized)
    {
        myICM.begin(Wire, 0);
        if (myICM.status != ICM_20948_Stat_Ok) {
            Serial.println("Trying to connect to IMU...");
            delay(500);
        } else {
            initialized = true;
        }
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

    if (success) {
        Serial.println("DMP Successfully Initialized!");
    } else {
        Serial.println("DMP Initialization FAILED!");
    }
}

void loop()
{
    icm_20948_DMP_data_t data;
    myICM.readDMPdataFromFIFO(&data);

    if ((myICM.status == ICM_20948_Stat_Ok) || (myICM.status == ICM_20948_Stat_FIFOMoreDataAvail)) // Was valid data available?
    {
        // BLIND EXTRACTION: We completely ignore the broken data.header bitmasks!
        // If the struct is correctly populated, these will contain real values.
        
        // --- GYRO (RAW) ---
        float gz = (float)data.Raw_Gyro.Data.Z;

        // --- ACCEL (RAW) ---
        float az = (float)data.Raw_Accel.Data.Z;

        // --- QUATERNIONS (from GAME_ROTATION_VECTOR) ---
        double q1 = ((double)data.Quat6.Data.Q1) / 1073741824.0; 

        Serial.print("DMP Packet | Gyro Z (raw): ");
        Serial.print(gz, 0);
        Serial.print(" | Accel Z (raw): ");
        Serial.print(az, 0);
        Serial.print(" | Quat Q1: ");
        Serial.println(q1, 4);

        delay(50); // Slow down the prints so you can read them
    }
}
