import sys
import os
import time

# 1つ上の親ディレクトリ（azami-monitor）をPythonの検索パスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 新しく作った最強の共通センサーライブラリをインポート
from libs.sensors import EnvironmentSensors

def main():
    sensors = EnvironmentSensors()
    print("⏳ センサーの現在値を測定中（5秒ほどかかります）...")
    
    try:
        data = sensors.read_all()
        
        temp = data["temperature"]
        humid = data["humidity"]
        co2 = data["co2"]
        addr = data["bme_addr"]
        
        print("\n==============================")
        print(f"🌡️  温  度: {f'{temp:.1f} °C' if temp is not None else '取得失敗'}")
        print(f"💧  湿  度: {f'{humid:.1f} %' if humid is not None else '取得失敗'}")
        print(f"🍃  CO2  : {f'{co2} ppm' if co2 is not None else '取得失敗'}")
        print(f"📡  BME280: {addr}")
        print("==============================")
        
    except Exception as e:
        print(f"❌ 予期せぬエラー: {e}")

if __name__ == "__main__":
    main()
