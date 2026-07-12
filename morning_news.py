import requests
import feedparser
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libs.config import DISCORD_NEWS_URL, MORNING_NEWS_FEEDS

def get_morning_news():
    message = "☀️ **【おはようございます。朝のニュースです】**\n\n"
    
    for category, url in MORNING_NEWS_FEEDS.items():
        feed = feedparser.parse(url)
    # 各ジャンルから最新3件だけ取得
        for entry in feed.entries[:3]:
            # リンクの出力をやめてタイトルだけに修正
            message += f"• [{entry.title}]({entry.link})\n"
        message += "\n"    

    # Discordへ通知
    requests.post(DISCORD_NEWS_URL, json={"content": message})

if __name__ == "__main__":
    get_morning_news()
