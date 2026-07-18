import matplotlib.pyplot as plt
import io
import pandas as pd
from influxdb_client import InfluxDBClient

# InfluxDB設定
URL = "http://localhost:8086"
TOKEN = "VbWL5CeFhUV_zzeAav13muak0n7FaV-ftcr-TSBHM5G8KJ2wigB6q1j1SSt37nkvkKjNB_hT2iMHQLDOAUGTlg=="
ORG = "home"
BUCKET = "sensors"

def create_graph_buffer():
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    query_api = client.query_api()

    # 過去24時間のデータを取得するクエリ
    query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -24h)
      |> filter(fn: (r) => r["_measurement"] == "environment_v2")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df = query_api.query_data_frame(query)

    # グラフ描画
    plt.figure(figsize=(10, 5))
    plt.plot(df['_time'], df['co2'], label='CO2 (ppm)')
    plt.title("24h CO2 Trend")
    plt.legend()
    
    # バッファ（メモリ）に画像を保存
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf

# ==========================================
# ここから下が「実際にスクリプトを動かす」部分
# ==========================================
if __name__ == "__main__":
    print("データ取得と画像生成を開始します...")
    
    # 関数を呼び出してバッファを受け取る
    buf = create_graph_buffer()
    
    # バッファのデータをファイルとして書き出す
    with open("test_graph.png", "wb") as f:
        f.write(buf.getbuffer())
    
    print("✅ 画像生成完了！ test_graph.png を確認してください。")
