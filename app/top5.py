from operator import itemgetter
import requests
import pandas as pd
import time



def si():
    # 탑 5 구하기 위해 market id 불러오기
    market_list = pd.read_csv("./app/data/market_list.csv")
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

    # 전체 코인의 현재 시세 변동률 (현재 조회)
    all_res_pct = []
    for i in range(c):
        market = market_list[i]
        all_url = (f"https://api.upbit.com/v1/ticker?markets={market}")
        time.sleep(0.1)
        all_headers = {"Accept": "application/json"}
        a = requests.get(all_url, headers=all_headers).json()
        if market == "BTC-LUNA":
            continue
        all_res_pct.extend(a)

    # 변동률 탑 5 정렬
    top_coin_ch = sorted(all_res_pct,key=itemgetter('change_rate'),reverse=True)




    # 1시간 변동률 탑 5 (매 정각으로 부터)
    # -> 불가 업비트 자체에서 1시간 정각 기준으로 데이터를 보내준다.
    # 매 정각 기준 지금까지의 데이터 값 추출
    # 위 기준 매 정각부터 해서 시가, 고가, 저가, 종가 추출
    # print(all_response[0])
    # print("=====================\n",all_res_pct[0])
    live_market = []
    base_time = []
    live_rate = []
    live_rate_str = []
    for i in range(c): 
        live_market.append(all_response[i]['market'])
        base_time.append(all_response[i]['candle_date_time_kst'])
        #  변동률 구해서 추가
        hour_price = all_response[i]['opening_price']
        trade_price = all_response[i]['trade_price']
        # 절대값으로 저장
        live_rate.append(abs(round((trade_price - hour_price) / hour_price * 100,2)))
        if round((trade_price - hour_price) / hour_price * 100,2) > 0 :
            live_rate_str.append("상승")
        elif round((trade_price - hour_price) / hour_price * 100,2) < 0 :
            live_rate_str.append("하락")
        else:
            live_rate_str.append("보합")


    #  합치고 정렬
    live_coin = list(zip(live_market,base_time,live_rate,live_rate_str))
    # print(type(live_coin[0]))
    live_coin.sort(key=lambda x: x[2], reverse=True)
    live_coin = live_coin[:5]
    print("정각 기준 실시가 변동률 탑 5")
    print(live_coin)
    # live_coin = pd.DataFrame(live_coin)
    # live_coin.columns=['market','base_time','live_rate','live_rate_str']
    # live_coin.to_csv("./app/data/live_top.csv",index=True, header=True)


    # 전일 대비 변동률 탑 5
    ch_market = []
    ch_rate = []
    ch_rate_str = []
    for i in range(5):
        ch_market.append(top_coin_ch[i]['market'])
        ch_rate.append(round(top_coin_ch[i]['change_rate']*100,2))
        if top_coin_ch[i]['change'] == "RISE":
            ch_rate_str.append("상승")
        elif top_coin_ch[i]['change'] == "FALL":
            ch_rate_str.append("하락")
        else:
            ch_rate_str.append("보합")
    
        
    top_change_val = list(zip(ch_market,ch_rate,ch_rate_str))
    # top_dict_change = dict(zip(top_market_ch,top_change_val))

    print("시세 변동률 탑 5 (전일대비 실시간)")
    print(top_change_val)
    top_change = top_change_val
    top_live = live_coin
    # top_change_val = pd.DataFrame(top_change_val)
    # top_change_val.columns=['market','change','change_str']
    # top_change_val.to_csv("./app/data/top_change.csv",index=True, header = True)
    return top_live, top_change
si()