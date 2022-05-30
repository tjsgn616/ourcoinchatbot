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

@app.route('/more',methods=['POST'])
def test():
    # 마켓 이름 데이터, 환율값, 발화 값 가져오기
    nameData = marketData()
    dataRecive = request.get_json()
    coin = dataRecive['action']['params']['guideMore'].upper().replace(" ","")
    USD = requests.get('https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD')
    USD = USD.json()
    USD = USD[0]['basePrice']
    print(coin)

    
    answer = []
    for i in nameData.index:
        if coin == nameData.korean_name[i] or coin == nameData.english_name[i] or coin == nameData.market[i]:
            answer.append([nameData.market[i],nameData.currency[i]])

    # 전체 마켓 시장에서 입력한 코인과 같은 종류의 코인 뽑아서 리스트로 반환 (KRW, BTC,USDT)
    # 코인 외 잘못 발화된 값은 coin_now =[]로 빈 리스트 추출
    # 다양한 입력 형태 다 포용한다.
    name_list = nameData.values.tolist()
    # print(name_list[:4])
    coin_now = []
    for i in range(len(name_list)):
        if coin in name_list[i]:
            coin_now.extend(name_list[i])
    # print("---coin_name----",coin_now)
    coin_now = set(coin_now)
    # print("----no 중복 코인 ----",coin_now)

    # 해당 코인의 화폐 시장 종류 뽑아내서 리스트로 반환 ->selection ['KRW','BTC','USDT] 형태
    # 잘못된 발화인 경우 selection =[] 빈 리스트 추출
    selection = []
    for i in range(len(answer)):
        selection.append(answer[i][1])


    if coin not in coin_now:
        coin_error = {
            "version":"2.0",
            "template":{
                "outputs":[
                    {
                        "basicCard":{
                            "title":"입력 오류",
                            "description":"존재하지 않는 가상 화폐이거나 입력 오류입니다",
                            "thumbnail":{
                                "imageUrl":"https://user-images.githubusercontent.com/65166786/169485601-ea315e41-4b3c-4520-b11a-6461d3e3233e.jpg"
                            },
                            "buttons":[
                                {
                                    "action":"block",
                                    "label":"다시 입력하기",
                                    "blockId": "628d8ff47bd2fd433357e2ee",
                                    "messageText":"짜잔!"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        return coin_error
    else:
        # 어떤 형태의 코인을 입력하던지 한국 이름으로 출력하게 한다.
        j=0
        for i in name_list:
            if coin in i:
                coin_id = nameData.iloc[j]['Id']
                coin_korea = nameData.iloc[j]['korean_name']
                break
            j +=1
        

        # 첫 배포 -> KRW 기준의 시세조회
        # KRW 시장이 없는 코인의 경우 -> 해당 시장 값 * btc로 원화 값 반환
        # KRW 시장이 있는 경우 그대로 현재 시세 조회
        market_or_name =[]
        for i in range (len(name_list)):
            market_or_name.append(nameData.market[i])
        # print(market_or_name)

        # market code로 입력할 경우 그대로 코인 값 출력
        # 한글 또는 영어 이름 입력할 경우 -> KRW,BTC,USDT순으로 첫번째로 존재하는 값 출력
        if coin in market_or_name:
            print("market 인지")
            print(coin)
            ticker = coin
            # coin_price = pyupbit.get_current_price(coin)
            coin_code = coin.split('-')[0]
            if coin_code == "KRW":
                coin_price = pyupbit.get_current_price(coin)
            elif coin_code == "BTC":
                BITCOIN = pyupbit.get_current_price("KRW-BTC")
                coin_price = pyupbit.get_current_price(coin) * BITCOIN
            else:
                coin_price = pyupbit.get_current_price(coin) * USD
        else : 
            print("한글 또는 영어입니다.")
            print(coin)
            if "KRW" not in selection:
                # print("KRW 없음")
                if "BTC" in selection:
                    BITCOIN = pyupbit.get_current_price("KRW-BTC")
                    BTC = selection.index("BTC")
                    ticker = answer[BTC][0]
                    coin_money = pyupbit.get_current_price(ticker)
                    coin_price = (BITCOIN * coin_money)
                    # print("한국 돈 변환 값 BTC : ",coin_price)
                else : 
                    ticker = answer[0][0]
                    coin_money = pyupbit.get_current_price(ticker)
                    coin_price = (USD * coin_money)
                    # print("한국 돈 변환 값 USDT : ",coin_price)
            else:
                # print("KRW 인덱스 값 KRW:" , selection.index("KRW"))
                KRW = selection.index("KRW")
                ticker = answer[KRW][0]
                coin_price = pyupbit.get_current_price(ticker)

        tz = pytz.timezone('Asia/Seoul')
        time_now = datetime.datetime.now(tz)
        time_now = time_now.strftime('%Y-%m-%d %H:%M')
        print(time_now)

        coin_price_now = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                            "carousel": {
                            "type": "itemCard",
                            "items": [
                                {
                                "imageTitle": {
                                    "title": "현재 시세 조회",
                                    "imageUrl" : f"https://static.upbit.com/logos/{coin_id}.png"
                                },
                                "itemList": [
                                    {
                                    "title": "가상 화폐",
                                    "description": f"{coin_korea}"
                                    },
                                    {
                                    "title": "현재 시간",
                                    "description": f"{time_now}"
                                    },
                                    {
                                    "title" : "기준",
                                    "description" : "KRW"
                                    },
                                    {
                                    "title" : "현재 시세",
                                    "description" : f"{coin_price:,}원"
                                    }
                                ],
                                "itemListAlignment": "left",
                                "buttons": [
                                    {
                                    "label": "추가 조회",
                                    "action": "block",
                                    "blockId": "628d8ff47bd2fd433357e2ee",
                                    "messageText" : "추가 조회"
                                    },
                                    {
                                    "label": "업비트",
                                    "action": "webLink",
                                    "messageText": "업비트 보러가기",
                                    "webLinkUrl": f"https://upbit.com/exchange?code=CRIX.UPBIT.{ticker}"
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        }
        return coin_price_now






