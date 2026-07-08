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
        tofSensor.setDistanceMode(VL53L1X::Long);
        tofSensor.setMeasurementTimingBudget(50000);
        tofSensor.startContinuous(50);
    }
}

void TOFGetData()
{
    tofSensor.read();
    // read() blocks until data is ready if we don't check dataReady(), or read(false) doesn't block.
    // However, if we do startContinuous(50), we can just check if data is ready.
    if (tofSensor.dataReady())
    {
        tof_distance = tofSensor.read(false);
    }
}
