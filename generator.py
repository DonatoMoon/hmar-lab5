import os
import requests
import time
import random
import sys

# Намагаємося завантажити змінні з .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_URL = os.environ.get("API_URL")
if not API_URL:
    print("Помилка: API_URL не знайдено! Створіть файл .env або пропишіть змінну середовища.")
    sys.exit(1)

def generate():
    while True:
        # З ймовірністю 80% генеруємо "Нормальну" ситуацію, з 20% — "Алерт"
        is_alert_scenario = random.random() < 0.5
        
        # Генеруємо відразу дві метрики (CPU та Пам'ять)
        if is_alert_scenario:
            cpu = random.randint(85, 99) if random.random() > 0.5 else random.randint(10, 75)
            mem = random.randint(95, 99) if random.random() > 0.5 else random.randint(10, 85)
            # Гарантуємо, що якщо це алерт, то хоча б одна метрика вища порогу
            if cpu <= 80 and mem <= 90:
                cpu = random.randint(85, 99)
        else:
            cpu = random.randint(10, 75)
            mem = random.randint(10, 85)
            
        payload = {
            "device_id": "server-1",
            "metrics": {
                "cpu_usage": cpu,
                "memory_usage": mem
            }
        }
            
        print(f"Sending CPU:{cpu}% MEM:{mem}%...", end=" ")
        
        try:
            response = requests.post(API_URL, json=payload, timeout=5)
            if response.status_code != 200:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                time.sleep(5)
                continue
                
            data = response.json()
            if data.get("is_alert"):
                print("⚠️  ALERT TRIGGERED!")
            else:
                print("✅ OK")
        except Exception as e:
            print(f"❌ Network Error: {e}")
            
        time.sleep(random.randint(5, 10))

if __name__ == "__main__":
    print(f"Starting generator. Pushing combined data to {API_URL}")
    print("Press Ctrl+C to stop.")
    generate()
