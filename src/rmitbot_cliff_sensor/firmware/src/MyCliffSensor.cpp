#include "MyCliffSensor.h"

MyCliffSensor::MyCliffSensor() {
    for (int i = 0; i < NUM_CLIFF_SENSORS; i++) {
        distances[i] = 0;
        timeouts[i] = false;
    }
}

void MyCliffSensor::pcaselect(uint8_t i) {
    if (i > 7) return;
    Wire.beginTransmission(PCA9548A_ADDR);
    Wire.write(1 << i);
    Wire.endTransmission();  
}

void MyCliffSensor::init() {
    // Perform a hardware reset of the multiplexer
    pinMode(MUX_RESET_PIN, OUTPUT);
    digitalWrite(MUX_RESET_PIN, LOW); // Pull LOW to reset
    delay(10);                        // Hold for 10ms
    digitalWrite(MUX_RESET_PIN, HIGH); // Pull HIGH to wake up
    delay(50);                        // Wait for multiplexer and sensors to boot up

    Wire.begin(21, 22);
    Wire.setClock(400000); // 400 kHz

    for (int i = 0; i < NUM_CLIFF_SENSORS; i++) {
        pcaselect(i);
        sensors[i].setTimeout(500);
        if (!sensors[i].init()) {
            Serial.print("Failed to init sensor on channel ");
            Serial.println(i);
        } else {
            sensors[i].setDistanceMode(VL53L1X::Long);
            sensors[i].setMeasurementTimingBudget(50000);
            sensors[i].startContinuous(50);
        }
    }
}

void MyCliffSensor::update() {
    for (int i = 0; i < NUM_CLIFF_SENSORS; i++) {
        pcaselect(i);
        distances[i] = sensors[i].read();
        timeouts[i] = sensors[i].timeoutOccurred();
    }
}

uint16_t MyCliffSensor::getDistance(uint8_t index) {
    if (index >= NUM_CLIFF_SENSORS) return 0;
    return distances[index];
}

bool MyCliffSensor::isTimeout(uint8_t index) {
    if (index >= NUM_CLIFF_SENSORS) return true;
    return timeouts[index];
}
