import sys
import os
import time

# libsフォルダを読み込めるように設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 必要なモジュールをインポート
from libs.bme280_sensor import BME280Sensor
from libs.scd41_sensor import SCD41Sensor
from libs.notifier import DiscordNotifier
from libs.logger import DataLogger
from libs.db_manager import DBManager
from libs.alerter import AlertManager
from libs.config import DISCORD_LOG_URL, DISCORD_ALERT_URL

# 設定用パス
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data") 
STATE_FILE = os.path.join(DATA_DIR, "alert_state.json")
LOG_CSV = os.path.join(DATA_DIR, "sensor_log.csv")
LAST_NOTIFY_FILE = os.path.join(DATA_DIR, "last_notify.txt")


# オブジェクトの初期化
logger = DataLogger(LOG_CSV)
db = DBManager()
alerter = AlertManager(STATE_FILE, DISCORD_ALERT_URL)
log_notifier = DiscordNotifier(DISCORD_LOG_URL)

def get_sensor_data():
    """センサーからデータを取得する"""
    bme = BME280Sensor()
    scd = SCD41Sensor()
    bme_data = bme.read()
    scd_data = scd.read()
    return {
        "temp": bme_data.get("temperature"),
        "hum": bme_data.get("humidity"),
        "co2": scd_data.get("co2"),
        "pressure": bme_data.get("pressure")  
    }
def should_notify():
    """10分経過しているか確認"""
    if not os.path.exists(LAST_NOTIFY_FILE):
        return True
    with open(LAST_NOTIFY_FILE, "r") as f:
        return (time.time() - float(f.read())) > 600

def send_periodic_log(data):
    """定期通知の実行と時刻記録"""
    msg = (f"📊 **【あざみモニター 定点観測】**\n"
           f"🌡️ **気温**: {data['temp']:.1f} ℃\n"
           f"💧 **湿度**: {data['hum']:.1f} %\n"
           f"💨 **CO2濃度**: {data['co2']} ppm\n"
           f"🎈 **気圧**: {data['pressure']} hPa")
    log_notifier.send(msg)
    with open(LAST_NOTIFY_FILE, "w") as f:
        f.write(str(time.time()))
def main():
    # 1. 取得
    data = get_sensor_data()
    if None in data.values():
        print(f"⚠️ センサー取得エラー: {data}")
        return
    # 2. 共通タイムスタンプ取得
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    # 3. 記録（DataLoggerとDBMnagerを使用）
    logger.save(data, data)
    db.write(now, data)

    # 4. 定期通知
    if should_notify():
        send_periodic_log(data)

    # 5. アラート判定（AlertManagerを使用）
    alerter.check(data)

if __name__ == "__main__":
    main()
