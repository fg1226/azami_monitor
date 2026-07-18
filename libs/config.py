import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_LOG_URL = os.getenv("DISCORD_LOG_URL")
DISCORD_ALERT_URL = os.getenv("DISCORD_ALERT_URL")
DISCORD_DB_URL = os.getenv("DISCORD_DB_URL")
DISCORD_NEWS_URL = os.getenv("DISCORD_NEWS_URL")
GRAFANA_ONE_DAY_URL = os.getenv("GRAFANA_ONE_DAY_URL")

MORNING_NEWS_FEEDS = {
    "天気": "https://rss-weather.yahoo.co.jp/rss/days/4410.xml",
    "社会": "https://news.yahoo.co.jp/rss/topics/domestic.xml"
}
