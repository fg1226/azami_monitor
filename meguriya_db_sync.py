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
    notifier = DiscordNotifier(DISCORD_DB_URL)

    if not os.path.exists(LOG_CSV) or os.path.getsize(LOG_CSV) == 0:
        return

    db = DBManager()
    records_to_save = []

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
    except Exception as e:
        notifier.send(f"⚠️ **【DB同期エラー】**\nCSV読み込み失敗: {e}")
        return

    if not records_to_save:
        return

    # 2. SQLiteへまとめて書き込み
    try:
        db.write_many(records_to_save)
        
        notifier.send(f"✅ **【DB同期完了】**\n同期件数: {len(records_to_save)} 件")
        print(f"✅ {len(records_to_save)}件のデータをSQLiteに同期しました。")

        # 3. CSVを空にする
        with open(LOG_CSV, 'w', encoding="utf-8") as f:
            pass
        print("🧹 CSVファイルをクリアしました。")

    except Exception as e:
        notifier.send(f"❌ **【DB同期失敗】**\nデータベース書き込み中にエラーが発生しました: {e}")
        print(f"❌ DB書き込みエラー: {e}")

if __name__ == "__main__":
    main()
