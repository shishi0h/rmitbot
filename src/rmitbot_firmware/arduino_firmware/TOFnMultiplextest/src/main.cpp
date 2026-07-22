#include <Arduino.h>
#include <Wire.h>
#include <VL53L1X.h>

#define PCA9548A_ADDR 0x70

VL53L1X sensor1;
VL53L1X sensor2;

void pcaselect(uint8_t i) {
  if (i > 7) return;
  Wire.beginTransmission(PCA9548A_ADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

void setup() {
  Serial.begin(115200);
  
  // Initialize I2C with SDA on 21 and SCL on 22
  Wire.begin(21, 22);
  Wire.setClock(400000); // 400 kHz I2C for faster ToF communication

  Serial.println("Starting VL53L1X Multiplexer Test");

  // Initialize Sensor 1 on channel 0
  pcaselect(0);
  sensor1.setTimeout(500);
  if (!sensor1.init()) {
    Serial.println("Failed to detect and initialize sensor 1 (Channel 0)!");
  } else {
    Serial.println("Sensor 1 initialized.");
    sensor1.setDistanceMode(VL53L1X::Long);
    sensor1.setMeasurementTimingBudget(50000);
    sensor1.startContinuous(50);
  }

  // Initialize Sensor 2 on channel 1
  pcaselect(1);
  sensor2.setTimeout(500);
  if (!sensor2.init()) {
    Serial.println("Failed to detect and initialize sensor 2 (Channel 1)!");
  } else {
    Serial.println("Sensor 2 initialized.");
    sensor2.setDistanceMode(VL53L1X::Long);
    sensor2.setMeasurementTimingBudget(50000);
    sensor2.startContinuous(50);
  }
}

void loop() {
  // Read Sensor 1
  pcaselect(0);
  uint16_t dist1 = sensor1.read();
  Serial.print("Sensor 1 (Ch 0): ");
  Serial.print(dist1);
  Serial.print(" mm");
  if (sensor1.timeoutOccurred()) {
    Serial.print(" TIMEOUT");
  }

  Serial.print("\t|\t");

  // Read Sensor 2
  pcaselect(1);
  uint16_t dist2 = sensor2.read();
  Serial.print("Sensor 2 (Ch 1): ");
  Serial.print(dist2);
  Serial.print(" mm");
  if (sensor2.timeoutOccurred()) {
    Serial.print(" TIMEOUT");
  }
  
  Serial.println();

  delay(100);
}
