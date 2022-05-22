from crypt import methods
from os import name
from select import select
from flask import Flask, jsonify, request
import pandas as pd
import pyupbit
import requests



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
    return namedata




app = Flask(__name__)
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
                                        }
                                    ],
                                    "buttons": [
                                        {
                                        "label": "더 많은 코인 조회하기",
                                        "action": "block",
                                        "blockId": "6284847275eca02fba63ab96"
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

    # 
    answer = []
    for i in nameData.index:
        if coin == nameData.korean_name[i] or coin == nameData.english_name[i] or coin == nameData.market[i]:
            answer.append([nameData.market[i],nameData.currency[i]])

    print("---list----",answer)
    # 전체 마켓 시장에서 입력한 코인과 같은 종류의 코인 뽑아서 리스트로 반환 (KRW, BTC,USDT)
    # 코인 외 잘못 발화된 값은 coin_now =[]로 빈 리스트 추출
    # 다양한 입력 형태 다 포용한다.
    name_list = nameData.values.tolist()
    coin_now = []
    for i in range(len(name_list)):
        if coin in name_list[i]:
            coin_now.extend(name_list[i])
    print("---coin_name----",coin_now)
    coin_now = set(coin_now)
    print("----no 중복 코인 ----",coin_now)

    # 해당 코인의 화폐 시장 종류 뽑아내서 리스트로 반환 ->selection ['KRW','BTC','USDT] 형태
    # 잘못된 발화인 경우 selection =[] 빈 리스트 추출
    selection = []
    for i in range(len(answer)):
        selection.append(answer[i][1])


    if coin not in coin_now:
        # coin_error = {
        #         "version": "2.0",
        #         "template": {
        #             "outputs": [
        #                 {
        #                     "simpleText":{
        #                         "text":"존재하지 않는 가상화폐입니다. \n 다시 시도해 주세요. \n\n"
        #                     }
        #                 }
        #             ]
        #         }
        #     }
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
                                    "label":"시세 조회로 돌아가기",
                                    "blockId": "627a430245b5fc3106459cab",
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
                print("한국 돈 변환 값 BTC : ",coin_price)
            else : 
                ticker = answer[0][0]
                coin_money = pyupbit.get_current_price(ticker)
                coin_price = (USD * coin_money)
                print("한국 돈 변환 값 USDT : ",coin_price)
        else:
            print("KRW 인덱스 값 KRW:" , selection.index("KRW"))
            KRW = selection.index("KRW")
            ticker = answer[KRW][0]
            coin_price = pyupbit.get_current_price(ticker)

        coin_price_now = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": f"{coin}의 현재 가격은 KRW 기준 {coin_price:.2f}원 입니다" #link 넣으면 좋을 듯
                            }
                        }
                    ]
                }
            }
        return coin_price_now
