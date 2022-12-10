import requests

URL = "https://api.telegram.org/bot"


class Telegram:
    def __init__(self, token):
        self.__url = f"{URL}{token}"

    def get_webhook(self):
        url = f"{self.__url}/getWebhookInfo"
        return requests.post(url)

    def set_webhook(self, webhook_url):
        url = f"{self.__url}/setWebhook"
        data = {"url": webhook_url}
        return requests.post(url, data=data)

    def delete_webhook(self):
        url = f"{self.__url}/deleteWebhook"
        return requests.post(url)

    def send_message(self, chat_id, message):
        url = f"{self.__url}/sendMessage"
        data = {"chat_id": chat_id,
                "text": message}
        return requests.post(url, data=data)

    def upload_video(self, chat_id, caption, filename):
        data = {"chat_id": chat_id, "caption": caption}
        url = f"{self.__url}/sendVideo"
        with open(filename, "rb") as fr:
            requests.post(url, data=data, files={"video", fr})
