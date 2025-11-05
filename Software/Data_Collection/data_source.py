import time, random, json
import paho.mqtt.publish  as publish

devices = {
    "fridge": (140, 160),
    "washer": (0, 2000),
    "ac": (0, 1500),
    "lights": (0, 100)
}



while True:
    for device, (low, high) in devices.items():
        if device == "washer":
            power = random.choice([0, random.uniform(low, high)])  # sometimes off
        elif device == "ac":
            power = random.choice([0, random.uniform(800, high)])  # on/off cycle
        else:
            power = random.uniform(low, high)
        
        payload = json.dumps({
            "timestamp": int(time.time()),
            "device": device,
            "power_w": round(power, 2)
        })
        publish.single(f"home/{device}/power", payload, hostname="localhost")
    time.sleep(5)

#Always run: mosquitto_sub -h localhost -t "home/#"