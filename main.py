import os
import re
#from _ast import pattern

#import yt_dlp
from dotenv import load_dotenv
from flask import Flask, jsonify, request, make_response
from tapi import Telegram
from pprint import pprint
from threading import Thread
from plumbum import local

load_dotenv()

app = Flask(__name__)


@app.route('/status', methods=['GET'])
def get_status():
    return make_response(jsonify({"status": "OK", "msg": "Up and running"}),
                         200)


@app.route('/info', methods=['GET'])
def get_info():
    token = os.getenv("TELEGRAM_API_TOKEN")
    telegram = Telegram(token)
    response = telegram.get_webhook()
    return response.text, 200


@app.route('/set', methods=['GET'])
def set_webhook():
    token = os.getenv("TELEGRAM_API_TOKEN")
    url = os.getenv("URL")
    telegram = Telegram(token)
    response = telegram.set_webhook(f"{url}/webhook")
    return response.text, 200


@app.route('/delete', methods=['GET'])
def delete_webhook():
    token = os.getenv("TELEGRAM_API_TOKEN")
    telegram = Telegram(token)
    response = telegram.delete_webhook()
    return response.text, 200


@app.route('/webhook', methods=['POST'])
def webhook():
    token = os.getenv("TELEGRAM_API_TOKEN")
    telegram = Telegram(token)
    message = request.json
    pprint(message)
    if message and 'message' in message and 'update_id' in message:
        content = message['message']
        if 'entities' in content and 'text' in content:
            chat_id = message['message']['chat']['id']
            telegram.send_message(chat_id, "Hello")
            print(chat_id)
            for entity in content['entities']:
                if entity["type"] == "url":
                    offset = entity["offset"]
                    end = offset + entity["length"]
                    url = content['text'][offset:end]
                    m = re.search(pattern, url)
                    if m:
                        code = m.group(6)
                        print(code)
                        athread = Thread(target=download, args=(code, telegram, chat_id))
                        athread.deamon = True
                        athread.start()
    print("We have already answered Telegram")
    return 'OK', 200


def download(code, telegram, chat_id):
    telegram.send_message(chat_id,
                          "Starting the download... wait a bit")
    origen = "/tmp/origen.mp4"
    destino = "/tmp/destino.mp4"
    if os.path.exists(origen):
        os.remove(origen)
    if os.path.exists(destino):
        os.remove(destino)
    url = f"https://www.youtube.com/watch?v={code}"
    ydl_opts = {"outtmpl": "/tmp/origen",
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                "retries": 5,
                "concurrent-fragments": 5,
                "fragment-retries": 5}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    telegram.send_message(chat_id, "Download completed")
    telegram.send_message(chat_id, "Starting the cut of the video")
    ffmpeg = local["ffmpeg"]
    ffmpeg["-y", "-ss", "0", "-to", "600", "-c:a", "copy", "-c:v", "copy",
           "-i", origen, destino]()
    telegram.send_message(chat_id, "End of the cut of the video")
    telegram.send_message(chat_id, "Beginning the upload of the video")
    telegram.upload_video(chat_id, "Video", destino)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8008)
