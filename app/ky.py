from flask import Flask, jsonify, request, g
import pandas as pd
import pyupbit
import requests
import datetime

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
    

    #namedata2 = namedata
    
    #coin_name = dataReceive["action"]["detailParams"]["coi
    #coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","") # 코인 이름 받기
    coin_name = dataReceive["action"]["params"]["coin"].replace(" ","") # 에반데
    answer = []
    for i in namedata.index:
        if coin_name == namedata.korean_name[i] or coin_name == namedata.english_name[i] or coin_name == namedata.market[i]:
            answer.append([namedata.market[0][0]])
    print(answer)

    
    
   
    
    