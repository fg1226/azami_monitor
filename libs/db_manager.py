import sqlite3
import os

class DBManager:
    def __init__(self, db_file="/mnt/hdd/azami_monitor/data/sensor_data.db"):
        self.db_file = db_file
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """テーブルがなければ作成する"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS environment_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temp REAL,
                hum REAL,
                co2 INTEGER,
                pressure REAL
            )
        ''')
        conn.commit()
        conn.close()

    def write(self, timestamp, data):
        """データをDBに挿入する"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO environment_log (timestamp, temp, hum, co2, pressure)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, data["temp"], data["hum"], data["co2"], data.get("pressure")))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"【警告】DBへの書き込みに失敗しました: {e}")
