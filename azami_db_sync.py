import sys
import os
import csv
from libs.db_manager import DBManager
from libs.notifier import DiscordNotifier
from libs.config import DISCORD_DB_URL

# ライブラリ読み込みパス設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設定用パス
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_CSV = os.path.join(BASE_DIR, "data", "sensor_log.csv")

def main():
    # Discord通知用の初期化
    notifier = DiscordNotifier(DISCORD_DB_URL)

    # CSVファイルがなければ何もしない
    if not os.path.exists(LOG_CSV) or os.path.getsize(LOG_CSV) == 0:
        return

    db = DBManager()
    records = []

    # 1. CSVからデータを読み込む
    try:
        with open(LOG_CSV, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            # ヘッダー行を読み飛ばす
            next(reader, None)
            
            for row in reader:
                if len(row) >= 5: # timestamp, temp, hum, co2, pressure
                    records.append(row)
    except Exception as e:
        notifier.send(f"⚠️ **【DB同期エラー】**\nCSV読み込み失敗: {e}")
        return

    if not records:
        return

    # 2. SQLiteへ書き込み
    try:
        for rec in records:
            timestamp = rec[0]
            data = {
                "temp": float(rec[1]),
                "hum": float(rec[2]),
                "co2": int(rec[3]),
                "pressure": float(rec[4])
            }
            db.write(timestamp, data)
        
        # 成功通知
        notifier.send(f"✅ **【DB同期完了】**\nSQLiteへのデータ書き込みに成功しました。\n同期件数: {len(records)} 件")
        print(f"✅ {len(records)}件のデータをSQLiteに同期しました。")

        # 3. CSVを空にしてストレージを解放
        with open(LOG_CSV, 'w', encoding="utf-8") as f:
            pass
        print("🧹 CSVファイルをクリアしました。")

    except Exception as e:
        notifier.send(f"❌ **【DB同期失敗】**\nデータベース書き込み中にエラーが発生しました: {e}")
        print(f"❌ DB書き込みエラー: {e}")

if __name__ == "__main__":
    main()
