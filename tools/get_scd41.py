import time
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libs.scd41_sensor import SCD41Sensor

def main():
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scd41_data.json")
    try:
        scd = SCD41Sensor()
        scd_data = scd.read()
        
        result = {"co2": scd_data.get("co2")}
        with open(data_path, "w") as f:
            json.dump(result, f)
        print(f"✓ CO2取得成功: {result}")
    except Exception as e:
        with open(data_path, "w") as f:
            json.dump({"co2": None}, f)
        print(f"✗ CO2取得失敗: {e}")

if __name__ == "__main__":
    main()
