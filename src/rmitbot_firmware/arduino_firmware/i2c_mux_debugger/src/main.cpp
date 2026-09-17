#include <Arduino.h>
#include <Wire.h>
#include <VL53L0X.h>

VL53L0X sensor;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }
  
  Serial.println("\n--- Direct Cliff Sensor Test ---");
  
  // You requested SCL on 21, SDA on 22
  // Wire.begin(SDA, SCL)
  Wire.begin(22, 21);
  
  // 1. Scan for the sensor at 0x29
  Serial.println("Scanning I2C bus for VL53L0X at 0x29...");
  Wire.beginTransmission(0x29);
  byte error = Wire.endTransmission();
  
  if (error == 0) {
    Serial.println("SUCCESS: Found device at 0x29!");
  } else {
    Serial.print("FAILED: Device not found at 0x29. Error code: ");
    Serial.println(error);
    Serial.println("Check SDA, SCL, VCC, and GND wiring.");
    while(1) { delay(1000); }
  }

  // 2. Try to initialize the VL53L0X driver
  Serial.println("Initializing VL53L0X sensor...");
  sensor.setTimeout(500);
  if (!sensor.init()) {
    Serial.println("ERROR: Failed to detect and initialize sensor!");
    while (1) { delay(1000); }
  }

  // Set up continuous measurement for testing
  sensor.setMeasurementTimingBudget(50000);
  sensor.startContinuous(50);
  Serial.println("Sensor initialized! Starting continuous read...\n");
}

void loop() {
  uint16_t distance = sensor.readRangeContinuousMillimeters();
  
  if (sensor.timeoutOccurred()) {
    Serial.println("[ERROR] Read TIMEOUT! Sensor hung.");
  } else {
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" mm");
  }
  
  delay(100);
}
