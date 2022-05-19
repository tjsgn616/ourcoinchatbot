from flask import Flask, jsonify, request, g
import pandas as pd
import pyupbit
import requests
app = Flask(__name__) 

@app.route('/msg', methods=['POST'])
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
    

    coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","")
    #coin_name = dataReceive["action"]["detailparams"]["koreanname"]['value'] # 에반데
#print(namedata2['korean_name'])
    answer = []
#print(namedata2.korean_name[0])
    for i in namedata2.index:
        if coin_name == namedata2.korean_name[i] or coin_name == namedata2.english_name[i]:
            answer.append([namedata2.market[i],namedata2.currency[i]])


    
# answer[여럿나온 답의 순서][0=market code, 1= currency]
#print(answer[:len(answer)][:len(answer)])
    while len(answer) == 0:
        
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
                "label": "도지코인" 
          }
     
]
                }
            }
        
        
        coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","")
#print(namedata2['korean_name'])
        answer = []

#print(namedata2.korean_name[0])
        for i in namedata2.index:
            if coin_name == namedata2.korean_name[i] or coin_name == namedata2.english_name[i]:
                answer.append([namedata2.market[i],namedata2.currency[i]])
                print("여기 되는건가?")
        return jsonify(none_ticker)       
    
    if len(answer) == 0 # 화폐 단위 하나만 있을
    #print(answer)
        ticker = answer[0][0]

        
        now_price = {
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": f"{coin_name}" "의 현재 가격은" f"{answer[0][1]}" "기준" f"{pyupbit.get_current_price(ticker):.3f}" "입니다" # f-string 수정
                    }
                }    
            ]
                }
            }
        
             # 문제점 : BTC는 소수점을 엄청 길게 표시하는데, 원화와 같은 소수점으로 표시하면 안된다. 
        return jsonify(now_price)
    
    
    elif len(answer) == 2: # 화폐 단위 2개 있을 때
        #print(answer)
        selection = []
        for i in range(len(answer)): # 이거 왜 안됨??
            selection.append(answer[i][1])
        #print(selection)

        manycurrency2 = {
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": "기준 화폐가 다수 존재합니다" f"{selection}" 
                    }
                }    
            ],
                    
                "quickReplies": [
          {
                "action": "block",
                "label": f"{selection[0]}",
                "blockId" : "6284847275eca02fba63ab96"
                

          },
                    
          {
                
                "action": "block",
                "label": f"{selection[1]}",
                "blockId" : "6284847275eca02fba63ab96"


          }
     
]
                }
            }
        
        return  jsonify(manycurrency2)
    
    else: # 화폐 단위 3개
        selection = []
        for i in range(len(answer)): 
            selection.append(answer[i][1])
        #print(selection)
        manycurrency = {
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": "기준 화폐가 다수 존재합니다" f"{selection}" 
                    }
                }    
            ],
                    
                "quickReplies": [
          {
                "messageText": f"{selection[0]}",
                "action": "block",
                "label": "6284847275eca02fba63ab96"
          },
                    
          {
                "messageText": f"{selection[1]}",
                "action": "message",
                "label": f"{selection[1]}"
          },
          {
                "messageText": f"{selection[2]}",
                "action": "message",
                "label": f"{selection[2]}"
          }
        
]
             }
            }
        dataReceive = request.get_json()

        # return jsonify(manycurrency)

        test_j = {
            
            "version" : "2.0",
            "data" : {
                "coin" : f"{coin_name}",
                "money" : f"{selection[0]}",
                "price" : f"{pyupbit.get_current_price(ticker):.3f}"
            }
            
            }
        
        return jsonify(manycurrency)
#스킬 + 함수로 블록 분리
@app.route('/abc', methods=['POST'])
def abc() :
    dataReceive = request.get_json()
    cur_sel = dataReceive["userRequest"]["utterance"] # 밑에 
    n = g.selection.index(cur_sel) # 비트코인입력했을때, KRW OR BTC 
    ticker = g.answer[n][0]
    abc = { "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": f"{g.coin_name}" "의 현재 가격은" f"{g.answer[n][1]}" "기준" f"{pyupbit.get_current_price(ticker):.3f}" "입니다"
                    }
                }    
            ]
                }
            }
    return jsonify(abc)

      
        #cur_sel = dataReceive["userRequest"]["utterance"]
        #if cur_sel == "KRW" or "BTC" or "USDT" :
        #cur_sel = "KRW"    
          # 일반 발화 안됨
        #cur_sel = dataReceive["action"]["clientExtra"] # 바로가기 응답 받아오는 코드 안됨
        #cur_sel = dataReceive["action"]["params"]["currency"]["value"]
        #cur_sel = dataReceive["quickReplies"]["messageText"]
        #cur_sel = dataReceive["quickReplies"]["messageText"]
        #cur_sel = dataReceive["userRequest"]["utterance"].upper()
        #cur_sel = dataReceive["quickReplies"]["action"]["message"]
