#include "MySerial.h"

extern double quat[4];          // Quaternion data from the IMU
extern double gyr[3];           // Gyroscope data from the IMU
extern double acc[3];           // Accelerometer data from the IMU
unsigned long Serial_time = 0;  // Time for serial communication
extern uint16_t tof_distance;   // TOF distance

void SerialBegin() // Function to initialize the serial communication
{
    Serial.begin(115200);
    while (!Serial)
        ;
}

void SerialDataPrint() // Function to print the data to the Serial Monitor
{
    if (micros() - Serial_time >= 50 * 1e3) // Print at 20 Hz
    {
        Serial_time = micros();
        
        Serial.print("TOF: ");
        Serial.print(tof_distance);
        
        Serial.print("\t| Q(W,X,Y,Z): ");
        Serial.print(quat[3], 2); Serial.print(",");
        Serial.print(quat[0], 2); Serial.print(",");
        Serial.print(quat[1], 2); Serial.print(",");
        Serial.print(quat[2], 2);
        
        Serial.print("\t| Gyr: ");
        Serial.print(gyr[0], 2); Serial.print(",");
        Serial.print(gyr[1], 2); Serial.print(",");
        Serial.print(gyr[2], 2);
        
        Serial.print("\t| Acc: ");
        Serial.print(acc[0], 2); Serial.print(",");
        Serial.print(acc[1], 2); Serial.print(",");
        Serial.println(acc[2], 2);
    }
}
