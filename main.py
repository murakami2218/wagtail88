# -*- coding: utf-8 -*-
import os
import sys
from flask import Flask, request, abort

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

#画像メッセージが送信されたときの処理
@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='いいねぇ(*^_^*)')) 

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