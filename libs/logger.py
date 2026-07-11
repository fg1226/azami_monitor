import csv
import os

class DataLogger:
    def __init__(self, log_file):
        self.log_file = log_file

    def save(self, timestamp, data):
        """データをCSVに保存する"""
        file_exists = os.path.exists(self.log_file)
        with open(self.log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "temp", "hum", "co2", "pressure"])
            writer.writerow([
                timestamp, 
                data["temp"], 
                data["hum"], 
                data["co2"], 
                data.get("pressure")
            ])
