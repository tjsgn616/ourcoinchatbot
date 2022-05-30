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
###### 

## /acc 
## 실시간 top 5

#####


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







