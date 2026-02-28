#include <Arduino.h>

void setup() {
    pinMode(2, OUTPUT);
}

void loop() {
    for (int i = 0; i < 100; i++) {
        digitalWrite(2, HIGH);
        delay(200);
        digitalWrite(2, LOW);
        delay(200);
    }
    while(true);  // halt after 100 blinks
}