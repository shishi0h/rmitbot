#include "MySerial.h"

MySerial::MySerial(MyCliffSensor& cliffSensor) : _cliffSensor(cliffSensor) {}

void MySerial::init() {
    Serial.begin(115200);
}

void MySerial::sendData() {
    // Format: [dist0\tdist1\tdist2\tdist3]
    Serial.print("[");
    bool first = true;
    for (int i = 0; i < NUM_CLIFF_SENSORS; i++) {
        if (i == 2) continue; // Skip sensor 2
        
        if (!first) {
            Serial.print("\t");
        }
        Serial.print(_cliffSensor.getDistance(i));
        first = false;
    }
    Serial.println("]");
}
