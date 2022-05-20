from flask import Flask, jsonify, request, g
import pandas as pd
import pyupbit
import requests
import datetime
app = Flask(__name__) 

@app.route('/msg3', methods=['POST'])

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
    

    #namedata2 = namedata
    
    #coin_name = dataReceive["action"]["detailParams"]["coi
    #coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","") # 코인 이름 받기
    coin_name = dataReceive["action"]["params"]["coin"].replace(" ","") # 에반데
    answer = []
    for i in namedata.index:
        if coin_name == namedata.korean_name[i] or coin_name == namedata.english_name[i] or coin_name == namedata.market[i]:
            answer.append(namedata.market[i][0])

    
    full_time = dataReceive["action"]["detailParams"]["datetime"]["origin"] # 시간대 받기
    full_time_replace = full_time.replace("-","").replace("T","").replace(":","")
    print(full_time_replace)
    print(coin_name)
    print(answer)
   
    while True:
        try:
            past_price =pyupbit.get_ohlcv(answer, interval="minute1", to=full_time_replace, count=1).open[0]
            break 

        except AttributeError:
            print("해당 시점에 해당 코인이 존재하지 않았거나 기록이 없습니다.")
    
    current_price = pyupbit.get_current_price(answer)
    nowDatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    coin = {
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": f'비교 가상 화폐: {answer}' f'현재 시간: {nowDatetime}, 현재 가격: {current_price}'
                        f'비교 시간: {full_time}, 비교 시간 가격: {past_price}'

                         # f-string 수정
                    }
                }    
            ]
                }
    }
    
    if current_price > past_price:
        a = current_price -past_price 
        b = round((current_price-past_price)*100/past_price, 2)

        price_up =  {
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": f'가격 상승 , ' f'변동량: {a} , '  f'변동량: {b}' f'비교 가상 화폐: {answer}' f'현재 시간: {nowDatetime}, 현재 가격: {current_price}'
                        f'비교 시간: {full_time}, 비교 시간 가격: {past_price}'
                        

                         # f-string 수정
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
                "simpleText": {
                "text": f'가격 보합(변화 없음)' f'비교 가상 화폐: {answer}' f'현재 시간: {nowDatetime}, 현재 가격: {current_price}'
                        f'비교 시간: {full_time}, 비교 시간 가격: {past_price}'
                        

                         # f-string 수정
                    }
                }    
            ]
                }
    }
        return  jsonify(price_now)
    else:
        a = past_price-current_price
        b = round((past_price-current_price)*100/current_price, 2)

        price_down =  {
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": f'가격 하락 , ' f'변동량: {a} , '  f'변동량: {b} \n' f'비교 가상 화폐: {coin_name} \t' f'현재 시간: {nowDatetime}, 현재 가격: {current_price}'
                        f'비교 시간: {full_time}, 비교 시간 가격: {past_price}'
                        

                         # f-string 수정
                    }
                }    
            ]
                }
    }
        return  jsonify(price_down)
    