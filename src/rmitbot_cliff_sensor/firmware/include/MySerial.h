#ifndef MYSERIAL_H
#define MYSERIAL_H

#include <Arduino.h>
#include "MyCliffSensor.h"

class MySerial {
public:
    MySerial(MyCliffSensor& cliffSensor);
    void init();
    void sendData();

private:
    MyCliffSensor& _cliffSensor;
};

#endif
