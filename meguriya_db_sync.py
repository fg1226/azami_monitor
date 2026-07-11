import sys
import os
import csv
from datetime import datetime
from libs.db_manager import DBManager
from libs.notifier import DiscordNotifier
from libs.config import DISCORD_DB_URL

# InfluxDB用ライブラリ
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# ライブラリ読み込みパス設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設定用パス
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_CSV = os.path.join(BASE_DIR, "data", "sensor_log.csv")

# --- InfluxDBの設定 ---
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "VbWL5CeFhUV_zzeAav13muak0n7FaV-ftcr-TSBHM5G8KJ2wigB6q1j1SSt37nkvkKjNB_hT2iMHQLDOAUGTlg=="
INFLUX_ORG = "home"
INFLUX_BUCKET = "sensors"

def main():
    notifier = DiscordNotifier(DISCORD_DB_URL)

    # InfluxDBクライアント初期化
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    if not os.path.exists(LOG_CSV) or os.path.getsize(LOG_CSV) == 0:
        return

    db = DBManager()
    records_to_save = []
    influx_points = []

    # 1. CSVからデータを読み込む
    try:
        with open(LOG_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None) # ヘッダー読み飛ばし
            
            for row in reader:
                if len(row) >= 5:
                    timestamp = row[0]
                    data = {
                        "temp": float(row[1]),
                        "hum": float(row[2]),
                        "co2": int(row[3]),
                        "pressure": float(row[4])
                    }
                    records_to_save.append((timestamp, data))

                    # InfluxDB用データポイント作成
                    point = Point("environment") \
                        .time(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%SZ")) \
                        .field("temp", data["temp"]) \
                        .field("hum", data["hum"]) \
                        .field("co2", data["co2"]) \
                        .field("pressure", data["pressure"])
                    influx_points.append(point)

    except Exception as e:
        notifier.send(f"⚠️ **【DB同期エラー】**\nCSV読み込み失敗: {e}")
        return

    if not records_to_save:
        return

    # 2. SQLite と InfluxDB へ書き込み
    try:
        # SQLiteへの保存
        db.write_many(records_to_save)
        
        # InfluxDBへの保存
        if influx_points:
            write_api.write(bucket=INFLUX_BUCKET, record=influx_points)
        
        notifier.send(f"✅ **【DB同期完了】**\n同期件数: {len(records_to_save)} 件")
        print(f"✅ {len(records_to_save)}件のデータをSQLiteとInfluxDBに同期しました。")

        # 3. CSVを空にする
        with open(LOG_CSV, 'w', encoding="utf-8") as f:
            pass
        print("🧹 CSVファイルをクリアしました。")

    except Exception as e:
        notifier.send(f"❌ **【DB同期失敗】**\n書き込み中にエラーが発生しました: {e}")
        print(f"❌ 書き込みエラー: {e}")

if __name__ == "__main__":
    main()
