import requests
import sys
import os

# 開発環境なのでsys.pathでlibsを読み込む設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libs.config import DISCORD_NEWS_URL, GRAFANA_ONE_DAY_URL

def send_daily_report():
    # config.py から設定値を読み込み
    snapshot_url = GRAFANA_ONE_DAY_URL
    webhook_url = DISCORD_NEWS_URL
    
    message = f"🌙 **【一日のまとめ】**\お疲れ様です。\n本日の測定グラフです\n{snapshot_url}"
    
    # Discordへ通知
    try:
        requests.post(webhook_url, json={"content": message})
        print("日次レポートを送信しました")
    except Exception as e:
        print(f"エラー発生: {e}")

if __name__ == "__main__":
    send_daily_report()
