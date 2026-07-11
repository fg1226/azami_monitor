import time
from smbus2 import SMBus, i2c_msg

class SCD41Sensor:
    def __init__(self):
        self.addr = 0x62

    def read(self):
        """SCD41にその場で1回だけ計測させ、安全にデータを回収する"""
        try:
            with SMBus(1) as bus:
                # 1. 念のため、現在動いているかもしれない自動計測を完全にストップさせる
                bus.write_i2c_block_data(self.addr, 0x3f, [0x86])
                time.sleep(0.5)
                
                # 2. 「今すぐ1回だけ計測してね」というコマンド（Measure Single Shot）を送信
                # コマンド: 0x219d
                bus.write_i2c_block_data(self.addr, 0x21, [0x9d])
                
                # 3. SCD41が内部でヒーターを温めて計測が終わるまで「5秒間」じっと待つ（超重要）
                print("[SCD41] 単発計測中... (5秒間お待ちください)")
                time.sleep(5.0)
                
                # 4. データの読み出し要求 (0xec05)
                bus.write_i2c_block_data(self.addr, 0xec, [0x05])
                time.sleep(0.1)
                
                # 5. 9バイト分（CO2、温度、湿度）のデータを一括回収
                read_msg = i2c_msg.read(self.addr, 9)
                bus.i2c_rdwr(read_msg)
                data = list(read_msg)
                
                # 6. CO2濃度の計算
                co2 = (data[0] << 8) | data[1]
                
                # 0ppmや異常に高い値はエラーとする
                if co2 == 0 or co2 > 5000:
                    return {"co2": None}
                    
                return {"co2": co2}
                
        except Exception as e:
            print(f"[SCD41] 読み込みエラー: {e}")
            return {"co2": None}
