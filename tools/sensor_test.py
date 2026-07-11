import time
from smbus2 import SMBus
import bme280
import urllib.request
import json

bus = SMBus(1)

# ─── 【設定】ここにコピーしたDiscordのWebhook URLを貼り付けてください ───
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1523305875908067378/41a4kjpxFgW4ynS53M3EIfeEohwNlEQ7KbJqGVAou2pgI0z0UfB12EvTn6T9IeRBEQyV"

# CO2の警告しきい値（テスト用に低めにするなら1000、運用なら1500など）
CO2_THRESHOLD = 1000  
# 連続で通知がいかないようにするためのタイマー（秒）
NOTIFICATION_INTERVAL = 300  # 5分間は再通知しない
last_notified_time = 0

# Discordにメッセージを送る関数（外部ライブラリ不要）
def send_discord_message(msg):
    payload = {"content": msg}
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    req = urllib.request.Request(DISCORD_WEBHOOK_URL, data=json.dumps(payload).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            pass
    except Exception as e:
        print("Discord送信エラー:", e)

# BME280の初期化
bme_addr = 0x76
calibration_params = bme280.load_calibration_params(bus, bme_addr)

# SCD41（CO2）の計測開始
try:
    bus.write_i2c_block_data(0x62, 0x21, [0xb1])
    print("システム起動。Discord通知機能付きで計測を開始します...")
    time.sleep(5)
except:
    pass

try:
    while True:
        # データの取得
        bme_data = bme280.sample(bus, bme_addr, calibration_params)
        
        try:
            bus.write_i2c_block_data(0x62, 0xec, [0x05])
            time.sleep(0.01)
            scd_raw = bus.read_i2c_block_data(0x62, 0, 9)
            co2 = (scd_raw[0] << 8) | scd_raw[1]
        except:
            co2 = None

        if co2 is not None:
            # 画面表示
            print(f"【BME280】 気温: {bme_data.temperature:.1f} °C  |  湿度: {bme_data.humidity:.1f} %")
            print(f"【SCD41 】 CO2濃度: {co2} ppm")
            print("-" * 50)

            # 🚨 CO2濃度がしきい値を超えたらDiscordへ通知
            current_time = time.time()
            if co2 > CO2_THRESHOLD and (current_time - last_notified_time) > NOTIFICATION_INTERVAL:
                alert_msg = (
                    f"⚠️ **【あざみー警告】部屋の空気がよどんでいます！**\n"
                    f"CO2濃度が **{co2} ppm** に達しました（基準: {CO2_THRESHOLD} ppm）。\n"
                    f"現在の室温: {bme_data.temperature:.1f}℃ / 湿度: {bme_data.humidity:.1f}%\n"
                    f"窓を開けて換気してください！"
                )
                print("🚨 しきい値超過！Discordに通知を送ります...")
                send_discord_message(alert_msg)
                last_notified_time = current_time

        time.sleep(5)

except KeyboardInterrupt:
    print("\n終了します。")
