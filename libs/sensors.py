import time
from smbus2 import SMBus, i2c_msg
import bme280

class EnvironmentSensors:
    def __init__(self):
        self.scd41_addr = 0x62
        self.bme280_addr = 0x76
        self.bme_params = None
        
        # クラスが作られた最初の1回だけ、BME280の初期化（補正データ読み込み）をおこなう
        bus = None
        try:
            bus = SMBus(1)
            time.sleep(0.1)
            self.bme_params = bme280.load_calibration_params(bus, self.bme280_addr)
        except Exception:
            # 起動時に万が一失敗しても、後でリトライできるようにNoneにしておく
            self.bme_params = None
        finally:
            if bus is not None:
                bus.close()

    def read_all(self):
        """お互いに干渉せず、I2Cバスを安全に使い回す完全版"""
        temperature, humidity, bme_addr_str = None, None, "未検出"
        co2_val = None
        
        # === ステップ1: SCD41に計測コマンドを送信 ===
        bus = None
        try:
            bus = SMBus(1)
            bus.write_i2c_block_data(self.scd41_addr, 0x21, [0xb1])
        except Exception:
            pass
        finally:
            if bus is not None:
                bus.close()  # 計測中はバスを解放

        # === ステップ2: センサーの測定をじっくり待つ ===
        time.sleep(5.5)

        # === ステップ3: データの回収（BME280 -> SCD41） ===
        bus = None
        try:
            bus = SMBus(1)
            time.sleep(0.05)
            
            # ① BME280の読み込み（paramsは使い回すので一瞬で終わります）
            try:
                # 起動時に失敗していた場合はここで1回だけ初期化を試みる
                if self.bme_params is None:
                    self.bme_params = bme280.load_calibration_params(bus, self.bme280_addr)
                    time.sleep(0.05)
                
                if self.bme_params is not None:
                    bme_data = bme280.sample(bus, self.bme280_addr, self.bme_params)
                    temperature = bme_data.temperature
                    humidity = bme_data.humidity
                    bme_addr_str = hex(self.bme280_addr)
            except Exception:
                bme_addr_str = "エラー"
                
            time.sleep(0.05)
            
            # ② SCD41のデータ回収
            try:
                write = i2c_msg.write(self.scd41_addr, [0xec, 0x05])
                read = i2c_msg.read(self.scd41_addr, 9)
                bus.i2c_rdwr(write, read)
                
                data = list(read)
                if len(data) >= 2:
                    co2_val = (data[0] << 8) | data[1]
            except Exception:
                co2_val = None
                
        except Exception:
            pass
        finally:
            if bus is not None:
                bus.close()

        return {
            "temperature": temperature,
            "humidity": humidity,
            "co2": co2_val,
            "bme_addr": bme_addr_str
        }
