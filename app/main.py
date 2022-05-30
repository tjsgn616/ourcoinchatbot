#from re import template
from flask import Flask, jsonify, request #, g ,make_response
import pandas as pd
import pyupbit
import requests
import datetime
import pytz
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
from bs4 import BeautifulSoup
#from pandas import DataFrame
#import re
import urllib.request
from urllib.parse import quote


app = Flask(__name__)

top_acc = pd.read_csv("./app/data/top_acc.csv")
top_change = pd.read_csv("./app/data/top_change.csv")
top_live = pd.read_csv("./app/data/live_top.csv")
top_market_list = pd.read_csv("./app/data/market_list.csv")



def marketData():
    # 마켓 데이터 불러오기
    marketData = requests.get('https://api.upbit.com/v1/market/all') # API 그냥 쓰면 되는듯

    if marketData.status_code == 200 :
        marketData = marketData.json()

    # 마켓 코드, 한글, 영어 df로 정리
    market = []
    korean_name = []
    english_name = []
    for i in range(len(marketData)) :
        namedata = marketData[i]
        market.append(namedata['market'])
        korean_name.append(namedata['korean_name'])
        english_name.append(namedata['english_name'].upper().replace(" ",""))

    namedata= pd.DataFrame((zip(market, korean_name, english_name)), columns = ['market', 'korean_name', 'english_name'])
    
    # 코인 종류 분할
    currency = []
    for i in namedata.loc[:,'market']:
        if i.split('-')[0] == "KRW":
            currency.append("KRW")
        elif i.split('-')[0] == "BTC":
            currency.append("BTC")
        else:
            currency.append("USDT")
    namedata['currency'] = currency
    coinId = []
    for i in namedata.loc[:,"market"]:
        coinId.append(i.split('-')[1])
    namedata['Id'] = coinId
    return namedata





@app.route('/now', methods=['POST'])
def now():
    best_Id = ['KRW-BTC', 'KRW-ETH','KRW-DOGE']
    current_price =  {  "version": "2.0",
                        "template": {
                            "outputs": [
                            {
                                "carousel": {
                                "type": "listCard",
                                "items": [
                                    {
                                    "header": {
                                        "title": "현재 시세 조회"
                                    },
                                    "items": [
                                        {
                                        "title": "비트코인",
                                        "description" : f"{pyupbit.get_current_price(best_Id[0]):.2f}원",
                                        "imageUrl": "https://static.upbit.com/logos/BTC.png"
                                        },
                                        {
                                        "title": "이더리움",
                                        "description": f"{pyupbit.get_current_price(best_Id[1]):.2f}원",
                                        "imageUrl": "https://static.upbit.com/logos/ETH.png"
                                        },
                                        {
                                        "title": "도지코인",
                                        "description": f"{pyupbit.get_current_price(best_Id[2]):.2f}원",
                                        "imageUrl": "https://static.upbit.com/logos/DOGE.png"
                                        }],
                                    "buttons": [
                                        {
                                        "label": "더 많은 코인 보러가기",
                                        "action": "block",
                                        "blockId": "628d8ff47bd2fd433357e2ee"
                                        }
                                    ]
                                    }
                                ]
                                }
                            }
                        
                            ]
                        }
                    }
    return current_price





