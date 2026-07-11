import time
from smbus2 import SMBus
import bme280

class BME280Sensor:
    def __init__(self):
        # アドレスを決め打ちせず、76と77の両方を探す仕組みにします
        self.addr = None 

    def read(self):
        try:
            with SMBus(1) as bus:
                # 76か77、反応する方を自動で選ぶ
                for addr in [0x76, 0x77]:
                    try:
                        params = bme280.load_calibration_params(bus, addr)
                        self.addr = addr # 見つけた方を保存
                        break
                    except:
                        continue
                
                if self.addr is None:
                    raise Exception("BME280が見つかりません")
                # そのままサンプリング
                data = bme280.sample(bus, self.addr, params)
                
                return {
                    "temperature": round(data.temperature, 1),
                    "humidity": round(data.humidity, 1),
                    "pressure": round(data.pressure, 1)
                }
        except Exception as e:
            print(f"[BME280] 読み込みエラー: {e}")
            return {"temperature": None, "humidity": None}
