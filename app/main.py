from re import template
from flask import Flask, make_response, jsonify, request, g
import pandas as pd
import pyupbit
import requests
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
from bs4 import BeautifulSoup
from pandas import DataFrame
import re
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

@app.route('/acc',methods=['POST'])
def acc():
    # market 한국 이름 뽑아내기
    nameData = marketData()
    # -------------------------------------------------if문 top_market_list nameData로 바꾸기
    top_acc_kor = []
    top_change_kor = []
    top_live_kor = []
    top_acc_id = []
    top_change_id = []
    top_live_id = []
    for i in range(5):
        for j in range(len(top_market_list)):
            if top_market_list.iloc[j]['market'] == top_acc.iloc[i]['market']:
                # top_acc_kor.append(top_market_list.iloc[j]['korean_name'])
                top_acc_kor.append(nameData.iloc[j]['korean_name'])
                top_acc_id.append(nameData.iloc[j]['Id'])
            if top_change.iloc[i]['market'] == top_market_list.iloc[j]['market']:
                top_change_kor.append(nameData.iloc[j]['korean_name'])
                top_change_id.append(nameData.iloc[j]['Id'])
            if top_live.iloc[i]['market'] == top_market_list.iloc[j]['market']:
                top_live_kor.append(nameData.iloc[j]['korean_name'])
                top_live_id.append(nameData.iloc[j]['Id'])



    live_coin = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText" : {
                            "text":"'실시간 TOP5 코인'에서는 1시간 기준 실시간 거래량과 변동량을 확인 할 수 있는 곳입니다."
                        }
                    },
                {
                    "carousel": {
                    "type": "listCard",
                    "items": [
                        {
                        "header": {
                            "title": "실시간 누적 거래량 TOP 5"
                        },
                        "items": [
                            {
                            "title": f"{top_acc_kor[0]} ({top_acc.iloc[0]['market']})",
                            "description": f"{top_acc.iloc[0]['change_rate']:,}-{top_acc.iloc[0]['change_rate_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_acc_id[0]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_acc_kor[0]}",
                                "key2": f"{top_acc.iloc[0]['market']}",
                                "key3": f"{top_acc_id[0]}"
                            }
                            },
                            {
                            "title": f"{top_acc_kor[1]} ({top_acc.iloc[1]['market']})",
                            "description": f"{top_acc.iloc[1]['change_rate']:,}-{top_acc.iloc[1]['change_rate_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_acc_id[1]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_acc_kor[1]}",
                                "key2": f"{top_acc.iloc[1]['market']}",
                                "key3": f"{top_acc_id[1]}"
                            }
                            },
                            {
                            "title": f"{top_acc_kor[2]} ({top_acc.iloc[2]['market']})",
                            "description": f"{top_acc.iloc[2]['change_rate']:,}-{top_acc.iloc[2]['change_rate_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_acc_id[2]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_acc_kor[2]}",
                                "key2": f"{top_acc.iloc[2]['market']}",
                                "key3": f"{top_acc_id[2]}"
                            }
                            },
                            {
                            "title": f"{top_acc_kor[3]} ({top_acc.iloc[3]['market']})",
                            "description": f"{top_acc.iloc[3]['change_rate']:,}-{top_acc.iloc[3]['change_rate_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_acc_id[3]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_acc_kor[3]}",
                                "key2": f"{top_acc.iloc[3]['market']}",
                                "key3": f"{top_acc_id[3]}"
                            }
                            },
                            {
                            "title": f"{top_acc_kor[4]} ({top_acc.iloc[4]['market']})",
                            "description": f"{top_acc.iloc[4]['change_rate']:,}-{top_acc.iloc[4]['change_rate_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_acc_id[4]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_acc_kor[4]}",
                                "key2": f"{top_acc.iloc[4]['market']}",
                                "key3": f"{top_acc_id[4]}"
                            }
                            }
                        ]
                        },
                        {
                        "header": {
                            "title": "정각 기준 실시간 변동량 TOP 5"
                        },
                        "items": [
                            {
                            "title": f"{top_live_kor[0]} ({top_live.iloc[0]['market']})",
                            "description": f"{top_live.iloc[0]['live_rate']}-{top_live.iloc[0]['live_rate_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_live_id[0]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_live_kor[0]}",
                                "key2": f"{top_live.iloc[0]['market']}",
                                "key3": f"{top_live_id[0]}"
                            }
                            },
                            {
                            "title": f"{top_live_kor[1]} ({top_live.iloc[1]['market']})",
                            "description": f"{top_live.iloc[1]['live_rate']}-{top_live.iloc[1]['live_rate_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_live_id[1]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_live_kor[1]}",
                                "key2": f"{top_live.iloc[1]['market']}",
                                "key3": f"{top_live_id[1]}"
                            }
                            },
                            {
                            "title": f"{top_live_kor[2]} ({top_live.iloc[2]['market']})",
                            "description": f"{top_live.iloc[2]['live_rate']}-{top_live.iloc[2]['live_rate_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_live_id[2]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_live_kor[2]}",
                                "key2": f"{top_live.iloc[2]['market']}",
                                "key3": f"{top_live_id[2]}"
                            }
                            },
                            {
                            "title": f"{top_live_kor[3]} ({top_live.iloc[3]['market']})",
                            "description": f"{top_live.iloc[3]['live_rate']}-{top_live.iloc[3]['live_rate_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_live_id[3]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_live_kor[3]}",
                                "key2": f"{top_live.iloc[3]['market']}",
                                "key3": f"{top_live_id[3]}"
                            }
                            },
                            {
                            "title": f"{top_live_kor[4]} ({top_live.iloc[4]['market']})",
                            "description": f"{top_live.iloc[4]['live_rate']}-{top_live.iloc[4]['live_rate_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_live_id[4]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_live_kor[4]}",
                                "key2": f"{top_live.iloc[4]['market']}",
                                "key3": f"{top_live_id[4]}"
                            }
                            }
                        ]
                        },
                        {
                        "header": {
                            "title": "전일 대비 실시간 변동량 TOP 5"
                        },
                        "items": [
                            {
                            "title": f"{top_change_kor[0]} ({top_change.iloc[0]['market']})",
                            "description": f"{top_change.iloc[0]['change']}-{top_change.iloc[0]['change_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_change_id[0]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_change_kor[0]}",
                                "key2": f"{top_change.iloc[0]['market']}",
                                "key3": f"{top_change_id[0]}"
                            }
                            },
                            {
                            "title": f"{top_change_kor[1]} ({top_change.iloc[1]['market']})",
                            "description": f"{top_change.iloc[1]['change']}-{top_change.iloc[1]['change_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_change_id[1]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_change_kor[1]}",
                                "key2": f"{top_change.iloc[1]['market']}",
                                "key3": f"{top_change_id[1]}"
                            }
                            },
                            {
                            "title": f"{top_change_kor[2]} ({top_change.iloc[2]['market']})",
                            "description": f"{top_change.iloc[2]['change']}-{top_change.iloc[2]['change_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_change_id[2]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_change_kor[2]}",
                                "key2": f"{top_change.iloc[2]['market']}",
                                "key3": f"{top_change_id[2]}"
                            }
                            },
                            {
                            "title": f"{top_change_kor[3]} ({top_change.iloc[3]['market']})",
                            "description": f"{top_change.iloc[3]['change']}-{top_change.iloc[3]['change_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_change_id[3]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_change_kor[3]}",
                                "key2": f"{top_change.iloc[3]['market']}",
                                "key3": f"{top_change_id[3]}"
                            }
                            },
                            {
                            "title": f"{top_change_kor[4]} ({top_change.iloc[4]['market']})",
                            "description": f"{top_change.iloc[4]['change']}-{top_change.iloc[4]['change_str']}",
                            "imageUrl": f"https://static.upbit.com/logos/{top_change_id[4]}.png",
                            "action":"block",
                            "blockId":"629020537befc3101c3bde55",
                            "extra":{
                                "key1": f"{top_change_kor[4]}",
                                "key2": f"{top_change.iloc[4]['market']}",
                                "key3": f"{top_change_id[4]}"
                            }
                            }
                        ],
                        "buttons": [
                            {
                            "label": "처음으로 돌아가기",
                            "action": "block",
                            "blockId":"627a3d5745b5fc3106459c56",
                            "messageText" : "처음으로 돌아가기"
                            }
                        ]
                        }
                    ]
                    }
                }
                ]
            }
        }
    return live_coin



# --------------------------------- 실시간 상세 조회  -------------------------------------
@app.route("/sang",methods=['POST'])
def sang():
    
    dataRecive = request.get_json()
    # print(dataRecive)
    coin_korea = dataRecive['action']['clientExtra']['key1']
    coin_market = dataRecive['action']['clientExtra']['key2']
    coin_id = dataRecive['action']['clientExtra']['key3']
    print(coin_korea,coin_market,coin_id)

    # 현재가 정보 불러오기
    url = f"https://api.upbit.com/v1/ticker?markets={coin_market}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    res = response.json()
    res = res[0]

    # KRW로 값 표시하기
    coin_kind = coin_market.split('-')[0]
    print(coin_kind)

    if "KRW" not in coin_kind:
        if "BTC" in coin_kind:
            toKRW = pyupbit.get_current_price("KRW-BTC")
        else : 
            USD = requests.get('https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD')
            USD = USD.json()
            USD = USD[0]['basePrice']
            toKRW = USD
    else:
        toKRW = 1

    

    # 시간 
    tz = pytz.timezone('Asia/Seoul')
    time_now = datetime.datetime.now(tz)
    time_now = time_now.strftime('%Y-%m-%d %H:%M')
    
    information = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "itemCard": {
                        "imageTitle": {
                            "title": f"{coin_market}",
                            "description": f"{time_now}"
                        },
                        "title": "BTC, USDT는 KRW로 환산된 값.",
                        "description": "52주 신고가/신저가 - ",
                        "thumbnail": {
                            "imageUrl": "https://user-images.githubusercontent.com/101306637/170913204-78700f45-1092-460d-a8c6-ef1d493b3bff.png",
                            "width": 800,
                            "height": 800
                        },
                        "profile": {
                            "title": f"{coin_korea}",
                            "imageUrl": f"https://static.upbit.com/logos/{coin_id}.png"
                        },
                        "itemList": [
                            {
                                "title": "시가",
                                "description": f"{res['opening_price'] * toKRW:,}"
                            },
                            {
                                "title": "고가",
                                "description": f"{res['high_price'] * toKRW:,}"
                            },
                            {
                                "title": "저가",
                                "description": f"{res['low_price']*toKRW:,}"
                            },
                            {
                                "title": "전일 종가",
                                "description": f"{res['prev_closing_price']*toKRW:,}"
                            },
                            {
                                "title": "변동률",
                                "description": f"{res['signed_change_rate']*100:,.2f}"
                            },
                            {
                                "title": "최근 거래량",
                                "description": f"{res['trade_volume']:,}"
                            },
                            {
                                "title": "신고가",
                                "description": f"{res['highest_52_week_price']*toKRW:,}"
                            },
                            {
                                "title": "신고가 달성",
                                "description": f"{res['highest_52_week_date']}"
                            },
                            {
                                "title": "신저가",
                                "description": f"{res['lowest_52_week_price']*toKRW:,}"
                            },
                            {
                                "title": "신저가 달성",
                                "description": f"{res['lowest_52_week_date']}"
                            }
                        ],
                        "itemListAlignment" : "right",
                        "itemListSummary": {
                            "title": "종가",
                            "description": f"{res['trade_price']*toKRW:,}"
                        },
                        "buttons": [
                            {
                                "label": "관련 뉴스 보러가기",
                                "action": "block",
                                "blockId": "6290494c51c40d32c6d8de9c",
                                "extra":{
                                "key": f"{coin_korea}"
                            }
                            },
                            {
                                "label": "업비트로 바로 가기",
                                "action": "webLink",
                                "webLinkUrl": f"https://upbit.com/exchange?code=CRIX.UPBIT.{coin_market}"
                            }
                        ],
                        "buttonLayout" : "vertical"
                    }
                }
            ]
        }
    }
    return information

@app.route('/hopeprice',methods=['POST'])
def hope_pirce():
    nameData = marketData()
    dataReceive = request.get_json()
    
    Coin_Name = dataReceive['action']['params']['HopePrice_Coin'].upper().replace(" ","")
    Average_Price = int(dataReceive['action']['params']['HopePrice_Average'])
    print(Average_Price)
     # 평균 가격
    Return_Rate = int(dataReceive['action']['params']['HopePrice_Rate']) # 수익률
    print(Return_Rate)
    
    Goal_Price = ((Return_Rate + 100)/100)*Average_Price
    Goal_Price = round(Goal_Price,1)

    USD = requests.get('https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD')
    USD = USD.json()
    USD = USD[0]['basePrice']

    # 
    answer = []
    for i in nameData.index:
        if Coin_Name == nameData.korean_name[i] or Coin_Name == nameData.english_name[i] or Coin_Name == nameData.market[i]:
            answer.append([nameData.market[i],nameData.currency[i]])

    # 전체 마켓 시장에서 입력한 코인과 같은 종류의 코인 뽑아서 리스트로 반환 (KRW, BTC,USDT)
    # 코인 외 잘못 발화된 값은 coin_now =[]로 빈 리스트 추출
    # 다양한 입력 형태 다 포용한다.
    name_list = nameData.values.tolist()
    # print(name_list[:4])
    Coin_now = []
    for i in range(len(name_list)):
        if Coin_Name in name_list[i]:
            Coin_now.extend(name_list[i])
    # print("---coin_name----",coin_now)
    Coin_now = set(Coin_now)
    # print("----no 중복 코인 ----",coin_now)

    # 해당 코인의 화폐 시장 종류 뽑아내서 리스트로 반환 ->selection ['KRW','BTC','USDT] 형태
    # 잘못된 발화인 경우 selection =[] 빈 리스트 추출
    selection = []
    for i in range(len(answer)):
        selection.append(answer[i][1])


    if Coin_Name not in Coin_now:
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
                                    "blockId": "627e143204a7d7314aebbda3",
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
            if Coin_Name in i:
                coin_id = nameData.iloc[j]['Id']
                coin_korea = nameData.iloc[j]['korean_name']
                break
            j +=1
        
        # print("aaaaaaaaaaaaaaaaaaa",coin_korea)

        # 첫 배포 -> KRW 기준의 시세조회
        # KRW 시장이 없는 코인의 경우 -> 해당 시장 값 * btc로 원화 값 반환
        # KRW 시장이 있는 경우 그대로 현재 시세 조회
        if "KRW" not in selection:
            # print("KRW 없음")
            if "BTC" in selection:
                BITCOIN = pyupbit.get_current_price("KRW-BTC")
                BTC = selection.index("BTC")
                ticker = answer[BTC][0]
                coin_money = pyupbit.get_current_price(ticker)
                coin_price = (BITCOIN * coin_money)
                income = round((coin_price/Average_Price)*100 - 100,2)
                # print("한국 돈 변환 값 BTC : ",coin_price)
            else : 
                ticker = answer[0][0]
                coin_money = pyupbit.get_current_price(ticker)
                coin_price = (USD * coin_money)
                income = round((coin_price/Average_Price)*100 - 100,2)
                # print("한국 돈 변환 값 USDT : ",coin_price)
        else:
            # print("KRW 인덱스 값 KRW:" , selection.index("KRW"))
            KRW = selection.index("KRW")
            ticker = answer[KRW][0]
            coin_price = pyupbit.get_current_price(ticker)
            income = round((coin_price/Average_Price)*100 - 100,2)
        
        coin_price_now = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                            "itemCard": {
                            
                            
                                "imageTitle": {
                                    "title": "희망 매도가 조회",
                                    "imageUrl" : f"https://static.upbit.com/logos/{coin_id}.png"
                                },
                                "itemList": [
                                    {
                                    "title": "가상 화폐",
                                    "description": f"{coin_korea}"
                                    },
                                    {
                                    "title" : "기준",
                                    "description" : "KRW"
                                    },
                                    {
                                    "title": "입력 평단가",
                                    "description": f"{Average_Price}"
                                    },{
                                    "title": "희망 수익률",
                                    "description": f"{Return_Rate}%"
                                    },{
                                    "title": "희망 가격",
                                    "description": f"{Goal_Price:.1f}원"
                                    },
                                    {
                                    "title" : "현재 시세",
                                    "description" : f"{coin_price:.1f}원"
                                    },{
                                    "title": "현재 수익률",
                                    "description": f"{income}%"
                                    }
                                ],
                                "itemListAlignment": "left",
                                "buttons": [
                                    {
                                    "label": "추가 조회",
                                    "action": "block",
                                    "blockId": "627e143204a7d7314aebbda3",
                                    "messageText" : "추가 조회"
                                    },
                                    {
                                    "label": "업비트",
                                    "action": "webLink",
                                    "messageText": "업비트 보러가기",
                                    "webLinkUrl": f"https://upbit.com/exchange?code=CRIX.UPBIT.{ticker}"
                                    },
                                    
                                ],
                                
                            }
                            }
                        ]
                    }
                }
            
        
        
        return coin_price_now

@app.route('/msg5', methods=['POST'])
def msg():
    dataReceive = request.get_json()
    
    #namedata2 = namedata
    
    #coin_name = dataReceive["action"]["detailParams"]["coi
    #coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","") # 코인 이름 받기
    coin_name = dataReceive['action']['params']['coin'].upper().replace(" ","") #.upper.replace(" ","")
    #coin_nu = coin_n.upper #.replace(" ","")
    #coin_name = coin_nu.replace(" ","")


    namedata = marketData() 
    answer = []
    for i in namedata.index:
        if coin_name == namedata.korean_name[i] or coin_name == namedata.english_name[i] or coin_name == namedata.market[i]:
            answer.append([namedata.market[i],namedata.currency[i],namedata.korean_name[i]])
        '''
        else :    
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
                                    "label":"시점 조회로 돌아가기",
                                    #"blockId": "627a1fd316b99e0c33812774",
                                    "blockId": "6281c5009ac8ed784416bccd",
                                    #"messageText":"짜잔!"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        return coin_error
        '''


    full_time = dataReceive["action"]["detailParams"]["datetime"]["origin"] # 시간대 받기
    full_time_replace = full_time.replace("-","").replace("T","").replace(":","")
    full_time_T = full_time.replace("T"," ")
    #print(full_time_replace) # 20220520000000
    #print(coin_name) # 비트코인
    #print(answer) # [['KRW-BTC', 'KRW'], ['USDT-BTC', 'USDT']]
    #print(answer[0][0]) # KRW-BTC
    #print(answer[0][2]) # q
    #print(namedata.korean_name[i])
    coin_ticker = answer[0][0]
    coin_id = coin_ticker[4:7] 
    #print(answer[0]) #  ['KRW-BTC', 'KRW']
    USD = requests.get('https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD')
    USD = USD.json()
    USD = USD[0]['basePrice'] #USDT 가격 조회를 위함.
    name_list = namedata.values.tolist()
    coin_now = []
    for i in range(len(name_list)):
        if coin_name in name_list[i]:
            coin_now.extend(name_list[i])
    print("---coin_name----",coin_now)
    #coin_id = ' '.join(coin_now[0])
    #coin_id = ''.join(coin_now[0])
    #print(coin_id)
    #coin_id_id = coin_id[4:7]
    #print(coin_id_id)
    coin_now = set(coin_now)
    print("----no 중복 코인 ----",coin_now)
    selection = []
    for i in range(len(answer)):
        selection.append(answer[i][1])

    if coin_name not in coin_now:
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
                                    "label":"시점 조회로 돌아가기",
                                    "blockId": "6281c5009ac8ed784416bccd",
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
        #KRW가 없을 때
        if "KRW" not in selection :
            if "BTC" in selection :
                #BITCOIN = pyupbit.get_current_price("KRW-BTC")
                BTC = selection.index("BTC")
                ticker = answer[BTC][0]
                print(ticker)
                current_price = pyupbit.get_current_price(ticker)
                past_price = pyupbit.get_ohlcv(ticker, interval="minute1", to=full_time_replace, count=1).open[0]
                #coin_money = pyupbit.get_current_price(ticker)
                #coin_price = (BITCOIN * coin_money)
            else:
                ticker = answer[0][0]
                current_price = pyupbit.get_current_price(ticker)
                past_price =pyupbit.get_ohlcv(ticker, interval="minute1", to=full_time_replace, count=1).open[0]
                #coin_money = pyupbit.get_current_price(ticker)
                #coin_price = (USD * coin_money)
                #print("한국 돈 변환 값 USDT : ",coin_price)
        else:
            print("KRW 인덱스 값 KRW:" , selection.index("KRW"))
            KRW = selection.index("KRW")
            ticker = answer[KRW][0]
            current_price = pyupbit.get_current_price(ticker)
            past_price =pyupbit.get_ohlcv(ticker, interval="minute1", to=full_time_replace, count=1).open[0]
            #coin_price = pyupbit.get_current_price(ticker)
    #while True:
     #   try:
      #      past_price =pyupbit.get_ohlcv(answer, interval="minute1", to=full_time_replace, count=1).open[0]
       #     break 
        #except AttributeError:
         #   print("해당 시점에 해당 코인이 존재하지 않았거나 기록이 없습니다.")
    
    
    #nowDatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tz= pytz.timezone('Asia/Seoul')
    time_now = datetime.datetime.now(tz)
    nowDatetime = time_now.strftime('%Y-%m-%d %H:%M:%S')
    #print(time_now)
    
    if current_price > past_price:
        a = abs(current_price - past_price)
        b = (round((current_price-past_price)*100/past_price, 2))
        price_up =  {
                    "version": "2.0",
                    "template": {
                    "outputs": [
                         {
                        "itemCard": {
                            "imageTitle": {
                            "title": "가격 상승"
                            
                    },
                    "profile": {
                        "title": f'{answer[0][2]}',
                        "imageUrl": f"https://static.upbit.com/logos/{coin_id}.png"
                    },
                    "itemList": [
                        {
                            "title": "현재 가격",
                            "description": f'{current_price}'
                        },
                        {
                            "title": "비교 가격",
                            "description": f'{past_price}'
                        },
                        {
                            "title": "현재 시간",
                            "description": f'{nowDatetime}'
                        },
                        {
                            "title": "비교 시간",
                            "description": f'{full_time_T}'
                        },
                        {
                            "title": "변동량",
                            "description": f"{a}"
                        },
                        {
                            "title": "변동량(%)",
                            "description": f"{b}%"
                        }
                    ],
                    "itemListAlignment" : "right",
                    "buttons": [
                        {
                            "label": "업비트 차트 보기",
                            "action": "webLink",
                            "webLinkUrl": f"https://upbit.com/exchange?code=CRIX.UPBIT.{ticker}"
                        }
                    ],
                    "buttonLayout" : "vertical"
                }
            }
        ]
    }
}
        return  jsonify(price_up)
    elif current_price == past_price:
        price_now =  {
                    "version": "2.0",
                    "template": {
                    "outputs": [
                         {
                        "itemCard": {
                            "imageTitle": {
                            "title": "가격 변동 없음 "
                            
                    },
                    "profile": {
                        "title": f'{answer[0][2]}', 
                        "imageUrl": f"https://static.upbit.com/logos/{coin_id}.png"
                    },
                    "itemList": [
                        {
                            "title": "현재 가격",
                            "description": f'{current_price}'
                        },
                        {
                            "title": "비교 가격",
                            "description": f'{past_price}'
                        },
                        {
                            "title": "현재 시간",
                            "description": f'{nowDatetime}'
                        },
                        {
                            "title": "비교 시간",
                            "description": f'{full_time_T}'
                        },
                        {
                            "title": "변동량",
                            "description": f"{a}"
                        },
                        {
                            "title": "변동량(%)",
                            "description": f"{b}%"
                        }
                    ],
                    "itemListAlignment" : "right",
                    "buttons": [
                        {
                            "label": "업비트 차트 보기",
                            "action": "webLink",
                            "webLinkUrl": f"https://upbit.com/exchange?code=CRIX.UPBIT.{ticker}"
                        }
                    ],
                    "buttonLayout" : "vertical"
                }
            }
        ]
    }
}
        return  jsonify(price_now)
    else:
        a = abs(current_price - past_price)
        b = (round((current_price-past_price)*100/past_price, 2))
        price_down =  {
                    "version": "2.0",
                    "template": {
                    "outputs": [
                         {
                        "itemCard": {
                            "imageTitle": {
                            "title": "가격 하락"
                           
                    },
                    "profile": {
                        "title": f'{answer[0][2]}',
                        "imageUrl": f"https://static.upbit.com/logos/{coin_id}.png"
                    },
                    "itemList": [
                        {
                            "title": "현재 가격",
                            "description": f'{current_price}'
                        },
                        {
                            "title": "비교 가격",
                            "description": f'{past_price}'
                        },
                        {
                            "title": "현재 시간",
                            "description": f'{nowDatetime}'
                        },
                        {
                            "title": "비교 시간",
                            "description": f'{full_time_T}'
                        },
                        {
                            "title": "변동량",
                            "description": f"{a}"
                        },
                        {
                            "title": "변동량(%)",
                            "description": f"{b}"
                        }
                    ],
                    "itemListAlignment" : "right",
                    "buttons": [
                        {
                            "label": "업비트 바로가기",
                            "action": "webLink",
                            "webLinkUrl": f"https://upbit.com/exchange?code=CRIX.UPBIT.{ticker}"
                        }
                    ],
                    "buttonLayout" : "vertical"
                }
            }
        ]
    }
}
        return  jsonify(price_down)
    

@app.route('/searchnews',methods=['POST'])
def searchnews():
    

    dataReceive = request.get_json()
    print(dataReceive)
    search_name = dataReceive['action']['clientExtra']['key']
    query = quote(search_name )

    news_num = 5

    news_url = f'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={query}'

    req = requests.get(news_url)
    soup = BeautifulSoup(req.text, 'html.parser')

    news_dict = {} 
    idx = 0 
    #cur_page = 1

    while idx < news_num:
    ### 네이버 뉴스 웹페이지 구성이 바뀌어 태그명, class 속성 값 등을 수정함(20210126) ###
        
        table = soup.find('ul',{'class' : 'list_news'})
        li_list = table.find_all('li', {'id': re.compile('sp_nws.*')})
        area_list = [li.find('div', {'class' : 'news_area'}) for li in li_list]
        a_list = [area.find('a', {'class' : 'news_tit'}) for area in area_list]
        
        for n in a_list[:min(len(a_list), news_num-idx)]:
            news_dict[idx] = {'title' : n.get('title'),
                              'url' : n.get('href') }
            idx += 1

        #cur_page += 1
        
        #pages = soup.find('div', {'class' : 'sc_page_inner'})
        #next_page_url = [p for p in pages.find_all('a') if p.text == str(cur_page)][0].get('href')
        
        #req = requests.get('https://search.naver.com/search.naver' + next_page_url)
        #soup = BeautifulSoup(req.text, 'html.parser')


    news_df = DataFrame(news_dict)

    title = []
    url = []
    i = 0
    for i in range(len(news_dict)):
      title.append(news_df.loc['title'][i])
      url.append(news_df.loc['url'][i])
    #print(title)


    
    
    imgurl = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query='
    imgurl = imgurl + query
    
    #print(imgurl)
    req = urllib.request.Request(imgurl)
    #print(req)
    res = urllib.request.urlopen(imgurl).read()  # 여기가 문제에요, 고쳤어요 -> url 형식으로 바꿔주었어요 (quote)
    #print('res:' ,res)
    
    soup = BeautifulSoup(res,'html.parser')
    soup = soup.find_all("a",class_="dsc_thumb")
    #print(soup)
    #print(soup[0])
    #print
    imgUrl = []
    for i in range(len(soup)):
      imgUrl.append(soup[i].find("img")["src"])

    #img = []
    #for i in range(5):
    #  img.append(imgUrl[i])
      
    responseBody = {"version": "2.0",
                "template": {
                "outputs": [
                {
                    "carousel": {
                    "type":"listCard",
                    "items": [
                        {
                        "header": {
                        "title": f"{search_name} 소식"
                        },
              "items": [
                {
                "title": f"{title[0]}",
                "imageUrl": f"{imgUrl[0]}",
                "link": {
                  "web": f"{url[0]}"
                        }
                },
                {
                  "title": f"{title[1]}",
                  "imageUrl": f"{imgUrl[1]}",
                  "link": {
                    "web": f"{url[1]}"
                  }
                },
                {
                  "title": f"{title[2]}",
                 "imageUrl": f"{imgUrl[2]}"  ,             
                  "link": {
                    "web": f"{url[2]}"
                  }
                },
                {
                  "title": f"{title[3]}",
                  "imageUrl": f"{imgUrl[3]}",
                  "link": {
                    "web": f"{url[3]}"
                  }
                },
                {
                  "title": f"{title[4]}",
                  "imageUrl": f"{imgUrl[4]}",      
                  "link": {
                    "web": f"{url[4]}"
                  }
              }
              ],
                "buttons": [
            {
              "label": "더 보기",
              "action": "webLink",
              "webLinkUrl": f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={search_name}"
            }
                
              ]
                  }
              ]  
          }
        }
        ]
        }
        }
    return responseBody




@app.route('/basic',methods=['POST'])
def sayHello():
    #body = request.get_json()
    #print(body)
    #print(body['userRequest']['utterance'])


    query = "비트코인|가상화폐|가상자산|이더리움"
    query = query.replace(' ', '+') 

    news_num = 5

    news_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8%7C%EC%9D%B4%EB%8D%94%EB%A6%AC%EC%9B%80%7C%EA%B0%80%EC%83%81%ED%99%94%ED%8F%90%7C%EA%B0%80%EC%83%81%EC%9E%90%EC%82%B0'
                
    req = requests.get(news_url.format(query))
    soup = BeautifulSoup(req.text, 'html.parser')

    news_dict = {} 
    idx = 0 
    #cur_page = 1

    while idx < news_num:
    ### 네이버 뉴스 웹페이지 구성이 바뀌어 태그명, class 속성 값 등을 수정함(20210126) ###
        
        table = soup.find('ul',{'class' : 'list_news'})
        li_list = table.find_all('li', {'id': re.compile('sp_nws.*')})
        area_list = [li.find('div', {'class' : 'news_area'}) for li in li_list]
        a_list = [area.find('a', {'class' : 'news_tit'}) for area in area_list]
        
        for n in a_list[:min(len(a_list), news_num-idx)]:
            news_dict[idx] = {'title' : n.get('title'),
                              'url' : n.get('href') }
            idx += 1

        


    news_df = DataFrame(news_dict)

    title = []
    url = []
    i = 0
    for i in range(len(news_dict)):
      title.append(news_df.loc['title'][i])
      url.append(news_df.loc['url'][i])
    #print(title)


    
    
    imgurl = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8%7C%EC%9D%B4%EB%8D%94%EB%A6%AC%EC%9B%80%7C%EA%B0%80%EC%83%81%ED%99%94%ED%8F%90%7C%EA%B0%80%EC%83%81%EC%9E%90%EC%82%B0'
    req = urllib.request.Request(imgurl)
    res = urllib.request.urlopen(imgurl).read()
    
    soup = BeautifulSoup(res,'html.parser')
    soup = soup.find_all("a",class_="dsc_thumb")
    #print(soup[0])
    #print
    imgUrl = []
    for i in range(len(soup)):
      imgUrl.append(soup[i].find("img")["src"])

    #img = []
    #for i in range(5):
    #  img.append(imgUrl[i])
      
    responseBody = {"version": "2.0",
                "template": {
                "outputs": [
                {
                    "carousel": {
                    "type":"listCard",
                    "items": [
                        {
                        "header": {
                        "title": "가상화폐 연관 뉴스 보러가기"
                        },
              "items": [
                {
                "title": f"{title[0]}",
                "imageUrl": f"{imgUrl[0]}",
                "link": {
                  "web": f"{url[0]}"
                        }
                },
                {
                  "title": f"{title[1]}",
                  "imageUrl": f"{imgUrl[1]}",
                  "link": {
                    "web": f"{url[1]}"
                  }
                },
                {
                  "title": f"{title[2]}",
                 "imageUrl": f"{imgUrl[2]}"  ,             
                  "link": {
                    "web": f"{url[2]}"
                  }
                },
                {
                  "title": f"{title[3]}",
                  "imageUrl": f"{imgUrl[3]}",
                  "link": {
                    "web": f"{url[3]}"
                  }
                },
                {
                  "title": f"{title[4]}",
                  "imageUrl": f"{imgUrl[4]}",      
                  "link": {
                    "web": f"{url[4]}"
                  }
              }
              ],
                "buttons": [
            {
              "label": "더 보기",
              "action": "webLink",
              "webLinkUrl": "https://search.naver.com/search.naver?where=news&sm=tab_jum&query=비트코인%7C이더리움%7C가상화폐%7C가상자산"
            }
                
              ]
                  }
              ]  
          }
        }
        ]
        }
        }
    return responseBody







@app.route('/youtube',methods=['POST'])
# 모듈 설치
#pip install --upgrade google_api_python_client
#pip install oauth2client

# 모듈 import 단
#from googleapiclient.discovery import build
#from googleapiclient.errors import HttpError
#from oauth2client.tools import argparser

# 모듈을 requirements 에 추가해줘야 heroku deploy가 작동한다.
# google_api_python_client==2.48.0
# oauth2client==4.1.3

def sayHello1():
    #body1 = request.get_json()
    #print(body1)
    #print(body1['userRequest']['utterance'])

# https://console.cloud.google.com/apis/credentials 여기서 API발급받아 사용
    DEVELOPER_KEY='AIzaSyBa_S65tRPb1mALqTtsDB1e9p6s-7kshJA' # 내 API 키값 입력
    YOUTUBE_API_SERVICE_NAME='youtube'
    YOUTUBE_API_VERSION='v3'

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                            developerKey = DEVELOPER_KEY)

    search_response=youtube.search().list(
        q="비트코인",
        
        part='id, snippet',
        maxResults=5,
        ).execute()
    print(search_response)
    search_title = []
    search_url = []
    thumb_img = []
    for i in range (5):
        search_title.append(search_response['items'][i]['snippet']['title'])
        search_url.append('https://youtube.com/watch?v='+ search_response['items'][i]['id']['videoId'])
        thumb_img.append(search_response['items'][i]['snippet']['thumbnails']['default']['url'])
    print(thumb_img)  
   
    responseBody1 = {"version": "2.0",
                      "template": {
                      "outputs": [
                      {
                          "carousel": {
                          "type":"listCard",
                          "items": [
                              {
                              "header": {
                              "title": "비트코인 영상 보러가기"
                              },
                    "items": [
                      {
                      "title": f"{search_title[0]}",
                      "imageUrl": f"{thumb_img[0]}",  
                      "link": {
                        "web": f"{search_url[0]}"
                              }
                      },
                      {
                        "title": f"{search_title[1]}",
                       "imageUrl": f"{thumb_img[1]}", 
                        "link": {
                          "web": f"{search_url[1]}"
                        }
                      },
                      {
                        "title": f"{search_title[2]}",
                      "imageUrl": f"{thumb_img[2]}", 
                        "link": {
                          "web": f"{search_url[2]}"
                        }
                      },
                      {
                        "title": f"{search_title[3]}",
                        "imageUrl": f"{thumb_img[3]}", 
                        "link": {
                          "web": f"{search_url[3]}"
                        }
                      },
                      {
                        "title": f"{search_title[4]}",
                        "imageUrl": f"{thumb_img[4]}", 
                        "link": {
                          "web": f"{search_url[4]}"
                        }
                    }
                    ],
                      "buttons": [
                  {
                    "label": "더 보기",
                    "action": "webLink",
                    "webLinkUrl": "https://www.youtube.com/results?search_query=비트코인"
                  }
                      
                    ]
                        }
                    ]  
                }
              }
              ]
              }
              }
    return responseBody1







    