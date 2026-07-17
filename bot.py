import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv

# libsフォルダを読み込めるように設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libs.bme280_sensor import BME280Sensor
from libs.scd41_sensor import SCD41Sensor
from libs.alerter import AlertManager  # アラート管理も後で使うためにインポート
from libs.config import DISCORD_ALERT_URL

# .env読み込み
load_dotenv()
TOKEN = os.getenv('DISCORD_AZAMI_BOT')

# ボット設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# センサー初期化（起動時に1回だけ実行）
bme = BME280Sensor()
scd = SCD41Sensor()

# アラートのON/OFF状態を保持する変数
alert_enabled = True

@bot.command()
async def アラート停止(ctx):
    global alert_enabled
    alert_enabled = False
    await ctx.send("🚨 はい！アラートを停止します！")

@bot.command()
async def アラート再開(ctx):
    global alert_enabled
    alert_enabled = True
    await ctx.send("✅ わかりました！アラートを停止します！")

# 定期的にセンサーをチェックするループ処理（これが必要！）
from discord.ext import tasks

@tasks.loop(seconds=60) # 1分おきにチェック
async def monitor_sensors():
    if not alert_enabled:
        return # アラート停止中なら何もしない
        
    # センサー取得
    bme_data = bme.read()
    scd_data = scd.read()
    data = {
        "temp": bme_data.get("temperature"),
        "hum": bme_data.get("humidity"),
        "co2": scd_data.get("co2"),
        "pressure": bme_data.get("pressure")
    }
    
    # 既存の alerter を使ってチェック
    # 注意: ここで alerter を使えるように、ボット起動時にインスタンスを作っておこう
    alerter.check(data)

@bot.event
async def on_ready():
    print(f'ログイン成功！ {bot.user} として動くよ')

@bot.command()
async def 気温(ctx):
    # センサーから読み取り
    bme_data = bme.read()
    scd_data = scd.read()
    
    temp = bme_data.get("temperature")
    hum = bme_data.get("humidity")
    co2 = scd_data.get("co2")
    
    # 返信
    await ctx.send(f"今の環境情報だよ！\n🌡️ 気温: {temp:.1f}℃\n💧 湿度: {hum:.1f}%\n💨 CO2: {co2} ppm")

bot.run(TOKEN)
