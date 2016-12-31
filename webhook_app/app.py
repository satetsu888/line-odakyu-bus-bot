import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, LocationMessage, TextSendMessage, StickerMessage,
    FollowEvent,
)

from webhook_app import create_app
from webhook_app.lib import bus

app = create_app()

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

@app.route('/')                                   
def hello_world():                                
    return "Hello World!!!"

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


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    response_pole_data(event)


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    response_bus_data(event)

def response_bus_data(event):
    bus_data = bus.fetch_bus_data()
    if bus_data is None:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='本日の運行は終了しました'))
        return

    bus_text = bus.build_bus_text(bus_data, limit=2)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=bus_text))

def response_pole_data(event):
    text = event.message.text

    pole_data = bus.search_pole(text)




if __name__ == '__main__':                        
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
