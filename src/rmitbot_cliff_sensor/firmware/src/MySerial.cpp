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
        if (i != 3 && i != 5) continue; // Only use sensors 3 and 5
        
        if (!first) {
            Serial.print("\t");
        }
        Serial.print(_cliffSensor.getDistance(i));
        first = false;
    }
    Serial.println("]");
}
