#include <Arduino.h>

void setup() { pinMode({{ULTRASONIC_TRIG_PIN}}, OUTPUT); pinMode({{ULTRASONIC_ECHO_PIN}}, INPUT); pinMode(4, OUTPUT); }

void loop() {
  digitalWrite({{ULTRASONIC_TRIG_PIN}}, LOW);
  delayMicroseconds(2);
  digitalWrite({{ULTRASONIC_TRIG_PIN}}, HIGH);
  delayMicroseconds(10);
  digitalWrite({{ULTRASONIC_TRIG_PIN}}, LOW);
  long duration = pulseIn({{ULTRASONIC_ECHO_PIN}}, HIGH);
  float distance = duration * 0.034 / 2;

  if (distance < 15) {
    digitalWrite(4, HIGH);
  } else {
    digitalWrite(4, LOW);
  }
}