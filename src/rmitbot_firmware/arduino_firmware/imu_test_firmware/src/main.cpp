#include <Arduino.h>
#include <Wire.h>
#include "ICM_20948.h"

// Your custom I2C pins
#define I2C_SDA 23
#define I2C_SCL 22

ICM_20948_I2C myICM;

// Add success flag globally
bool dmp_success = false;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("IMU Standalone Tester Starting...");

  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(100000);
  Wire.setTimeOut(2000);

  bool initialized = false;
  while (!initialized) {
    myICM.begin(Wire, 0); // I2C address 0x68 (0)
    if (myICM.status != ICM_20948_Stat_Ok) {
      Serial.println("IMU initialization failed. Retrying...");
      delay(500);
    } else {
      initialized = true;
    }
  }
  Serial.println("IMU Initialized! Booting DMP...");

  // Initialize DMP exactly as original firmware did
  bool success = true;
  ICM_20948_Status_e stat;

  stat = myICM.initializeDMP();
  Serial.print("initializeDMP: "); Serial.println(stat);
  success &= (stat == ICM_20948_Stat_Ok);

  stat = myICM.enableDMPSensor(INV_ICM20948_SENSOR_GAME_ROTATION_VECTOR);
  Serial.print("enableDMPSensor(Quat): "); Serial.println(stat);
  success &= (stat == ICM_20948_Stat_Ok);

  stat = myICM.enableDMPSensor(INV_ICM20948_SENSOR_RAW_GYROSCOPE);
  Serial.print("enableDMPSensor(Gyro): "); Serial.println(stat);
  success &= (stat == ICM_20948_Stat_Ok);

  stat = myICM.enableDMPSensor(INV_ICM20948_SENSOR_RAW_ACCELEROMETER);
  Serial.print("enableDMPSensor(Accel): "); Serial.println(stat);
  success &= (stat == ICM_20948_Stat_Ok);

  stat = myICM.setDMPODRrate(DMP_ODR_Reg_Quat6, 0);
  success &= (stat == ICM_20948_Stat_Ok);

  stat = myICM.setDMPODRrate(DMP_ODR_Reg_Accel, 0);
  success &= (stat == ICM_20948_Stat_Ok);

  stat = myICM.setDMPODRrate(DMP_ODR_Reg_Gyro, 0);
  success &= (stat == ICM_20948_Stat_Ok);

  stat = myICM.enableFIFO();
  success &= (stat == ICM_20948_Stat_Ok);

  stat = myICM.enableDMP();
  success &= (stat == ICM_20948_Stat_Ok);

  stat = myICM.resetDMP();
  success &= (stat == ICM_20948_Stat_Ok);

  stat = myICM.resetFIFO();
  success &= (stat == ICM_20948_Stat_Ok);

  if (success) {
    dmp_success = true;
    Serial.println("DMP Ready! Starting raw data stream...");
  } else {
    dmp_success = false;
    Serial.println("DMP Failed! (Will sit idle in loop)");
  }
}

void loop() {
  if (dmp_success) {
    icm_20948_DMP_data_t data;
    myICM.readDMPdataFromFIFO(&data);

    if ((myICM.status == ICM_20948_Stat_Ok) || (myICM.status == ICM_20948_Stat_FIFOMoreDataAvail)) {
      if ((data.header & DMP_header_bitmap_Gyro) > 0) {
        // Print raw integer data exactly as the DMP outputs it
        int raw_z = data.Raw_Gyro.Data.Z;
        Serial.print("Raw Gyro Z: ");
        Serial.print(raw_z);

        // Print calculated values for both 16.4 and 65.5 scales to compare
        constexpr float Deg2Rad = 3.1416f / 180.0f;
        float z_float = (float)raw_z;

        float rads_16 = (z_float / 16.4f) * Deg2Rad;
        float rads_65 = (z_float / 65.5f) * Deg2Rad;

        Serial.print("\t| If 16.4 scale: ");
        Serial.print(rads_16, 4);
        Serial.print(" rad/s");

        Serial.print("\t| If 65.5 scale: ");
        Serial.print(rads_65, 4);
        Serial.println(" rad/s");
      }
    }
  }
  delay(10); // Wait for the DMP to generate new data
}
