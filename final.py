import time
import os
import board
import busio
import adafruit_dht
import subprocess
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Pin
from supabase import create_client, Client

SUPABASE_URL = "https://zbipgacibeawnexsgcxe.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpiaXBnYWNpYmVhd25leHNnY3hlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5OTgwMDMsImV4cCI6MjA4NzU3NDAwM30.VoVhfeb_FSw4PHn14yBGzbEqYR5eRptKYHdtZhHONN4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1.0)

ads = None
wind_chan = None

print("Connecting to sensors...")

while ads is None:
    try:
        ads = ADS.ADS1115(i2c)
        wind_chan = AnalogIn(ads, Pin.A0)
    except (ValueError, OSError):
        print("Waiting for ADS1115 to wake up...")
        time.sleep(1.0)

dht_device = adafruit_dht.DHT11(board.D4, use_pulseio=False)

# Wind Calibration Constants (Standard 0.4V - 2.0V Sensor)
WIND_MIN_V = 0.4
WIND_MAX_V = 2.0
WIND_MAX_MPH = 72.5

def voltage_to_mph(voltage):
    if voltage <= WIND_MIN_V:
        return 0.0
    elif voltage >= WIND_MAX_V:
        return WIND_MAX_MPH
    else:
        return (voltage - WIND_MIN_V) * WIND_MAX_MPH / (WIND_MAX_V - WIND_MIN_V)

def capture_and_upload():
    img_name = f"drone_cam_{int(time.time())}.jpg"
    
    subprocess.run(
        ["rpicam-still", "--camera", "1", "-t", "500", "-o", img_name, "--immediate"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    if os.path.exists(img_name):
        with open(img_name, 'rb') as f:
            supabase.storage.from_("drone-images").upload(img_name, f)
            
        img_url = supabase.storage.from_("drone-images").get_public_url(img_name)
        os.remove(img_name)
        return img_url
    else:
        print("-> Camera Warning: Failed to capture image. Skipping photo upload.")
        return "No Image"

print("--- Drone Sensor & Telemetry System Online ---")
print("Initializing transmission to Supabase...")

while True:
    try:
        temp_c = dht_device.temperature
        hum = dht_device.humidity
        wind_voltage = wind_chan.voltage
        
        if temp_c is not None and hum is not None:
            image_url = capture_and_upload()
            
            # Convert the raw voltage to MPH here
            wind_mph = voltage_to_mph(wind_voltage)
            
            data = {
                "temperature": float(temp_c),
                "humidity": float(hum),
                "wind_speed": float(wind_mph),
                "altitude": 0.0,
                "gps_coords": "0,0",
                "image_url": image_url
            }
            
            response = supabase.table("flight_data").insert(data).execute()
            print(f"Sync Success! Temp: {temp_c}C | Hum: {hum}% | Wind: {wind_mph:.1f} MPH (Raw: {wind_voltage:.2f}V)")
            
    except RuntimeError:
        time.sleep(1.0)
        continue
    except OSError as e:
        print(f"-> I2C Connection hiccup: {e}")
        time.sleep(1.0)
        continue
    except Exception as e:
        print(f"System Error: {e}")
        
    time.sleep(10)
