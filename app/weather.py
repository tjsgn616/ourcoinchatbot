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

def msg():
    dataReceive = request.get_json()
    
    #namedata2 = namedata
    
    #coin_name = dataReceive["action"]["detailParams"]["coi
    #coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","") # 코인 이름 받기
    coin_name = dataReceive["action"]["params"]["coin"] #.upper.replace(" ","")


    namedata = marketData() # 에반데
    answer = []
    for i in namedata.index:
        if coin_name == namedata.korean_name[i] or coin_name == namedata.english_name[i] or coin_name == namedata.market[i]:
            answer.append([namedata.market[i],namedata.currency[i]])



    full_time = dataReceive["action"]["detailParams"]["datetime"]["origin"] # 시간대 받기
    full_time_replace = full_time.replace("-","").replace("T","").replace(":","")
    full_time_T = full_time.replace("T"," ")
    print(full_time_replace)
    print(coin_name)
    print(answer)
    print(answer[2])
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
msg()