from components.base import BaseComponent


class MPU9250(BaseComponent):
    """
    MPU-9250 / MPU-6500 IMU
    Uses I2C communication (SDA, SCL)
    """

    name = "MPU9250"

    interfaces = [
        {"label": "SDA", "signal_type": "digital_input"},
        {"label": "SCL", "signal_type": "digital_output"},
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        sda = pin_assignments.get("SDA", 21)
        scl = pin_assignments.get("SCL", 22)

        return f"""
    Wire.begin({sda}, {scl});
    Serial.begin(115200);

    // Wake up MPU9250 (exit sleep mode)
    Wire.beginTransmission(0x68);
    Wire.write(0x6B);
    Wire.write(0);
    Wire.endTransmission();

    Serial.println("MPU9250 initialized");
"""

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        return """
    // Read Accelerometer (AX, AY, AZ)
    Wire.beginTransmission(0x68);
    Wire.write(0x3B); // starting register for accel
    Wire.endTransmission(false);
    Wire.requestFrom(0x68, 6, true);

    int16_t ax = Wire.read() << 8 | Wire.read();
    int16_t ay = Wire.read() << 8 | Wire.read();
    int16_t az = Wire.read() << 8 | Wire.read();

    Serial.print("AX: "); Serial.print(ax);
    Serial.print(" AY: "); Serial.print(ay);
    Serial.print(" AZ: "); Serial.println(az);

    delay(500);
"""