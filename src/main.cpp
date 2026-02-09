#include <HardwareSerial.h>

#include <Arduino.h>
#include <Wire.h>

#define MPU6050_ADDRESS 0x68

void setup() {
  Wire.begin();
}

void loop() {
  Wire.beginTransmission(MPU6050_ADDRESS);
  Wire.write(0x3B);
  Wire.endTransmission(false);

  Wire.requestFrom(MPU6050_ADDRESS, 14, true);

  uint8_t data[14];
  for (int i = 0; i < 14; i++) {
    data[i] = Wire.read();
  }

  int16_t accX = (data[0] << 8) | data[1];
  int16_t accY = (data[2] << 8) | data[3];
  int16_t accZ = (data[4] << 8) | data[5];

  int16_t gyroX = (data[8] << 8) | data[9];
  int16_t gyroY = (data[10] << 8) | data[11];
  int16_t gyroZ = (data[12] << 8) | data[13];

  Serial.print("Acc X: ");
  Serial.print(accX);
  Serial.print(", Acc Y: ");
  Serial.print(accY);
  Serial.print(", Acc Z: ");
  Serial.println(accZ);

  Serial.print("Gyro X: ");
  Serial.print(gyroX);
  Serial.print(", Gyro Y: ");
  Serial.print(gyroY);
  Serial.print(", Gyro Z: ");
  Serial.println(gyroZ);
}