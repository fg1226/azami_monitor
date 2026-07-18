import os
import io
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient

load_dotenv()
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")

def create_graph_buffer():
    client = InfluxDBClient(url="http://localhost:8086", token=INFLUX_TOKEN, org="home")
    query_api = client.query_api()

    query = 'from(bucket: "sensors") |> range(start: -24h) |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
    df = query_api.query_data_frame(query)

    df['_time'] = pd.to_datetime(df['_time']).dt.tz_convert('Asia/Tokyo')
    df = df[(df['_time'].dt.hour >= 4) & (df['_time'].dt.hour < 22)]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    fig.subplots_adjust(right=0.75) 
    
    # 1. 左軸: CO2 (緑)
    ax1.plot(df['_time'], df['co2'], color='green', label='CO2 (ppm)')
    ax1.set_ylabel('CO2 (ppm)', color='green')
    ax1.tick_params(axis='y', colors='green')
    ax1.set_ylim(200, 1800)
    ax1.axhline(1100, color='red', linestyle='--', alpha=0.5)
    ax1.axhline(700, color='green', linestyle='--', alpha=0.5)

    # 2. 右軸1: 温度 (オレンジ)
    ax2 = ax1.twinx()
    ax2.plot(df['_time'], df['temp'], color='orange', label='Temp (°C)')
    ax2.set_ylabel('Temp (°C)', color='orange')
    ax2.tick_params(axis='y', colors='orange')
    ax2.set_ylim(24.5, 28.5)

    # 3. 右軸2: 湿度 (青)
    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("axes", 1.2)) # 外側にずらす
    ax3.plot(df['_time'], df['hum'], color='blue', label='Humidity (%)')
    ax3.set_ylabel('Humidity (%)', color='blue')
    ax3.tick_params(axis='y', colors='blue')
    ax3.spines["right"].set_color("blue")
    ax3.set_ylim(40, 90)

    # 凡例統合
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper left')

    plt.title("Daily Activity Report")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf
