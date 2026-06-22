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
    delay(1000); 
    Serial.println("\n--- Starting MIXED DMP + Hardware Test ---");
    
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
    
    // We must enable RAW Gyro and Accel so the DMP's internal fusion engine has data to work with!
    // However, we will STILL read the actual Gyro/Accel data from the hardware registers to avoid the header bug!
    bool success = true;
    success &= (myICM.initializeDMP() == ICM_20948_Stat_Ok);
    success &= (myICM.enableDMPSensor(INV_ICM20948_SENSOR_GAME_ROTATION_VECTOR) == ICM_20948_Stat_Ok);
    success &= (myICM.enableDMPSensor(INV_ICM20948_SENSOR_RAW_GYROSCOPE) == ICM_20948_Stat_Ok);
    success &= (myICM.enableDMPSensor(INV_ICM20948_SENSOR_RAW_ACCELEROMETER) == ICM_20948_Stat_Ok);
    
    // Set ODR so it doesn't overflow
    success &= (myICM.setDMPODRrate(DMP_ODR_Reg_Quat6, 0) == ICM_20948_Stat_Ok); 
    success &= (myICM.setDMPODRrate(DMP_ODR_Reg_Gyro, 0) == ICM_20948_Stat_Ok); 
    success &= (myICM.setDMPODRrate(DMP_ODR_Reg_Accel, 0) == ICM_20948_Stat_Ok); 
    
    success &= (myICM.enableFIFO() == ICM_20948_Stat_Ok);
    success &= (myICM.enableDMP() == ICM_20948_Stat_Ok);
    success &= (myICM.resetDMP() == ICM_20948_Stat_Ok);
    success &= (myICM.resetFIFO() == ICM_20948_Stat_Ok);

    if (success) {
        Serial.println("DMP Successfully Initialized for Quaternions ONLY!");
    }
}

void loop()
{
    icm_20948_DMP_data_t data;
    
    // 1. FLUSH the DMP FIFO to get the absolute newest Quaternion packet
    myICM.readDMPdataFromFIFO(&data);
    while (myICM.status == ICM_20948_Stat_FIFOMoreDataAvail) {
        myICM.readDMPdataFromFIFO(&data);
    }

    if (myICM.status == ICM_20948_Stat_Ok) 
    {
        if ((data.header & DMP_header_bitmap_Quat6) > 0) {
            double q1 = ((double)data.Quat6.Data.Q1) / 1073741824.0; 
            Serial.print("DMP Quat Q1: "); Serial.print(q1, 4);
        }
    }
    
    // 2. Read Gyro and Accel directly from the flawless hardware registers!
    if (myICM.dataReady()) {
        myICM.getAGMT();
        
        Serial.print(" | Hardware Gyro Z (deg/s): "); 
        Serial.print(myICM.gyrZ(), 2);
        Serial.print(" | Hardware Accel Z (mg): "); 
        Serial.print(myICM.accZ(), 2);
    }
    
    Serial.println();
    delay(50); 
}
