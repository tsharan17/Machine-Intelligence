#include <Arduino.h>

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(12); // Calculate delay for approximately 85 blinks per second
  digitalWrite(LED_BUILTIN, LOW);
  delay(12);
}