#include <Arduino.h>
#include <Wire.h>
#include <VL53L0X.h>

#define MUX_ADDRESS 0x70 // Default PCA9548A I2C address
#define MUX_RESET_PIN 23

VL53L0X sensor;

void tcaselect(uint8_t i) {
  if (i > 7) return;
  Wire.beginTransmission(MUX_ADDRESS);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }
  
  Serial.println("\n--- I2C MUX Debugger Started! ---");
  
  // 1. Hardware reset of the multiplexer
  Serial.println("Resetting MUX via GPIO 23...");
  pinMode(MUX_RESET_PIN, OUTPUT);
  digitalWrite(MUX_RESET_PIN, LOW);
  delay(10);
  digitalWrite(MUX_RESET_PIN, HIGH);
  delay(50);
  
  // 2. Start I2C (matching your main firmware: SDA=21, SCL=22)
  Wire.begin(21, 22);
  
  // 3. Ping the MUX itself
  Serial.println("---------------------------------");
  Serial.println("Pinging PCA9548A MUX at 0x70...");
  Wire.beginTransmission(MUX_ADDRESS);
  byte error = Wire.endTransmission();
  
  if (error == 0) {
    Serial.println("SUCCESS: MUX found at 0x70!");
  } else {
    Serial.print("FAILED: MUX NOT found. Error code: ");
    Serial.println(error);
    Serial.println("Check power, ground, and I2C wiring to the MUX.");
    // Wait here if no MUX is found
    while(1) { delay(1000); }
  }
  Serial.println("---------------------------------");

  // 4. Scan Channels 3 and 5 on the MUX and attempt to read VL53L0X
  for (uint8_t t=3; t<=5; t++) {
    if (t == 4) continue; // Skip channel 4
    tcaselect(t);
    Serial.print("TCA Port #"); Serial.println(t);

    bool sensorFound = false;
    for (uint8_t addr = 0; addr<=127; addr++) {
      if (addr == MUX_ADDRESS) continue; // Skip the MUX itself

      Wire.beginTransmission(addr);
      if (!Wire.endTransmission()) {
        Serial.print("  Found I2C 0x");
        if (addr < 16) Serial.print("0");
        Serial.println(addr, HEX);
        if (addr == 0x29) {
          sensorFound = true;
        }
      }
    }

    // Try to initialize and read from the VL53L0X regardless of I2C scan result
    sensor.setTimeout(500);
    if (!sensor.init()) {
      Serial.println("  [SENSOR] Failed to initialize VL53L0X on this port.");
    } else {
      uint16_t distance = sensor.readRangeSingleMillimeters();
      if (sensor.timeoutOccurred()) {
        Serial.println("  [SENSOR] Read TIMEOUT!");
      } else {
        Serial.print("  [SENSOR] Distance: ");
        Serial.print(distance);
        Serial.println(" mm");
      }
    }
  }
  
  Serial.println("---------------------------------");
  Serial.println("Scan complete.");
}

void loop() {
  // Do nothing
  delay(1000);
}
