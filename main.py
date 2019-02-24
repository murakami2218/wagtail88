# -*- coding: utf-8 -*-
import requests, json, os, io, cv2
from io import BytesIO
from PIL import Image
import sys
from flask import Flask, request, abort
import h5py
from keras.models import Model, Sequential, load_model
from keras.preprocessing import image
from keras.utils.np_utils import to_categorical
from keras.layers import Dense, Dropout, Flatten, Input, GlobalAveragePooling2D
from keras.applications.vgg16 import VGG16
from keras import optimizers
#from keras.preprocessing import load_img, img_to_array
import tensorflow as tf
import numpy as np
import tempfile
import cv2
#import matplotlib.pyplot as plt

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, TextSendMessage, FollowEvent
)

app = Flask(__name__)

# 環境変数からchannel_secret・channel_access_tokenを取得
# channel_secret = os.environ['LINE_CHANNEL_SECRET']
# channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

# if channel_secret is None:
#     print('Specify LINE_CHANNEL_SECRET as environment variable.')
#     sys.exit(1)
# if channel_access_token is None:
#     print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
#     sys.exit(1)

# line_bot_api = LineBotApi(channel_access_token)
line_bot_api = LineBotApi('jYMeYeWivnfSMv/Acr2ZoI9PRi6nMo0zEJD3JVcaRvbLguzbwyTIrswbH2kUV4n4uNMtNKyRBzENYG3icRMgDCqgHslu1T6pXqJSMg9KjCw89xCmXsMdnwAtXvKJXlxoKKlmw5eWo/06tInrjURlOwdB04t89/1O/w1cDnyilFU=')
# handler = WebhookHandler(channel_secret)
handler = WebhookHandler('f21f90b64dfa9940749a58d86e604e37')

header = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + YOUR_CHANNEL_ACCESS_TOKEN
}

# model はグローバルで宣言し、初期化しておく
model = None

@app.route("/")
def hello_world():
    return "Hello World"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#テキストメッセージが送信されたときの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == 'おはよう':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='おはようございます、ご主人様(*^_^*)'))
    elif text == 'こんにちは':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='こんにちは、ご主人様(*^_^*)'))
    elif text == 'こんばんは':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='こんばんは、ご主人様(*^_^*)')) 
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    print("handle_image:", event)

    message_id = event.message.id
    getImageLine(message_id)

    try:
        image_text = get_text_by_ms(image_url=getImageLine(message_id))

        messages = [
            TextSendMessage(text=image_text),
        ]

        line_bot_api.reply_message(event, messages)

    except Exception as e:
        line_bot_api.reply_message(event, TextSendMessage(text='エラーが発生しました'))

def getImageLine(id):

    line_url = 'https://api.line.me/v2/bot/message/' + id + '/content/'

    # 画像の取得
    result = requests.get(line_url, headers=header)
    print(result)

    # 画像の保存
    im = Image.open(BytesIO(result.content))
    filename = '/tmp/' + id + '.jpg'
    print(filename)
    im.save(filename)

    return filename

def get_text_by_ms(image_url):
    image = cv2.imread(image_url)
    if image is None:
        print("Not open")
    b,g,r = cv2.split(image)
    image = cv2.merge([r,g,b])
    img = cv2.resize(image,(32,32))
    img=np.expand_dims(img,axis=0)
    gender = detect_gender(img)

    text = gender
    return text

def detect_gender(img):

    gender = ""
    # グローバル変数を取得する
    global model

    # 一番初めだけ model をロードしたい
    if model is None:
        model = load_model('./param_vgg_15.hdf5')

    result = model.predict(img)
    predicted = np.argmax(result)

    if predicted == 0:
        gender = "男"
    elif predicted == 1:
        gender = "女"
    else:
        gender = "幽霊"
    return gender

#フォローイベント時の処理
@handler.add(FollowEvent)
def handle_follow(event):
    #誰が追加したかわかるように機能追加
    profile = line_bot_api.get_profile(event.source.user_id)
    line_bot_api.push_message("U976352bf0af02711f9d172e8317f26bc",
        TextSendMessage(text="表示名:{}\nユーザID:{}\n画像のURL:{}\nステータスメッセージ:{}"\
        .format(profile.display_name, profile.user_id, profile.picture_url, profile.status_message)))
    
    #友達追加したユーザにメッセージを送信
    line_bot_api.reply_message(      
        event.reply_token, TextSendMessage(text='友達になってくれてありがとう(*^_^*)'))

if __name__ == "__main__":
    app.run()