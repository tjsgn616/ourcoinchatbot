from flask import Flask, jsonify, request, g
import pandas as pd
import pyupbit
import requests
import datetime

def marketData():
     # 사용자가 입력한 데이터
    #print(dataReceive)
    marketData = requests.get('https://api.upbit.com/v1/market/all') # API 그냥 쓰면 되는듯
    if marketData.status_code == 200 :
        jsonMarket = marketData.json()
        
    market = []
    korean_name = []
    english_name = []
    for i in range(len(jsonMarket)) :
        namedata = jsonMarket[i]
        market.append(namedata['market'])
        korean_name.append(namedata['korean_name'])
        english_name.append(namedata['english_name'].upper().replace(" ",""))
        
    
    namedata= pd.DataFrame((zip(market, korean_name, english_name)), columns = ['market', 'korean_name', 'english_name'])
    
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
@app.route('/msg5', methods=['POST'])
def msg():
    dataReceive = request.get_json()
    
    #namedata2 = namedata
    
    #coin_name = dataReceive["action"]["detailParams"]["coi
    #coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","") # 코인 이름 받기
    coin_name = dataReceive["action"]["params"]["coin"] #.upper.replace(" ","")


    namedata = marketData() # 에반데
    answer = []
    id = []
    for i in namedata.index:
        if coin_name == namedata.korean_name[i] or coin_name == namedata.english_name[i] or coin_name == namedata.market[i]:
            answer.append([namedata.market[i],namedata.currency[i]])

    
    full_time = dataReceive["action"]["detailParams"]["datetime"]["origin"] # 시간대 받기
    full_time_replace = full_time.replace("-","").replace("T","").replace(":","")
    full_time_T = full_time.replace("T"," ")
    print(full_time_replace)
    print(coin_name)
    print(answer)

    USD = requests.get('https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD')
    USD = USD.json()
    USD = USD[0]['basePrice'] #USDT 가격 조회를 위함.





    name_list = namedata.values.tolist()
    coin_now = []
    for i in range(len(name_list)):
        if coin_name in name_list[i]:
            coin_now.extend(name_list[i])
    print("---coin_name----",coin_now) 
    coin_id = ''.join(coin_now[0])
    print(coin_id)
    coin_id_id = coin_id[4:7]
    print(coin_id_id)
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
                                    #"messageText":"짜잔!"
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
            #print("KRW 인덱스 값 KRW:" , selection.index("KRW"))
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
    
    
    nowDatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if current_price > past_price:
        a = abs(current_price - past_price)
        b = abs(round((current_price-past_price)*100/past_price, 2))

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
                        "title": f'{ticker}',
                        "description": "가격 상승",
                        "imageUrl": f"https://static.upbit.com/logos/{coin_id_id}.png"
                    },
                    "itemList": [
                        {
                            "title": "현재 가격",
                            "description": f'{current_price}'
                        },
                        {
                            "title": "비교 시간 가격",
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
                        "title": f'{ticker}',
                        "imageUrl": f"https://static.upbit.com/logos/{coin_id_id}.png"
                    },
                    "itemList": [
                        {
                            "title": "현재 가격",
                            "description": f'{current_price}'
                        },
                        {
                            "title": "비교 시간 가격",
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
        a = current_price - past_price
        b = round((current_price-past_price)*100/past_price, 2)

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
                        "title": f'{ticker}',
                        "imageUrl": f"https://static.upbit.com/logos/{coin_id_id}.png"
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