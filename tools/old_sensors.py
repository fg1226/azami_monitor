import time
from smbus2 import SMBus, i2c_msg
import bme280

class EnvironmentSensors:
    def __init__(self):
        self.bus = SMBus(1)
        self.scd41_addr = 0x62
        
    def get_bme_params(self):
        """0x76 と 0x77 を自動スキャンしてcalibration_paramsを返す"""
        for addr in [0x76, 0x77]:
            try:
                params = bme280.load_calibration_params(self.bus, addr)
                return addr, params
            except Exception:
                continue
        return None, None

    def read_all(self):
        """両方のセンサーからデータを取得して辞書で返す"""
        # 1. BME280のスキャンと取得
        bme_addr, params = self.get_bme_params()
        if bme_addr is None:
            raise RuntimeError("BME280センサーが見つかりません。")
            
        bme_data = bme280.sample(self.bus, bme_addr, params)
        temperature = bme_data.temperature
        humidity = bme_data.humidity

        # 2. SCD41（CO2）の取得
        self.bus.write_i2c_block_data(self.scd41_addr, 0x21, [0xb1])
        time.sleep(5)
        
        write = i2c_msg.write(self.scd41_addr, [0xec, 0x05])
        read = i2c_msg.read(self.scd41_addr, 9)
        self.bus.i2c_rdwr(write, read)
        
        data = list(read)
        co2_val = (data[0] << 8) | data[1]

        return {
            "temperature": temperature,
            "humidity": humidity,
            "co2": co2_val,
            "bme_addr": hex(bme_addr)
        }
