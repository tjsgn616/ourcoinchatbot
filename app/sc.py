from operator import itemgetter
import re
import requests
import pandas as pd
import time
#import schedule
def si():
    # 누적 거래량 탑 5 구하기 위해 market id 불러오기
    market_list = pd.read_csv("./app/market_list.csv")
    market_list = market_list['market']
    market_list = market_list.values.tolist()
    c = len(market_list)
    # 전체 코인의 1 시간 누적 거래량 구하기 (candle 조회)
    all_response = []
    for i in range(c):
        market = market_list[i]
        # print(market)
        all_url = (f"https://api.upbit.com/v1/candles/minutes/60?market={market}&count=1")
        all_headers = {"Accept": "application/json"}
        time.sleep(0.1)
        a = requests.get(all_url, headers=all_headers).json()
        if market == "BTC-LUNA":
            continue
        all_response.extend(a)
        # print(type(all_response[i]),i,market)
    time.sleep(0.1)
    top_acc_val = pd.DataFrame(all_response)
    #top_acc_val.columns=['market','acc_trade_volume','change_rate']
    top_acc_val.to_csv("./app/data/top_acc.csv",index=True, header = True)
    # 전체 코인의 현재 시세 변동률 (현재 조회)
si()