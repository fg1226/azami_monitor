import time
from dotenv import load_dotenv

# 💡 共通ライブラリをインポート
from libs.sensors import EnvironmentSensors

# .envファイルから環境変数を読み込む
load_dotenv(dotenv_path="/home/fg1226/azami-monitor/.env")

# インスタンス化
try:
    sensors = EnvironmentSensors()
except Exception as e:
    print(f"❌ センサーの初期化に失敗しました。ライブラリやI2Cの設定を確認してください。: {e}")
    exit(1)

print("🔍 センサー疎通テストを開始します。30秒間、5秒おきにデータを表示するよ！")
print("Ctrl+C でいつでも途中で止められます。\n")

try:
    for i in range(6):
        print(f"--- テスト計測 {i+1}回目 ---")
        
        # センサーからデータを一発取得
        data = sensors.read_all()
        temp = data["temperature"]
        humidity = data["humidity"]
        co2 = data["co2"]
        
        # データの表示
        if temp is None and humidity is None and co2 is None:
            print("⚠️ 警告: 全てのデータが None です。配線が抜けているか、アドレスが違います。")
        else:
            print(f"🌡️ 気温 : {f'{temp:.1f} ℃' if temp is not None else '取得失敗 (None)'}")
            print(f"💧 湿度 : {f'{humidity:.1f} %' if humidity is not None else '取得失敗 (None)'}")
            print(f"💨 CO2  : {f'{co2} ppm' if co2 is not None else '取得失敗 (None)'}")
        
        print("-" * 25)
        time.sleep(10)

    print("\n🟢 テスト終了！データが正しく表示されていれば、配線は100点満点だよ！")

except KeyboardInterrupt:
    print("\nテストを中断したよ。")
