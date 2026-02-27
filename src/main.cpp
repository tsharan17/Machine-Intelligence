#include <Arduino.h>

void setup() {
    pinMode(2, OUTPUT);
    pinMode(4, INPUT);
    Serial.begin(115200);
    pinMode(5, OUTPUT);
}

void loop() {
    // Ultrasonic HC-SR04 measurement
    digitalWrite(2, LOW);
    delayMicroseconds(2);
    digitalWrite(2, HIGH);
    delayMicroseconds(10);
    digitalWrite(2, LOW);
    long duration = pulseIn(4, HIGH);
    float distance_cm = duration * 0.034 / 2.0;
    Serial.print("Distance: ");
    Serial.print(distance_cm);
    Serial.println(" cm");
    if (distance_cm < 15) {
        Serial.println("OBJECT DETECTED!");
    }
    delay(200);
    digitalWrite(5, HIGH);
    delay(0);
    digitalWrite(5, LOW);
    delay(0);
}