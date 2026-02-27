from components.base import BaseComponent


class DHTSensor(BaseComponent):
    """
    DHT11 / DHT22 Temperature and Humidity Sensor

    Interfaces:
        DATA (digital_input) — single-wire data line

    Wiring:
        VCC  → 3.3V (DHT22) or 5V (DHT11)
        GND  → GND
        DATA → GPIO with 10kΩ pull-up resistor to VCC

    Library required:
        Add to platformio.ini under lib_deps:
            adafruit/DHT sensor library @ ^1.4.4
            adafruit/Adafruit Unified Sensor @ ^1.1.9
    """

    name = "DHT"
    interfaces = [
        {"label": "DATA", "signal_type": "digital_input"}
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        pin      = pin_assignments["DATA"]
        dht_type = action.get("dht_type", "DHT11")  # DHT11 or DHT22
        lines = [
            f"    // DHT Sensor Setup",
            f"    // dht.begin() is called in constructor — see global declaration",
            f"    Serial.begin(115200);",
            f"    Serial.println(\"DHT Sensor Ready on GPIO {pin}\");",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        pin      = pin_assignments["DATA"]
        interval = action.get("interval_ms", 2000)

        lines = [
            f"    // NOTE: Declare globally above setup():",
            f"    // #include <DHT.h>",
            f"    // DHT dht({pin}, DHT11);  // or DHT22",
            f"    float humidity    = dht.readHumidity();",
            f"    float temperature = dht.readTemperature();",
            f"    if (isnan(humidity) || isnan(temperature)) {{",
            f"        Serial.println(\"DHT: Failed to read!\");",
            f"    }} else {{",
            f"        Serial.print(\"Temp: \");",
            f"        Serial.print(temperature);",
            f"        Serial.print(\" C  |  Humidity: \");",
            f"        Serial.print(humidity);",
            f"        Serial.println(\" %\");",
            f"    }}",
            f"    delay({interval});",
        ]
        return "\n".join(lines) + "\n"
