import os
import sys
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

# libsフォルダを読み込めるように設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libs.bme280_sensor import BME280Sensor
from libs.scd41_sensor import SCD41Sensor
from libs.alerter import AlertManager
from libs.config import DISCORD_ALERT_URL

# .env読み込み
load_dotenv()
TOKEN = os.getenv('DISCORD_AZAMI_BOT')

# ボット設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 1. パスの定義
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ALERT_MODE_FILE = os.path.join(DATA_DIR, "alert_mode.txt")

# 2. センサーとマネージャーの初期化
bme = BME280Sensor()
scd = SCD41Sensor()
alerter = AlertManager(os.path.join(DATA_DIR, "alert_state.json"), DISCORD_ALERT_URL)

@bot.command()
async def アラート停止(ctx):
    with open(ALERT_MODE_FILE, "w") as f:
        f.write("disabled")
    await ctx.send("🚨 はい！アラートを停止します！")

@bot.command()
async def アラート再開(ctx):
    with open(ALERT_MODE_FILE, "w") as f:
        f.write("enabled")
    await ctx.send("✅ わかりました！アラートを再開します！\n換気が必要になったらお知らせしますね。")

@bot.event
async def on_ready():
    print(f'ログイン成功！ {bot.user} として動くよ')

@bot.command()
async def 気温(ctx):
    bme_data = bme.read()
    scd_data = scd.read()
    
    temp = bme_data.get("temperature")
    hum = bme_data.get("humidity")
    co2 = scd_data.get("co2")
    
    await ctx.send(f"今の環境情報です！\n🌡️ 気温: {temp:.1f}℃\n💧 湿度: {hum:.1f}%\n💨 CO2: {co2} ppm")

bot.run(TOKEN)
