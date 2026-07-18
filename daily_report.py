import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meguriya_generate_graph import create_graph_buffer
from libs.config import DISCORD_NEWS_URL

def send_daily_report():
    webhook_url = DISCORD_NEWS_URL
    
    # 1. グラフをメモリ上に生成
    buf = create_graph_buffer()
    
    # 2. メッセージを先に送る
    message = "🌙 **【一日のまとめ】**\nお疲れ様です。本日の測定グラフです。"
    requests.post(webhook_url, json={"content": message})
    
    # 3. 画像だけを別々に送る
    files = {'file': ('graph.png', buf, 'image/png')}
    requests.post(webhook_url, files=files)
    
    print("日次レポート（メッセージ＋画像）を送信しました")

if __name__ == "__main__":
    send_daily_report()
