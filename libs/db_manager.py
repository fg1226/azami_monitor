import sqlite3
import os

class DBManager:
    def __init__(self, db_file=None):
        # 💡 ここで自動判定！
        # もし引数でパスが指定されなかったら、現在のファイルの場所から自動でパスを計算する
        if db_file is None:
            # このファイルの親の親（つまり azami-monitor または azami-monitor-dev フォルダ）を取得
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # フォルダ名が「dev」で終わる場合は開発用DB、そうじゃない場合は本番のHDDを向く
            if base_dir.endswith("-dev"):
                self.db_file = os.path.join(base_dir, "data", "sensor_data.db")
            else:
                self.db_file = "/mnt/hdd/azami_monitor/data/sensor_data.db"
        else:
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

    def write_many(self, records):
        """まとめて書き込んで最後にコミットする"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        for timestamp, data in records:
            cursor.execute('''
                INSERT INTO environment_log (timestamp, temp, hum, co2, pressure)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, data["temp"], data["hum"], data["co2"], data.get("pressure")))
        conn.commit()
        conn.close()
    def fetch_all_data(self):
        """全データをリストとして取得する"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT timestamp, temp, hum, co2, pressure FROM environment_log')
        data = cursor.fetchall()
        conn.close()
        return data
