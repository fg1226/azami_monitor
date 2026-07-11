import time
from smbus2 import SMBus
import bme280

print("🌡️ BME280（温湿度）正統派単体テストを開始します...")
addr = 0x76

# === 最初に1回だけ、バスを開いて補正データを読み込む ===
bus = SMBus(1)
time.sleep(0.1)
try:
    params = bme280.load_calibration_params(bus, addr)
    print("✓ センサーの初期化に成功しました！")
except Exception as e:
    print(f"✗ 初期化でエラーが発生: {e}")
finally:
    bus.close()

time.sleep(0.5)

# === あとはデータ（数値）だけをループで引き抜く ===
for i in range(1, 6):
    bus = None
    try:
        bus = SMBus(1)
        time.sleep(0.05)
        
        # 補正データ(params)は使い回すので、ここではサンプリングするだけ！
        data = bme280.sample(bus, addr, params)
        print(f"[{i}回目] 気温: {data.temperature:.1f} ℃ / 湿度: {data.humidity:.1f} %")
    except Exception as e:
        print(f"[{i}回目] 取得失敗: {e}")
    finally:
        if bus is not None:
            bus.close()
    time.sleep(2)
