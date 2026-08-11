#ifndef MYCLIFFSENSOR_H
#define MYCLIFFSENSOR_H

#include <Arduino.h>
#include <Wire.h>
#include <VL53L0X.h>

#define PCA9548A_ADDR 0x70
#define NUM_CLIFF_SENSORS 6
#define MUX_RESET_PIN 23 // Connect this GPIO to the RST pin on the multiplexer

class MyCliffSensor {
public:
    MyCliffSensor();
    void init();
    void update();
    uint16_t getDistance(uint8_t index);
    bool isTimeout(uint8_t index);

private:
    VL53L0X sensors[NUM_CLIFF_SENSORS];
    uint16_t distances[NUM_CLIFF_SENSORS];
    bool timeouts[NUM_CLIFF_SENSORS];

    void pcaselect(uint8_t i);
};

#endif
