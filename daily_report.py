import sys
import os
import requests
from dotenv import load_dotenv

load_dotenv() # .envを読み込む

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meguriya_generate_graph import create_graph_buffer
from libs.config import DISCORD_NEWS_URL

def send_daily_report():
    webhook_url = DISCORD_NEWS_URL
    if not webhook_url:
        print("エラー: DISCORD_NEWS_URL が設定されていません")
        return

    buf = create_graph_buffer()
    
    # 画像送信
    files = {'file': ('graph.png', buf, 'image/png')}
    payload = {"content": "📊 本日の活動時間帯のまとめです。"}
    requests.post(webhook_url, data=payload, files=files)
    print("✅ レポート送信完了!")

if __name__ == "__main__":
    send_daily_report()
