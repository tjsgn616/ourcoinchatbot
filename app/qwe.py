import pyupbit
#import requests
import pandas as pd
#import json
import datetime 
#import project_def as pr_d
import time
#import test as ts
#import csv
#import sys
## 9시 , 2시 , 8시
# https://ddolcat.tistory.com/660
#sys.stdout = open('output.csv','w')
#qwe = pd.read_csv('output.csv')
def func_9():
    nowDatetime = datetime.datetime.now().strftime('%d,%H')
    #top5_coin = 가영이가 만든 젤 많이 거래된 코인 5개 종류 불러오는거  nowDatetime = datetime.datetime.now()
    now_d = nowDatetime.split(',')[0]
    now_h = nowDatetime.split(',')[1]
    pastDatetime = (datetime.datetime.now()+datetime.timedelta(hours=-13)).strftime('%Y,%m%d,%H%M')
    pastDatetime_YYYY = pastDatetime.split(',')[0]
    pastDatetime_md = pastDatetime.split(',')[1]
    past_d = pastDatetime_md[2:4]
    pastDatetime_HM = pastDatetime.split(',')[2]
    past_h = pastDatetime_HM[0:2]
    sun = []
    # timedelta =() 만큼 이전의 시간 출력
    top5_coins = []
    for i in pd.read_csv('top5_coin.csv')['market']:
        top5_coins.append(i)
    #for i in range(len(top5_coin)):
    #    top_5_coin_names.append(top5_coin['market'])
    #for i in top_5_coin_names:      # 위에꺼랑 합칠수 없나? 될거가튼데
    for i in top5_coins:
        current_price = (pyupbit.get_current_price(i))
        time.sleep(0.05)
        past_price_20 = (pyupbit.get_ohlcv(f'{i}', interval="minute60", to=f'{pastDatetime_YYYY}{pastDatetime_md}{pastDatetime_HM}', count=1).open[0])
        time.sleep(0.05)
        #print(i)
        sun.append(i)
        sun2 = [] 
        sun3 = [] 
        sun4 = []
        sun5 = [] 
        sun6 = []
        #cloud2 = [] 
        #cloud3 = [] 
        #cloud4= []
        past_time2 = 0
        for num1 in range(0,26): #[(12,10),(10,8),(8,6),(6,4),(4,2),(2,0)]:#([2,4,6,8,10,12], [0,2,4,6,8,10]:)]
            past_time1 = past_time2
            #test = datetime(2022, 5, 25, 9, 00, 00)
            #past_time2 = dat +datetime.timedelta(hours=+num1) - datetime.timedelta(days = 1)).strftime('%Y%m%d%H%M')
            past_time2 = (datetime.datetime(2022, 5, 25, 8, 00, 00) +datetime.timedelta(hours=+num1) - datetime.timedelta(days = 1)).strftime('%Y%m%d%H%M')
            #print(past_time2)
            
            if past_time1 == 0:
                continue
            elif past_time1 != 0:
                past_d1 = past_time1[6:8]
                past_H1 = past_time1[8:10]
                past_price1 = (pyupbit.get_ohlcv(f'{i}', interval="minute60", to=f'{past_time1}', count=1).open[0])
                time.sleep(0.05)
                past_price2 = (pyupbit.get_ohlcv(f'{i}', interval="minute60", to=f'{past_time2}', count=1).open[0])
                time.sleep(0.05)
                
                if past_price2 >= past_price1:
                    sun2.append(past_d1)
                    sun3.append(past_H1)
                    sun4.append(past_price1)
                    sun5.append(round(100*(past_price2-past_price1)/past_price1,3))
                    sun6.append('맑음')
                    
                    #print(past_d1,'일',past_H1,'시: ',past_price1,round(100*(past_price2-past_price1)/past_price1,3), '%, 맑음')
                    sun10 = i,past_d1,'일',past_H1,'시: ',past_price1,round(100*(past_price2-past_price1)/past_price1,3), '%, 맑음'
                    sun.append(sun10)
                    
                else:
                    sun2.append(past_d1)
                    sun3.append(past_H1)
                    sun4.append(past_price1)
                    sun5.append(round(100*(past_price2-past_price1)/past_price1,3))
                    sun6.append('흐림')

                    #print(past_d1,'일',past_H1,'시',past_price1,round(100*(past_price2-past_price1)/past_price1,3), '%, 흐림')
                    cloud5 = i,past_d1,'일',past_H1,'시: ',past_price1,round(100*(past_price2-past_price1)/past_price1,3), '%, 흐림'
                    sun.append(cloud5)
                    
            #print(sun2)
            #print(cloud2)
        if current_price >= past_price_20:
            
            sun7 = past_d,'일',past_h,'시', '->',now_d,'일',now_h,'시',past_price_20,'->',current_price, round(100*(current_price-past_price_20)/past_price_20,3),'%, 20 ~ 09 날씨는 맑음'
            sun.append(sun7)
        else:
            
            sun8 = past_d,'일',past_h,'시','->',now_d,'일',now_h,'시',past_price_20,'->',current_price, round(100*(current_price-past_price_20)/past_price_20,3),'%,20 ~ 09 날씨는 흐림'
            sun.append(sun8)
    #print("테스트")
    #print(sun[1][0])
    #print(sun[1][1])
    #print(sun[1][2])
    #print(sun[1][9])
    #
    print(sun[133][3]) # 데이터를 가져오는데 시간이 오래걸림.. 리스트 셀렉션 + 터플 셀렉션 조합 + 파이썬 파일 불러오기 조합으로 가면 되지 않을까
    # 생각함  # 데이터 파일을 주기적으로 만드는 것은 heroku 서버의 스케줄러를 이용하면 가능할 것으로 보임
    # 어떻게 JSON 형태를 스케줄러로 출력하는거지? 그것만 따로 다른 언어로 만들어야 하나 고민됨
func_9()
#func_14()
#func_20()
