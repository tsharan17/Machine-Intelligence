#include <Arduino.h>

void setup() {
    pinMode(2, OUTPUT);
}

void loop() {
    for (int i = 0; i < 15; i++) {
        digitalWrite(2, HIGH);
        delay(500);
        digitalWrite(2, LOW);
        delay(500);
    }
    while(true);  // halt after 15 blinks
}