#include <Arduino.h> // Arduino library for basic functions

#include "MyIMU.h"        // Library for the IMU
#include "MySerial.h"     // Library for the controller
#include "MyTOF.h"        // Library for the TOF

//==============================================
// Arduino Setup
//==============================================
void setup()
{
  SerialBegin();
  IMUBegin();          // Initialize the IMU
  TOFBegin();          // Initialize the TOF
}

void loop()
{
  IMUGetData();                // Get the data from the IMU
  TOFGetData();                // Get the data from the TOF
  // IMUGetData_Uncalibrated();                // Get the data from the IMU
  SerialDataPrint();           // Print the data to the Serial Monitor
}
