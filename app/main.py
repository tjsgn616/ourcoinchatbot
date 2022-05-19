from flask import Flask, jsonify, request
import pandas as pd
import pyupbit
import requests
app = Flask(__name__) 

@app.route('/msg2', methods=['POST'])
def msg():
    
    dataReceive = request.get_json() # 사용자가 입력한 데이터
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
        english_name.append(namedata['english_name'].lower().replace(" ",""))
        
    tickers=pyupbit.get_tickers()
    namedata= pd.DataFrame((zip(market, korean_name, english_name)), columns = ['market', 'korean_name', 'english_name'])
    
    
    currency = []
    for i in namedata.loc[:,'market']:
        if i.split('-')[0] == "KRW":
            currency.append("KRW")
        elif i.split('-')[0] == "BTC":
            currency.append("BTC")
        else:
            currency.append("USDT")
            
    namedata['currency'] = currency # currency column을 새로 추가
    namedata2 = namedata
    ## 여기까지 데이터 받아오는거..

    coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","")
    #coin_name = dataReceive["action"]["detailparams"]["koreanname"]['value'] # 에반데
#print(namedata2['korean_name'])
    print("coin : " ,coin_name)
    answer = []
#print(namedata2.korean_name[0])
    for i in namedata2.index:
        if coin_name == namedata2.korean_name[i] or coin_name == namedata2.english_name[i]:
            answer.append([namedata2.market[i],namedata2.currency[i]])

    print("1 : ", answer)
    print("len:",len(answer))


    
# answer[여럿나온 답의 순서][0=market code, 1= currency]
#print(answer[:len(answer)][:len(answer)])
    while len(answer) == 0:
        coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","")
        #coin_name = dataReceive["action"]["detailparams"]["koreanname"]['value']
        #coin_name = dataReceive["content"]
        none_ticker = {
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": "일치하는 가상화폐가 존재하지 않습니다. 이름을 다시 확인해주세요 " # f-string 수정
                    }
                }    
            ],
                "quickReplies": [
          {
                "messageText": "이더리움",
                "action": "message",
                "label": "이더리움"
          },
                    
          {
                "messageText": "비트코인",
                "action": "message",
                "label": "비트코인"
          },  
                    
          {
                "messageText": "도지코인",
                "action": "message",
                "label": "도지코인" # 비트코인의 경우 BTC를 어떻게 처리하지
          }
     
]
                }
            }
        return jsonify(none_ticker)
        
        
    if len(answer) != 0 : # 화폐 단위 하나만 있을 때
        selection = []
        for i in range(len(answer)): # 이거 왜 안됨??
            selection.append(answer[i][1])
        #print(selection)
        print("2:" , selection.index("KRW")) # 2
        KRW = selection.index("KRW")
        ticker = answer[KRW][0]
        now_price = { 
            "version":"2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text":  f"{coin_name}" "의 현재 가격은 KRW 기준" f"{pyupbit.get_current_price(ticker):.2f}" "입니다"
                        }
                    }
                ]
            }
        }
        return jsonify(now_price)