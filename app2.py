import os
import sys
import json
from datetime import datetime
import requests
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from flask import Flask, request
import codecs


app = Flask(__name__)

FB_ACCESS_TOKEN = "EAAbbpqtrkj8BAGjpgddvNgI54G2btUIVnZB1UhPYk4zk6IqSI9u5t610hqxsxTSPACGchLPreZAZA5BBwaveDHa08e1TDABaHXagAyAVIvQeqZBAp1t3FXSn8o7624h9eO3kvzTgjK7FDRoJ74ZBmZBeVzSeP0kqmeZBRKUvcba7CZB0giTMkMk2u2UuOPw3NCQZD"

bot = ChatBot('Servify_bot')

bot.set_trainer(ListTrainer)

curr_dir = os.getcwd()
path = curr_dir + '/data/'

for files in os.listdir(path):
    data = codecs.open(path + files, 'r', encoding='iso-8859-1').readlines()
    bot.train(data)

VERIFICATION_TOKEN = "hello"


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFICATION_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    print(request.data)
    data = request.get_json()

    if data['object'] == "page":
        entries = data['entry']

        for entry in entries:
            messaging = entry['messaging']

            for messaging_event in messaging:

                sender_id = messaging_event['sender']['id']
                recipient_id = messaging_event['recipient']['id']

                if messaging_event.get('message'):
                    # HANDLE NORMAL MESSAGES HERE
                    if messaging_event['message'].get('text'):
                        # HANDLE TEXT MESSAGES
                        message = messaging_event['message']['text']
                        # ECHO THE RECEIVED MESSAGE
                        default_response = bot.get_response(message)
                        send_message(sender_id, str(default_response))

    return "Hello world", 200


def send_message(recipient_id, message_text):

    print("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": FB_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)

    return "Hello world", 200


'''
def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = unicode(msg).format(*args, **kwargs)
        print u"{}: {}".format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()
'''

if __name__ == "__main__":
    app.run(debug=True)
