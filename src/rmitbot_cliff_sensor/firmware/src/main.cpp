#include <Arduino.h>
#include "MyCliffSensor.h"
#include "MySerial.h"

MyCliffSensor cliffSensor;
MySerial mySerial(cliffSensor);

unsigned long lastTime = 0;
const unsigned long interval = 50; // 20 Hz (50 ms)

void setup() {
    mySerial.init();
    cliffSensor.init();
}

void loop() {
    if (millis() - lastTime >= interval) {
        lastTime = millis();
        cliffSensor.update();
        mySerial.sendData();
    }
}
