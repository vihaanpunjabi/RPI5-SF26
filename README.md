#  Raspberry Pi 5 Drone Telemetry & Weather System

A robust, Python-based flight telemetry system designed for a Raspberry Pi 5 drone. This script continuously reads environmental data (temperature, humidity, wind speed) and captures aerial photographs, pushing everything in real-time to a Supabase PostgreSQL database. 

It is specifically designed to be "bulletproof" in the air, featuring automatic recovery from loose I2C wires, camera failures, and sensor timing timeouts without crashing the main flight loop.

##  Features
* **Real-Time Telemetry Logging:** Captures ambient temperature and humidity.
* **Analog Wind Speed Conversion:** Reads an analog anemometer via an I2C ADC and converts raw voltage to Miles Per Hour (MPH).
* **Automated Aerial Photography:** Uses `libcamera` to snap photos from a Pi 5 MIPI port and uploads them directly to cloud storage.
* **Fault-Tolerant Loop:** Safely ignores temporary hardware dropouts (e.g., vibration-induced I2C disconnects) and missing camera modules, ensuring sensor data always makes it to the cloud.

##  Hardware Requirements
* **Compute:** Raspberry Pi 5
* **Camera:** Arducam Hawkeye (or standard Pi Camera) connected to **Port 1** via a Type B FFC cable.
* **Sensors:**
  * **DHT11:** Temperature and Humidity sensor.
  * **ADS1115 (I2C):** 16-bit Analog-to-Digital Converter.
  * **Analog Anemometer:** Wind speed sensor (0.4V - 2.0V scale).
* **Power/Connectivity:** Cellular HAT (e.g., Sixfab) or Wi-Fi for cloud syncing.

##  Wiring Guide
**DHT11 Sensor:**
* `VCC` ➔ Pi Pin 1 (3.3V)
* `GND` ➔ Pi Pin 9 (Ground)
* `DATA` ➔ Pi Pin 7 (GPIO 4)

**ADS1115 (Analog to Digital Converter):**
* `VDD` ➔ Pi Pin 1 (3.3V)
* `GND` ➔ Pi Pin 9 (Ground)
* `SCL` ➔ Pi Pin 5 (GPIO 3)
* `SDA` ➔ Pi Pin 3 (GPIO 2)
* `A0` ➔ Signal wire from the Analog Anemometer

## Software Setup

### 1. Install Dependencies
You will need the Adafruit CircuitPython libraries and the Supabase Python client. Run this in your virtual environment:
```bash
pip install adafruit-circuitpython-dht adafruit-circuitpython-ads1x15 supabase
