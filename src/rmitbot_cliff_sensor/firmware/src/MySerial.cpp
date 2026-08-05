#include "MySerial.h"

MySerial::MySerial(MyCliffSensor& cliffSensor) : _cliffSensor(cliffSensor) {}

void MySerial::init() {
    Serial.begin(115200);
}

void MySerial::sendData() {
    // Format: [dist0\tdist1\tdist2\tdist3]
    Serial.print("[");
    for (int i = 0; i < NUM_CLIFF_SENSORS; i++) {
        Serial.print(_cliffSensor.getDistance(i));
        if (i < NUM_CLIFF_SENSORS - 1) {
            Serial.print("\t");
        }
    }
    Serial.println("]");
}
