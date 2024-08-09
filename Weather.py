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

url = 'https://invoice.etax.nat.gov.tw/index.html'
web = requests.get(url)
web.encoding='utf-8'

soup = BeautifulSoup(web.text, "html.parser")
td = soup.select('.container-fluid')[0].select('.etw-tbiggest')
ns = td[0].getText()  # 特別獎
n1 = td[1].getText()  # 特獎


app = Flask(__name__)
key = os.getenv('Chat_key',None)
Secret = os.getenv('Linebot_Secret', None)
Token = os.getenv('Linebot_Token',None)
line_bot_api = LineBotApi(Token)
line_handler = WebhookHandler(Secret)
config = Configuration(access_token=Token)

url ='https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWA-E5DD6503-6C55-4E4E-BB83-ABADD30BE3AA&format=JSON'


ansA=[]
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


def myG(aa):
    ansA.clear()
    ssl._create_default_https_context = ssl._create_unverified_context
    response = urlopen(url)
    data = response.read()
    output = json.loads(data)
    location=output['records']['location']
    for i in location:
        city = i['locationName']
        if city==aa:
            wx = i['weatherElement'][0]['time'][0]['parameter']['parameterName']
            maxtT = i['weatherElement'][4]['time'][0]['parameter']['parameterName']
            mintT = i['weatherElement'][2]['time'][0]['parameter']['parameterName']
            ci = i['weatherElement'][3]['time'][0]['parameter']['parameterName']
            pop = i['weatherElement'][4]['time'][0]['parameter']['parameterName']
            
            ansA.append(city)
            ansA.append(wx)
            ansA.append(mintT)
            ansA.append(maxtT)
    return ansA



@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):        

    if event.message.text == "1":        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(myG('臺北市'))))        

    elif event.message.text == "2":        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(myG('桃園市'))))
        
    elif event.message.text=='3':            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(myG('新竹市'))))
        
    elif event.message.text=='4':            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=str(myG('臺中市'))))
        
    elif event.message.text=='5':            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='特別獎: '+str(ns)))
    
    elif event.message.text=='6':            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='頭獎: '+str(n1)))
        
    else:
        if key and event.message.text:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=chat(event.message.text,key)))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='ChapGPT Error'))

if __name__ == "__main__":
    app.run()
