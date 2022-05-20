import pyupbit
import requests
import pandas as pd



## get_namedata() 함수
## marketData 와 tickers 데이터를 합쳐서 기준화폐 값까지 붙은 하나의 큰 데이터를 만드는 함수
## 중간에 대소문자 , 공백을 없애는 처리가 되어있음

def get_namedata():
    marketData = requests.get('https://api.upbit.com/v1/market/all') ## 업비트에서 거래가능한 마켓 목록(코드/이름/영어이름 데이터)
## marketData.status_code == 200 일때 정상적으로 정보 수신중이라는 뜻
## 200 일때 json 데이터로 저장
    if marketData.status_code == 200 :
        jsonMarket = marketData.json()


#print(type(jsonMarket))
#print(jsonMarket[0])
#print(len(jsonMarket))
#print(jsonMarket[0])


# 코드/이름/영어이름 dataframe 만들기(최종적으로 namedata2로 저장)




    market = []
    korean_name = []
    english_name = []
    for i in range(len(jsonMarket)) :
        namedata = jsonMarket[i]
        market.append(namedata['market'])
        korean_name.append(namedata['korean_name'])
        english_name.append(namedata['english_name'].lower().replace(" ",""))
    #namedata2.append(namedata.values())
    #print(namedata2)

#print(market)
#print(korean_name)
#print(english_name)

# df = df.set_index('A') 특정 컬럼을 인덱스로 설정

    tickers=pyupbit.get_tickers()
    namedata= pd.DataFrame((zip(market, korean_name, english_name)), columns = ['market', 'korean_name', 'english_name'])

#print(namedata2.loc[:,'market'])
#print(namedata2.loc[:,'market'].size)


## 새로운 행 만들어서 기준 화폐 입력
## 한화 = KRW, 비트코인 = BTC, 미국달러 = USDT
    currency = []
    for i in namedata.loc[:,'market']:
        if i.split('-')[0] == "KRW":
            currency.append("KRW")
        elif i.split('-')[0] == "BTC":
            currency.append("BTC")
        else:
            currency.append("USDT")

    #print(currency)   
    namedata['currency'] = currency
    namedata2 = namedata
    namedata.to_csv("name.csv", index=True, header=False)
    
    return namedata2

# 먼저 coin_name = input('')으로 코인 이름을 입력하게함
## a 입력값(보통 coin_name)과, b 입력값(보통 namedata2)을 받아서
## 우리가 input 으로 a 를 받았을 때 (보통 coin_name = input(코인입력) 다음에 나옴)
## a로 받은 값을 전처리해서 공백을 없애고 소문자로 바꾼다음
## b와 대조해서 맞는 값이 있는지를 비교해주고 그 비교값에 따라 결과를 출력해주는 함수