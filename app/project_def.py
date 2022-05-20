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
    
    namedata2 = namedata
    return namedata2



# 먼저 coin_name = input('')으로 코인 이름을 입력하게함
## a 입력값(보통 coin_name)과, b 입력값(보통 namedata2)을 받아서
## 우리가 input 으로 a 를 받았을 때 (보통 coin_name = input(코인입력) 다음에 나옴)
## a로 받은 값을 전처리해서 공백을 없애고 소문자로 바꾼다음
## b와 대조해서 맞는 값이 있는지를 비교해주고 그 비교값에 따라 결과를 출력해주는 함수
def change_name(a, b):
    
    a = a.lower().replace(" " , "")
#print(b['korean_name'])
    answer = []

#print(b.korean_name[0])
    for i in b.index:
        if a == b.korean_name[i] or a == b.english_name[i]:
            answer.append([b.market[i],b.currency[i]])


    
# answer[여럿나온 답의 순서][0=market code, 1= currency]
#print(answer[:len(answer)][:len(answer)])
    while len(answer) == 0:
        print("일치하는 가상화폐가 존재하지 않습니다. 이름을 다시 확인해 주세요.")
        a = input("원하시는 가상 화폐를 입력하세요.")
        a = a.lower().replace(" " , "")
        for i in b.index:
            if a == b.korean_name[i] or a == b.english_name[i]:
                answer.append([b.market[i],b.currency[i]])
#print(b['korean_name'])
    

#print(b.korean_name[0])
    
    if len(answer) == 1:
        input_coin_name = answer[0][0]
    
    else:
        selection = []
        for i in range(len(answer)):
            selection.append(answer[i][1])
    #print(selection)    
        print("기준 화폐가 다수 존재합니다: ", selection)
        cur_sel = input('원하시는 기준 화폐를 선택하세요.').upper()
        while cur_sel not in selection:
            print("잘못된 입력입니다. 원하시는 기준 화폐를 올바르게 입력해주세요. ", selection)
            cur_sel = input('원하시는 기준 화폐를 선택하세요.').upper()
        n = selection.index(cur_sel)
        input_coin_name = answer[n][0]
        return input_coin_name
        
    

## current=현재 가격 값과, past=과거 가격 값을 받아서 비교한 뒤 결과에 따라 다른 출력을 내는 함수
def show_change(current, past):
    if current > past:
            print('\033[31m' +  '가격 상승'+  '\033[0m')
            print('변동량:''\033[31m',current-past,'\033[0m')
            print('변동률:''\033[31m', round((current-past)*100/past, 2),'%''\033[0m')
    elif current == past:
        print(f'가격 보합(변화 없음)')
    else:
        print('\033[34m' +  '가격 하락'+  '\033[0m')
        print('변동량:''\033[34m',current - past, '\033[0m')
        print('변동률:''\033[34m', round((current-past)*100/past, 2),'%''\033[0m')


