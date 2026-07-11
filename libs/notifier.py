import requests

class DiscordNotifier:
    def __init__(self, webhook_url):
        # 呼び出されたときにURLをしっかり受け取って記憶する
        self.webhook_url = webhook_url

    def send(self, message):
        """指定されたメッセージをDiscordに送信する"""
        if not self.webhook_url or self.webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
            print("[Notifier] ⚠️ Webhook URLが正しく設定されていません。")
            return False
            
        payload = {"content": message}
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 204:
                print("✓ Discordへの通知に成功しました。")
                return True
            else:
                print(f"✗ Discord通知失敗 (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"✗ Discord通信エラー: {e}")
            return False
