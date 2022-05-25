import pyupbit
import requests
import pandas as pd
import csv
import datetime
#import project_def as pr_d
#import schedule
import time
from flask import Flask, jsonify, request
import json

csv_data = pd.read_csv("./app/top5_coin.csv")
#qwe = pd.read_csv(".app/output.csv")

#print(json.dumps(json_data) )

## 9시 , 2시 , 8시
# https://ddolcat.tistory.com/660
app = Flask(__name__) 
@app.route('/price', methods=['POST'])
def func_9():
    #print(csv_data)
    #dataReceive = request.get_json()
    #full_time = dataReceive["action"]["detailParams"]["datetime"]["origin"]
    #top5_coin = 가영이가 만든 젤 많이 거래된 코인 5개 종류 불러오는거
    nowDatetime = datetime.datetime.now().strftime('%d,%H')
    now_d = nowDatetime.split(',')[0]
    now_h = nowDatetime.split(',')[1]
    pastDatetime = (datetime.datetime.now()+datetime.timedelta(hours=-13)).strftime('%Y,%m%d,%H%M') # -13?
    pastDatetime_YYYY = pastDatetime.split(',')[0]
    pastDatetime_md = pastDatetime.split(',')[1]
    past_d = pastDatetime_md[2:4]
    pastDatetime_HM = pastDatetime.split(',')[2]
    past_h = pastDatetime_HM[0:2]
    # timedelta =() 만큼 이전의 시간 출력
    top5_coins = []
    #for i in csv_data['market']:
    #    top5_coins.append(i)
    #tet = pd.DataFrame(csv_data)
    for i in csv_data['market']:
        top5_coins.append(i)
    #print(top5_coins)
    #for i in top_5_coin_names:      # 위에꺼랑 합칠수 없나? 될거가튼데
    for i in top5_coins:
        current_price =  (pyupbit.get_current_price(i)) #requests.get(f"https://api.upbit.com/v1/ticker?markets={i}")
        time.sleep(0.05)
        past_price_20 = (pyupbit.get_ohlcv(f'{i}', interval="minute60", to=f'{pastDatetime_YYYY}{pastDatetime_md}{pastDatetime_HM}', count=1).open[0])
        time.sleep(0.05)
        sun = [] 
        #coin_id = ''.join(i)
        #coin_id_id = coin_id[4:7]
        past_time2 = 0
        #past_price3 = round(100*(past_price2-past_price1)/past_price1,3)
        #past_price4 = round(100*(current_price-past_price_20)/past_price_20,3)
        for num1 in range(0,26): #[(12,10),(10,8),(8,6),(6,4),(4,2),(2,0)]:#([2,4,6,8,10,12], [0,2,4,6,8,10]:)]
            past_time1 = past_time2
            past_time2 = (datetime.datetime(2022, 5, 25, 8, 00, 00) +datetime.timedelta(hours=+num1) - datetime.timedelta(days = 1)).strftime('%Y%m%d%H%M')
            if past_time1 == 0:
                    continue
            elif past_time1 != 0:
                past_d1 = past_time1[6:8]
                past_H1 = past_time1[8:10]
                #past_price1 = (requests.get(f"https://api.upbit.com/v1/candles/minutes/60?market={i}&to={past_time1}&count=1").open[0])
                past_price1 = (pyupbit.get_ohlcv(f'{i}', interval="minute60", to=f'{past_time1}', count=1).open[0])
                time.sleep(0.05)
                past_price2 = (pyupbit.get_ohlcv(f'{i}', interval="minute60", to=f'{past_time2}', count=1).open[0])
                #past_price2 = (requests.get(f"https://api.upbit.com/v1/candles/minutes/60?market={i}&to={past_time2}&count=1").open[0])
                time.sleep(0.05)
                if past_price2 >= past_price1:
                    #sun.append(past_d1)
                    #sun2.append(past_H1)
                    #sun3.append(past_price1)
                    #sun4.append(round(100*(past_price2-past_price1)/past_price1,3))
                    #print(past_d1,'일',past_H1,'시: ',past_price1,round(100*(past_price2-past_price1)/past_price1,3), '%, 맑음')
                    sun5 = (past_d1,'일',past_H1,'시: ',past_price1,round(100*(past_price2-past_price1)/past_price1,3), '%, 맑음')
                    sun.append(sun5)
                    
                else:
                    #cloud.append(past_d1)
                    #cloud2.append(past_H1)
                    #cloud3.append(past_price1)
                    #cloud4.append(round(100*(past_price2-past_price1)/past_price1,3))

                    #print(past_d1,'일',past_H1,'시',past_price1,round(100*(past_price2-past_price1)/past_price1,3), '%, 흐림')
                    cloud5 = (past_d1,'일',past_H1,'시:',past_price1,round(100*(past_price2-past_price1)/past_price1,3),'%, 흐림')
                    sun.append(cloud5)
        print(sun)
        sunpd = pd.DataFrame(sun)
        if current_price >= past_price_20:

            test =  {
                    "version": "2.0",
                    "template": {
                    "outputs": [
                    {
                    "simpleText": {
                    "text": f"{sunpd}" 
                }
            }
        ]
    }
        }       
                    
            #print(past_d,'일',past_h,'시 ->',now_d,'일',now_h,'시 :',past_price_20,'->''\033[31m',current_price, round(100*(current_price-past_price_20)/past_price_20,3),'% 20~ 09 날씨는 맑음''\033[0m')
        else:
            #print(past_d,'일',past_h,'시 ->',now_d,'일',now_h,'시 :',past_price_20,'->''\033[34m',current_price, round(100*(current_price-past_price_20)/past_price_20,3),'% 20~ 09 날씨는 흐림''\033[0m')
            test = {
                    "version": "2.0",
                    "template": {
                    "outputs": [
                    {
                    "simpleText": {
                    "text": f"{sunpd}"
                }
            }
        ]
    }
        }       
        return (test)
    

#func_9()
#func_14()
#func_20()