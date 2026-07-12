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
        
        count = state.get("count", 0)
        was_alerting = state["is_alerting"]
        
        USER_ID = "573382845259841547"
        mention = f"<@{USER_ID}> "        
        
        # 1000を超えていたらカウントアップ
        if co2 > 1000:
            count += 1
            # 3回連続超えたらアラート（既にアラート中なら重複通知しない）
            if count >= 3 and not was_alerting:
                self.notifier.send(f"{mention}\n🚨 **【換気アラート】CO2濃度が {co2} ppm に達しました！窓を開けて換気してください！**")
                self._save_state(True, 0)
                return
        # 800未満になったら回復判定
        elif co2 < 800 and was_alerting:
            self.notifier.send(f"{mention}\n🟢 **【換気完了】CO2濃度が {co2} ppm まで下がりました。もう大丈夫ですよ～！窓を閉めて構いません。**")
            self._save_state(False, 0)
            return
        else:
            # 閾値の範囲内ならカウントをリセット
            count = 0

        # 状態を保存（アラート中でなければ現在のカウントを保持）
        self._save_state(was_alerting, count)

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {"is_alerting": False, "count": 0}

    def _save_state(self, is_alerting, count):
        with open(self.state_file, "w") as f:
            json.dump({"is_alerting": is_alerting, "count": count}, f)
