import os, ssl, json, requests
from urllib.request import urlopen
from flask import Flask, request, abort
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from test__openai import chat
from linebot import LineBotApi, WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (Configuration,ApiClient,MessagingApi,ReplyMessageRequest,TextMessage)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.models import MessageEvent, TextMessage, TextSendMessage

Invoice_url = 'https://invoice.etax.nat.gov.tw/index.html'
web = requests.get(Invoice_url)
web.encoding='utf-8'

soup = BeautifulSoup(web.text, "html.parser")
td = soup.select('.container-fluid')[0].select('.etw-tbiggest')
ns = td[0].getText()  # 特別獎
n1 = td[1].getText()  # 特獎

weather_element_name = {
    'Wx'  : '天氣現象',
    'PoP' : '降雨機率',
    'CI'  : '舒適程度',
    'MinT': '最低溫度',
    'MaxT': '最高溫度'
}

app = Flask(__name__)
Chat_key = os.getenv('Chat_key',None)
CWA_key = os.getenv('CWA_key',None)
Secret = os.getenv('Linebot_Secret', None)
Token = os.getenv('Linebot_Token',None)
line_bot_api = LineBotApi(Token)
line_handler = WebhookHandler(Secret)
config = Configuration(access_token=Token)

CWA_url ='https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + str(CWA_key) + '&format=JSON'

city=''

@app.route('/')
def home():
    return 'Hello World!'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def City(user_city):
    ssl._create_default_https_context = ssl._create_unverified_context
    response = urlopen(CWA_url)
    data = response.read()
    weather_data = json.loads(data)

    Forecasts = dict()
    # 每一個location
    for location in weather_data['records']['location']:
        # print(location['locationName']) 城市名稱
        city_name = location['locationName']

        if city_name == user_city:

            Forecast = dict()
            # 每一種天氣預報的數值, eg: CI, Wx, PoP, MinT, MaxT
            for element in location['weatherElement']:
                # print(element['elementName'], end=': ') 數值的名稱, 結尾用冒號。
                # print(element['time'][0]['parameter']['parameterName']) 取時間最靠近的數值，所以取index 0。
                
                # 取得資訊
                element_name = element['elementName'] # 英文名稱
                element_value = element['time'][0]['parameter']['parameterName']
                if element_name in ['MinT', 'MaxT']:
                    element_unit = '°C'
                elif element_name in ['PoP']:
                    element_unit = '%'
                else:
                    element_unit = ''

                # 轉成對應的中文名稱
                element_name = weather_element_name[element_name]
                Forecast[element_name] = element_value + element_unit
        else:
            continue

        Forecasts[city_name] = Forecast

        bot_response = ''
        for location in Forecasts: # 取得每一個縣市的名稱
            bot_response += f"{location}:\n" # 加入縣市名稱訊息到response
            for weather_key in sorted(Forecasts[location]): # 根據縣市名稱，取得縣市天氣資料
                bot_response += f"\t\t\t\t{weather_key}: {Forecasts[location][weather_key]}\n"
        bot_response = bot_response.strip()
        bot_response = '請用以下的天氣資料，生成一段天氣預報&外出建議: ' + bot_response
        
    return chat(bot_response,Chat_key,'Helios')



@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):        
    userID = event.source.user_id #傳訊息的人的ID

    if event.message.text == "1":        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(City('臺北市'))))        

    elif event.message.text == "2":        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(City('桃園市'))))
        
    elif event.message.text=='3':            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(City('新竹市'))))
        
    elif event.message.text=='4':            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(City('臺中市'))))
        
    elif event.message.text=='5':            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='特別獎: '+str(ns)))
    
    elif event.message.text=='6':            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='頭獎: '+str(n1)))
        
    else:
        if Chat_key and event.message.text:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=chat(event.message.text,Chat_key,userID)))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='ChapGPT Error'))

if __name__ == "__main__":
    app.run()
