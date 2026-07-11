import os
import time
from datetime import datetime

from libs.sensors import EnvironmentSensors
from libs.notifier import DiscordNotifier

LOG_FILE = "/home/fg1226/azami-monitor/data/sensor_log.csv"
INTERVAL = 60  # 10分間隔

sensors = EnvironmentSensors()
notifier = DiscordNotifier(env_key="DISCORD_NOTICE_URL")

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("datetime,temperature,humidity,co2\n")

print(f"🚀 ロガー（耐ノイズ・10分間隔版）を起動しました。")
notifier.send("🤖 **環境モニターシステム（耐ノイズ運用）が起動しました**")

while True:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        data = sensors.read_all()
        
        temp = data["temperature"]
        humid = data["humidity"]
        co2 = data["co2"]
        addr = data["bme_addr"]
        
        # 表示用のテキスト整形（Noneの場合はハイフンにする）
        t_str = f"{temp:.1f} °C" if temp is not None else "取得失敗 ⚠️"
        h_str = f"{humid:.1f} %" if humid is not None else "取得失敗 ⚠️"
        c_str = f"{co2} ppm" if co2 is not None else "取得失敗 ⚠️"
        
        # 1. CSVログへの保存（取れなかった値は空文字にする）
        t_csv = f"{temp:.1f}" if temp is not None else ""
        h_csv = f"{humid:.1f}" if humid is not None else ""
        c_csv = f"{co2}" if co2 is not None else ""
        
        with open(LOG_FILE, "a") as f:
            f.write(f"{now_str},{t_csv},{h_csv},{c_csv}\n")
        print(f"[{now_str}] 💾 CSV記録処理完了 (BME: {addr})")

        # 2. Discordへの定期レポート送信
        discord_msg = (
            f"📊 **【定期環境レポート】** ({now_str})\n"
            f"🌡️ **温度:** {t_str}\n"
            f"💧 **湿度:** {h_str}\n"
            f"🍃 **CO2:** {c_str}\n"
            f"📡 _(BME280状況: {addr})_"
        )
        notifier.send(discord_msg)

    except Exception as e:
        # 想定外の大元のエラーが起きても絶対に落とさない
        print(f"[{now_str}] ❌ 予期せぬエラー: {e}")
        notifier.send(f"⚠️ **致命的なシステムエラー:** {e}")
        
    time.sleep(max(0, INTERVAL - 5))
