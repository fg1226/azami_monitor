import time
import json
import os
from smbus2 import SMBus
import bme280

def main():
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bme280_data.json")
    try:
        with SMBus(1) as bus:
            time.sleep(0.1)
            params = bme280.load_calibration_params(bus, 0x76)
            time.sleep(0.1)
            data = bme280.sample(bus, 0x76, params)
            
            result = {
                "temperature": round(data.temperature, 1),
                "humidity": round(data.humidity, 1)
            }
            with open(data_path, "w") as f:
                json.dump(result, f)
            print(f"✓ 温湿度取得成功: {result}")
    except Exception as e:
        # 失敗時は古いデータを残さないようにNoneで上書き
        with open(data_path, "w") as f:
            json.dump({"temperature": None, "humidity": None}, f)
        print(f"✗ 温湿度取得失敗: {e}")

if __name__ == "__main__":
    main()
