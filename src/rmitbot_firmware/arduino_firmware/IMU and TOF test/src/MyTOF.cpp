#include "MyTOF.h"

VL53L1X tofSensor;
uint16_t tof_distance = 0;

void TOFBegin()
{
    tofSensor.setTimeout(500);
    if (!tofSensor.init())
    {
        Serial.println("Failed to detect and initialize VL53L1X sensor!");
    }
    else
    {
        tofSensor.setDistanceMode(VL53L1X::Short);
        tofSensor.setMeasurementTimingBudget(50000);
        tofSensor.startContinuous(50);
    }
}

void TOFGetData()
{
    if (tofSensor.dataReady())
    {
        tof_distance = tofSensor.read(false);
    }
}
