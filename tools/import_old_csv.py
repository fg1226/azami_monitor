import csv
import sqlite3
import os

# パスの設定
CSV_PATH = 'data/sensor_log.csv'
DB_DIR = '/mnt/hdd/azami_monitor/data'
DB_PATH = os.path.join(DB_DIR, 'sensor_data.db')

# HDD側に保存用ディレクトリがなければ作成
os.makedirs(DB_DIR, exist_ok=True)

print(f"データベースを作成中: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. テーブルの作成（もしなければ）
# 君のCSVのヘッダーに合わせて、timestamp, temp, hum, co2, pressure の5列を作成
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

# 2. CSVファイルを読み込んでDBへ一括挿入
print(f"CSVファイル {CSV_PATH} を読み込んでいます...")
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    # 1行目がヘッダー（timestamp,temp,hum,co2,pressure）であることを前提にします
    reader = csv.reader(f)
    header = next(reader) 
    
    # データの挿入クエリ
    insert_query = '''
        INSERT INTO environment_log (timestamp, temp, hum, co2, pressure)
        VALUES (?, ?, ?, ?, ?)
    '''
    
    # 高速化のためにトランザクション内で一括処理
    inserted_count = 0
    for row in reader:
        # 行のデータ数が足りない場合の安全策（古いデータで気圧がない場合など）
        while len(row) < 5:
            row.append(None)
            
        cursor.execute(insert_query, (row[0], row[1], row[2], row[3], row[4]))
        inserted_count += 1

# コミットして保存
conn.commit()
conn.close()

print(f"✨ 移行完了！ {inserted_count} 件のデータをHDDのデータベースに格納したよ！")
