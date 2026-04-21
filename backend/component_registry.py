from components.led import LED
from components.buzzer import Buzzer
from components.ultrasonic import Ultrasonic
from components.serial_output import SerialOutput
from components.servo import Servo
from components.ir_sensor import IRSensor
from components.dht_sensor import DHTSensor
from components.ldr import LDR
from components.relay import Relay
from components.rgb_led import RGBLED
from components.button import Button
from components.potentiometer import Potentiometer
from components.pir_sensor import PIRSensor
from components.soil_moisture import SoilMoisture
from components.sound_sensor import SoundSensor
from components.mpu9250 import MPU9250

# ─────────────────────────────────────────────────────────────
# Keys must be UPPERCASE — matched against normalized LLM output
# Add aliases for common spoken variations of component names
# ─────────────────────────────────────────────────────────────

registry = {

    # ── Original components ───────────────────────────────────
    "LED":                  LED(),
    "BUZZER":               Buzzer(),
    "ULTRASONIC":           Ultrasonic(),
    "ULTRASONIC SENSOR":    Ultrasonic(),
    "SERIAL":               SerialOutput(),
    "SERVO":                Servo(),
    "SERVO MOTOR":          Servo(),

    # ── New components ────────────────────────────────────────
    "IR":                   IRSensor(),
    "IR SENSOR":            IRSensor(),
    "INFRARED":             IRSensor(),
    "INFRARED SENSOR":      IRSensor(),

    "DHT":                  DHTSensor(),
    "DHT11":                DHTSensor(),
    "DHT22":                DHTSensor(),
    "TEMPERATURE SENSOR":   DHTSensor(),
    "HUMIDITY SENSOR":      DHTSensor(),
    "TEMP SENSOR":          DHTSensor(),

    "LDR":                  LDR(),
    "LIGHT SENSOR":         LDR(),
    "PHOTORESISTOR":        LDR(),

    "RELAY":                Relay(),
    "RELAY MODULE":         Relay(),

    "RGB":                  RGBLED(),
    "RGB LED":              RGBLED(),
    "COLOR LED":            RGBLED(),

    "BUTTON":               Button(),
    "PUSH BUTTON":          Button(),
    "SWITCH":               Button(),
    "TACTILE BUTTON":       Button(),

    "POTENTIOMETER":        Potentiometer(),
    "POT":                  Potentiometer(),
    "KNOB":                 Potentiometer(),
    "VARIABLE RESISTOR":    Potentiometer(),

    "PIR":                  PIRSensor(),
    "PIR SENSOR":           PIRSensor(),
    "MOTION SENSOR":        PIRSensor(),
    "MOTION DETECTOR":      PIRSensor(),

    "SOIL":                 SoilMoisture(),
    "SOIL SENSOR":          SoilMoisture(),
    "SOIL MOISTURE":        SoilMoisture(),
    "MOISTURE SENSOR":      SoilMoisture(),

    "SOUND":                SoundSensor(),
    "SOUND SENSOR":         SoundSensor(),
    "MICROPHONE":           SoundSensor(),
    "MIC":                  SoundSensor(),
    "NOISE SENSOR":         SoundSensor(),

    "MPU9250":              MPU9250(),
    "MPU6500":              MPU9250(),
}


def get_component(name: str):
    """Look up a component by name (case-insensitive). Returns instance or None."""
    return registry.get(name.upper().strip())


def list_components() -> list:
    """Return all registered component names."""
    return list(registry.keys())