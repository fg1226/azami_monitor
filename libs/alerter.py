import json
import os
from libs.notifier import DiscordNotifier

class AlertManager:
    def __init__(self, state_file, webhook_url):
        self.state_file = state_file
        self.notifier = DiscordNotifier(webhook_url)

    def check(self, data):
        co2 = data["co2"]
        state = self._load_state()
        was_alerting = state["is_alerting"]
        USER_ID = "573382845259841547"
        mention = f"<@{USER_ID}> "        
        if co2 > 1000 and not was_alerting:
            self.notifier.send(f"{mention}\n🚨 **【換気アラート】CO2濃度が {co2} ppm に達しました！窓を開けて換気してください！**")
            self._save_state(True)
        elif co2 < 800 and was_alerting:
            self.notifier.send(f"{mention}\n🟢 **【換気完了】CO2濃度が {co2} ppm まで下がりました。もう大丈夫ですよ～！窓を閉めて構いません。**")
            self._save_state(False)

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {"is_alerting": False}

    def _save_state(self, is_alerting):
        with open(self.state_file, "w") as f:
            json.dump({"is_alerting": is_alerting}, f)
