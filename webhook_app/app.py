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

from urllib import request as urllib_request
from bs4 import BeautifulSoup

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
    response_bus_data(event)


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    response_bus_data(event)

def response_bus_data(event):
    bus_data = fetch_bus_data()
    if bus_data is None:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='本日の運行は終了しました'))
        return

    bus_text = build_bus_text(bus_data, limit=2)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=bus_text))

def build_bus_text(bus_data, limit):
    head = '{time}\n{pole}\n'.format(**bus_data)
    body = ''
    for data in bus_data['bus'][:limit]:
        body+= '{table_time} {destination}行きは、{description}\n'.format(**data)

    return head + body


def fetch_bus_data():
    response = urllib_request.urlopen('http://www.odakyubus-navi.com/blsys/loca?VID=ldt&EID=nt&DSMK=83&DK=2j_6u_1b&DK=2j_6u_6q')
    body = response.read()
    soup = BeautifulSoup(body)
    result_div = soup.find('div', {'class': 'resultBox'})
    if result_div is None:
        return None
    # print(result_div)
    time = result_div.find('p', {'class': 'time'})
    # print(time.string)
    pole = result_div.find('h3', {'class': 'pole'})
    # print(pole.string)
    table = result_div.find('table', { 'class': 'resultTbl'})
    # print(table.string)
    bus = []
    for tr in table.find_all('tr'):
        if len(tr.find_all('td')) != 0:
            (table_time, predict_time, destination, bus_type, description) = [th.string for th in tr.find_all('td')]
            # print(table_time)
            # print(predict_time)
            # print(destination)
            # print(bus_type)
            # print(description)
            bus.append({
                'table_time': table_time,
                'predict_time': predict_time,
                'destination': destination,
                'bus_type': bus_type,
                'description': description,
                })
    return {
        'time': time.string,
        'pole': pole.string,
        'bus': bus,
        }


if __name__ == '__main__':                        
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
