from re import template
from flask import Flask, make_response, jsonify, request, g
import pandas as pd
import pyupbit
import requests
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
from bs4 import BeautifulSoup
from pandas import DataFrame
import re
import urllib.request
from urllib.parse import quote


app = Flask(__name__)


tz = pytz.timezone('Asia/Seoul')
time_now = datetime.now(tz)
time_now = time_now.strftime('%Y-%m-%d %H:%M')
print(time_now)

def marketData():
    # 마켓 데이터 불러오기
    marketData = requests.get('https://api.upbit.com/v1/market/all') # API 그냥 쓰면 되는듯

    if marketData.status_code == 200 :
        marketData = marketData.json()

    # 마켓 코드, 한글, 영어 df로 정리
    market = []
    korean_name = []
    english_name = []
    for i in range(len(marketData)) :
        namedata = marketData[i]
        market.append(namedata['market'])
        korean_name.append(namedata['korean_name'])
        english_name.append(namedata['english_name'].upper().replace(" ",""))

    namedata= pd.DataFrame((zip(market, korean_name, english_name)), columns = ['market', 'korean_name', 'english_name'])
    
    # 코인 종류 분할
    currency = []
    for i in namedata.loc[:,'market']:
        if i.split('-')[0] == "KRW":
            currency.append("KRW")
        elif i.split('-')[0] == "BTC":
            currency.append("BTC")
        else:
            currency.append("USDT")
    namedata['currency'] = currency
    coinId = []
    for i in namedata.loc[:,"market"]:
        coinId.append(i.split('-')[1])
    namedata['Id'] = coinId
    return namedata





@app.route('/now', methods=['POST'])
def now():
    best_Id = ['KRW-BTC', 'KRW-ETH','KRW-DOGE']
    current_price =  {  "version": "2.0",
                        "template": {
                            "outputs": [
                            {
                                "carousel": {
                                "type": "listCard",
                                "items": [
                                    {
                                    "header": {
                                        "title": "현재 시세 조회"
                                    },
                                    "items": [
                                        {
                                        "title": "비트코인",
                                        "description" : f"{pyupbit.get_current_price(best_Id[0]):.2f}원",
                                        "imageUrl": "https://static.upbit.com/logos/BTC.png"
                                        },
                                        {
                                        "title": "이더리움",
                                        "description": f"{pyupbit.get_current_price(best_Id[1]):.2f}원",
                                        "imageUrl": "https://static.upbit.com/logos/ETH.png"
                                        },
                                        {
                                        "title": "도지코인",
                                        "description": f"{pyupbit.get_current_price(best_Id[2]):.2f}원",
                                        "imageUrl": "https://static.upbit.com/logos/DOGE.png"
                                        }],
                                    "buttons": [
                                        {
                                        "label": "더 많은 코인 보러가기",
                                        "action": "block",
                                        "blockId": "628d8ff47bd2fd433357e2ee"
                                        }
                                    ]
                                    }
                                ]
                                }
                            }
                        
                            ]
                        }
                    }
    return current_price





@app.route('/more',methods=['POST'])
def test():
    # 마켓 이름 데이터, 환율값, 발화 값 가져오기
    nameData = marketData()
    dataRecive = request.get_json()
    coin = dataRecive['action']['params']['guideMore'].upper().replace(" ","")
    USD = requests.get('https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD')
    USD = USD.json()
    USD = USD[0]['basePrice']

    # 
    answer = []
    for i in nameData.index:
        if coin == nameData.korean_name[i] or coin == nameData.english_name[i] or coin == nameData.market[i]:
            answer.append([nameData.market[i],nameData.currency[i]])

    # 전체 마켓 시장에서 입력한 코인과 같은 종류의 코인 뽑아서 리스트로 반환 (KRW, BTC,USDT)
    # 코인 외 잘못 발화된 값은 coin_now =[]로 빈 리스트 추출
    # 다양한 입력 형태 다 포용한다.
    name_list = nameData.values.tolist()
    # print(name_list[:4])
    coin_now = []
    for i in range(len(name_list)):
        if coin in name_list[i]:
            coin_now.extend(name_list[i])
    # print("---coin_name----",coin_now)
    coin_now = set(coin_now)
    # print("----no 중복 코인 ----",coin_now)

    # 해당 코인의 화폐 시장 종류 뽑아내서 리스트로 반환 ->selection ['KRW','BTC','USDT] 형태
    # 잘못된 발화인 경우 selection =[] 빈 리스트 추출
    selection = []
    for i in range(len(answer)):
        selection.append(answer[i][1])


    if coin not in coin_now:
        coin_error = {
            "version":"2.0",
            "template":{
                "outputs":[
                    {
                        "basicCard":{
                            "title":"입력 오류",
                            "description":"존재하지 않는 가상 화폐이거나 입력 오류입니다",
                            "thumbnail":{
                                "imageUrl":"https://user-images.githubusercontent.com/65166786/169485601-ea315e41-4b3c-4520-b11a-6461d3e3233e.jpg"
                            },
                            "buttons":[
                                {
                                    "action":"block",
                                    "label":"다시 입력하기",
                                    "blockId": "628d8ff47bd2fd433357e2ee",
                                    "messageText":"짜잔!"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        return coin_error
    else:
        # 어떤 형태의 코인을 입력하던지 한국 이름으로 출력하게 한다.
        j=0
        for i in name_list:
            if coin in i:
                coin_id = nameData.iloc[j]['Id']
                coin_korea = nameData.iloc[j]['korean_name']
                break
            j +=1
        
        # print("aaaaaaaaaaaaaaaaaaa",coin_korea)

        # 첫 배포 -> KRW 기준의 시세조회
        # KRW 시장이 없는 코인의 경우 -> 해당 시장 값 * btc로 원화 값 반환
        # KRW 시장이 있는 경우 그대로 현재 시세 조회
        if "KRW" not in selection:
            # print("KRW 없음")
            if "BTC" in selection:
                BITCOIN = pyupbit.get_current_price("KRW-BTC")
                BTC = selection.index("BTC")
                ticker = answer[BTC][0]
                coin_money = pyupbit.get_current_price(ticker)
                coin_price = (BITCOIN * coin_money)
                # print("한국 돈 변환 값 BTC : ",coin_price)
            else : 
                ticker = answer[0][0]
                coin_money = pyupbit.get_current_price(ticker)
                coin_price = (USD * coin_money)
                # print("한국 돈 변환 값 USDT : ",coin_price)
        else:
            # print("KRW 인덱스 값 KRW:" , selection.index("KRW"))
            KRW = selection.index("KRW")
            ticker = answer[KRW][0]
            coin_price = pyupbit.get_current_price(ticker)

        coin_price_now = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                            "itemCard": {
                            
                            
                                "imageTitle": {
                                    "title": "현재 시세 조회",
                                    "imageUrl" : f"https://static.upbit.com/logos/{coin_id}.png"
                                },
                                "itemList": [
                                    {
                                    "title": "가상 화폐",
                                    "description": f"{coin_korea}"
                                    },
                                    {
                                    "title": "현재 시간",
                                    "description": f"{time_now}"
                                    },
                                    {
                                    "title" : "기준",
                                    "description" : "KRW"
                                    },
                                    {
                                    "title" : "현재 시세",
                                    "description" : f"{coin_price:.2f}원"
                                    }
                                ],
                                "itemListAlignment": "left",
                                "buttons": [
                                    {
                                    "label": "추가 조회",
                                    "action": "block",
                                    "blockId": "628d8ff47bd2fd433357e2ee",
                                    "messageText" : "추가 조회"
                                    },
                                    {
                                    "label": "업비트",
                                    "action": "webLink",
                                    "messageText": "업비트 보러가기",
                                    "webLinkUrl": f"https://upbit.com/exchange?code=CRIX.UPBIT.{ticker}"
                                    },
                                    
                                ],
                                
                            }
                            }
                        ]
                    }
                }
            
        
        
        return coin_price_now
@app.route('/hopeprice',methods=['POST'])
def hope_pirce():
    nameData = marketData()
    dataReceive = request.get_json()
    
    Coin_Name = dataReceive['action']['params']['HopePrice_Coin'].upper().replace(" ","")
    Average_Price = int(dataReceive['action']['params']['HopePrice_Average'])
    print(Average_Price)
     # 평균 가격
    Return_Rate = int(dataReceive['action']['params']['HopePrice_Rate']) # 수익률
    print(Return_Rate)
    
    Goal_Price = ((Return_Rate + 100)/100)*Average_Price
    Goal_Price = round(Goal_Price,1)

    USD = requests.get('https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD')
    USD = USD.json()
    USD = USD[0]['basePrice']

    # 
    answer = []
    for i in nameData.index:
        if Coin_Name == nameData.korean_name[i] or Coin_Name == nameData.english_name[i] or Coin_Name == nameData.market[i]:
            answer.append([nameData.market[i],nameData.currency[i]])

    # 전체 마켓 시장에서 입력한 코인과 같은 종류의 코인 뽑아서 리스트로 반환 (KRW, BTC,USDT)
    # 코인 외 잘못 발화된 값은 coin_now =[]로 빈 리스트 추출
    # 다양한 입력 형태 다 포용한다.
    name_list = nameData.values.tolist()
    # print(name_list[:4])
    Coin_now = []
    for i in range(len(name_list)):
        if Coin_Name in name_list[i]:
            Coin_now.extend(name_list[i])
    # print("---coin_name----",coin_now)
    Coin_now = set(Coin_now)
    # print("----no 중복 코인 ----",coin_now)

    # 해당 코인의 화폐 시장 종류 뽑아내서 리스트로 반환 ->selection ['KRW','BTC','USDT] 형태
    # 잘못된 발화인 경우 selection =[] 빈 리스트 추출
    selection = []
    for i in range(len(answer)):
        selection.append(answer[i][1])


    if Coin_Name not in Coin_now:
        coin_error = {
            "version":"2.0",
            "template":{
                "outputs":[
                    {
                        "basicCard":{
                            "title":"입력 오류",
                            "description":"존재하지 않는 가상 화폐이거나 입력 오류입니다",
                            "thumbnail":{
                                "imageUrl":"https://user-images.githubusercontent.com/65166786/169485601-ea315e41-4b3c-4520-b11a-6461d3e3233e.jpg"
                            },
                            "buttons":[
                                {
                                    "action":"block",
                                    "label":"다시 입력하기",
                                    "blockId": "627e143204a7d7314aebbda3",
                                    "messageText":"짜잔!"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        return coin_error
    else:
        # 어떤 형태의 코인을 입력하던지 한국 이름으로 출력하게 한다.
        j=0
        for i in name_list:
            if Coin_Name in i:
                coin_id = nameData.iloc[j]['Id']
                coin_korea = nameData.iloc[j]['korean_name']
                break
            j +=1
        
        # print("aaaaaaaaaaaaaaaaaaa",coin_korea)

        # 첫 배포 -> KRW 기준의 시세조회
        # KRW 시장이 없는 코인의 경우 -> 해당 시장 값 * btc로 원화 값 반환
        # KRW 시장이 있는 경우 그대로 현재 시세 조회
        if "KRW" not in selection:
            # print("KRW 없음")
            if "BTC" in selection:
                BITCOIN = pyupbit.get_current_price("KRW-BTC")
                BTC = selection.index("BTC")
                ticker = answer[BTC][0]
                coin_money = pyupbit.get_current_price(ticker)
                coin_price = (BITCOIN * coin_money)
                income = round((coin_price/Average_Price)*100 - 100,2)
                # print("한국 돈 변환 값 BTC : ",coin_price)
            else : 
                ticker = answer[0][0]
                coin_money = pyupbit.get_current_price(ticker)
                coin_price = (USD * coin_money)
                income = round((coin_price/Average_Price)*100 - 100,2)
                # print("한국 돈 변환 값 USDT : ",coin_price)
        else:
            # print("KRW 인덱스 값 KRW:" , selection.index("KRW"))
            KRW = selection.index("KRW")
            ticker = answer[KRW][0]
            coin_price = pyupbit.get_current_price(ticker)
            income = round((coin_price/Average_Price)*100 - 100,2)
        
        coin_price_now = {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                            "itemCard": {
                            
                            
                                "imageTitle": {
                                    "title": "희망 매도가 조회",
                                    "imageUrl" : f"https://static.upbit.com/logos/{coin_id}.png"
                                },
                                "itemList": [
                                    {
                                    "title": "가상 화폐",
                                    "description": f"{coin_korea}"
                                    },
                                    {
                                    "title" : "기준",
                                    "description" : "KRW"
                                    },
                                    {
                                    "title": "입력 평단가",
                                    "description": f"{Average_Price}"
                                    },{
                                    "title": "희망 수익률",
                                    "description": f"{Return_Rate}%"
                                    },{
                                    "title": "희망 가격",
                                    "description": f"{Goal_Price:.1f}원"
                                    },
                                    {
                                    "title" : "현재 시세",
                                    "description" : f"{coin_price:.1f}원"
                                    },{
                                    "title": "현재 수익률",
                                    "description": f"{income}%"
                                    }
                                ],
                                "itemListAlignment": "left",
                                "buttons": [
                                    {
                                    "label": "추가 조회",
                                    "action": "block",
                                    "blockId": "627e143204a7d7314aebbda3",
                                    "messageText" : "추가 조회"
                                    },
                                    {
                                    "label": "업비트",
                                    "action": "webLink",
                                    "messageText": "업비트 보러가기",
                                    "webLinkUrl": f"https://upbit.com/exchange?code=CRIX.UPBIT.{ticker}"
                                    },
                                    
                                ],
                                
                            }
                            }
                        ]
                    }
                }
            
        
        
        return coin_price_now
    
    '''
    goal_price = ((answer2 + 100)/100)* answer
  goal_price = round(goal_price)
  current_price = pyupbit.get_current_price(coin)
  income = (current_price/answer)*100 - 100
  print(f"나의 매도 타이밍은 수익율이 {answer2}% 오른 {goal_price}원이 됐을 때입니다.")
  print(f"현재 수익률은 {income}%입니다.")
    '''
    


@app.route('/searchnews',methods=['POST'])
def searchnews():
    

    dataReceive = request.get_json()
    print(dataReceive)
    search_name = dataReceive['action']['clientExtra']['key']
    query = quote(search_name )

    news_num = 5

    news_url = f'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={query}'

    req = requests.get(news_url)
    soup = BeautifulSoup(req.text, 'html.parser')

    news_dict = {} 
    idx = 0 
    #cur_page = 1

    while idx < news_num:
    ### 네이버 뉴스 웹페이지 구성이 바뀌어 태그명, class 속성 값 등을 수정함(20210126) ###
        
        table = soup.find('ul',{'class' : 'list_news'})
        li_list = table.find_all('li', {'id': re.compile('sp_nws.*')})
        area_list = [li.find('div', {'class' : 'news_area'}) for li in li_list]
        a_list = [area.find('a', {'class' : 'news_tit'}) for area in area_list]
        
        for n in a_list[:min(len(a_list), news_num-idx)]:
            news_dict[idx] = {'title' : n.get('title'),
                              'url' : n.get('href') }
            idx += 1

        #cur_page += 1
        
        #pages = soup.find('div', {'class' : 'sc_page_inner'})
        #next_page_url = [p for p in pages.find_all('a') if p.text == str(cur_page)][0].get('href')
        
        #req = requests.get('https://search.naver.com/search.naver' + next_page_url)
        #soup = BeautifulSoup(req.text, 'html.parser')


    news_df = DataFrame(news_dict)

    title = []
    url = []
    i = 0
    for i in range(len(news_dict)):
      title.append(news_df.loc['title'][i])
      url.append(news_df.loc['url'][i])
    #print(title)


    
    
    imgurl = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query='
    imgurl = imgurl + query
    
    #print(imgurl)
    req = urllib.request.Request(imgurl)
    #print(req)
    res = urllib.request.urlopen(imgurl).read()  # 여기가 문제에요, 고쳤어요 -> url 형식으로 바꿔주었어요 (quote)
    #print('res:' ,res)
    
    soup = BeautifulSoup(res,'html.parser')
    soup = soup.find_all("a",class_="dsc_thumb")
    #print(soup)
    #print(soup[0])
    #print
    imgUrl = []
    for i in range(len(soup)):
      imgUrl.append(soup[i].find("img")["src"])

    #img = []
    #for i in range(5):
    #  img.append(imgUrl[i])
      
    responseBody = {"version": "2.0",
                "template": {
                "outputs": [
                {
                    "carousel": {
                    "type":"listCard",
                    "items": [
                        {
                        "header": {
                        "title": f"{search_name} 소식"
                        },
              "items": [
                {
                "title": f"{title[0]}",
                "imageUrl": f"{imgUrl[0]}",
                "link": {
                  "web": f"{url[0]}"
                        }
                },
                {
                  "title": f"{title[1]}",
                  "imageUrl": f"{imgUrl[1]}",
                  "link": {
                    "web": f"{url[1]}"
                  }
                },
                {
                  "title": f"{title[2]}",
                 "imageUrl": f"{imgUrl[2]}"  ,             
                  "link": {
                    "web": f"{url[2]}"
                  }
                },
                {
                  "title": f"{title[3]}",
                  "imageUrl": f"{imgUrl[3]}",
                  "link": {
                    "web": f"{url[3]}"
                  }
                },
                {
                  "title": f"{title[4]}",
                  "imageUrl": f"{imgUrl[4]}",      
                  "link": {
                    "web": f"{url[4]}"
                  }
              }
              ],
                "buttons": [
            {
              "label": "더 보기",
              "action": "webLink",
              "webLinkUrl": f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={search_name}"
            }
                
              ]
                  }
              ]  
          }
        }
        ]
        }
        }
    return responseBody




@app.route('/basic',methods=['POST'])
def sayHello():
    #body = request.get_json()
    #print(body)
    #print(body['userRequest']['utterance'])


    query = "비트코인|가상화폐|가상자산|이더리움"
    query = query.replace(' ', '+') 

    news_num = 5

    news_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8%7C%EC%9D%B4%EB%8D%94%EB%A6%AC%EC%9B%80%7C%EA%B0%80%EC%83%81%ED%99%94%ED%8F%90%7C%EA%B0%80%EC%83%81%EC%9E%90%EC%82%B0'
                
    req = requests.get(news_url.format(query))
    soup = BeautifulSoup(req.text, 'html.parser')

    news_dict = {} 
    idx = 0 
    #cur_page = 1

    while idx < news_num:
    ### 네이버 뉴스 웹페이지 구성이 바뀌어 태그명, class 속성 값 등을 수정함(20210126) ###
        
        table = soup.find('ul',{'class' : 'list_news'})
        li_list = table.find_all('li', {'id': re.compile('sp_nws.*')})
        area_list = [li.find('div', {'class' : 'news_area'}) for li in li_list]
        a_list = [area.find('a', {'class' : 'news_tit'}) for area in area_list]
        
        for n in a_list[:min(len(a_list), news_num-idx)]:
            news_dict[idx] = {'title' : n.get('title'),
                              'url' : n.get('href') }
            idx += 1

        #cur_page += 1
        #print(cur_page)
        #pages = soup.find('div', {'class' : 'sc_page_inner'})
        #print(pages)
        #print(pages.find_all('a'))
        #what = (p for p in pages.find_all('a') if p.text == cur_page)
        #print(what)
        #for p in pages.find_all('a'):
            #print(p)
            #if p.text == cur_page:
            #    next_page_url = p.get('href')
            #    print(next_page_url)
        #next_page_url = [p for p in pages.find_all('a') if p.text == cur_page][0].encode('utf-8').get('href')
        
        #req = requests.get('https://search.naver.com/search.naver' + next_page_url)
        #soup = BeautifulSoup(req.text, 'html.parser')


    news_df = DataFrame(news_dict)

    title = []
    url = []
    i = 0
    for i in range(len(news_dict)):
      title.append(news_df.loc['title'][i])
      url.append(news_df.loc['url'][i])
    #print(title)


    
    
    imgurl = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8%7C%EC%9D%B4%EB%8D%94%EB%A6%AC%EC%9B%80%7C%EA%B0%80%EC%83%81%ED%99%94%ED%8F%90%7C%EA%B0%80%EC%83%81%EC%9E%90%EC%82%B0'
    req = urllib.request.Request(imgurl)
    res = urllib.request.urlopen(imgurl).read()
    
    soup = BeautifulSoup(res,'html.parser')
    soup = soup.find_all("a",class_="dsc_thumb")
    #print(soup[0])
    #print
    imgUrl = []
    for i in range(len(soup)):
      imgUrl.append(soup[i].find("img")["src"])

    #img = []
    #for i in range(5):
    #  img.append(imgUrl[i])
      
    responseBody = {"version": "2.0",
                "template": {
                "outputs": [
                {
                    "carousel": {
                    "type":"listCard",
                    "items": [
                        {
                        "header": {
                        "title": "가상화폐 연관 뉴스 보러가기"
                        },
              "items": [
                {
                "title": f"{title[0]}",
                "imageUrl": f"{imgUrl[0]}",
                "link": {
                  "web": f"{url[0]}"
                        }
                },
                {
                  "title": f"{title[1]}",
                  "imageUrl": f"{imgUrl[1]}",
                  "link": {
                    "web": f"{url[1]}"
                  }
                },
                {
                  "title": f"{title[2]}",
                 "imageUrl": f"{imgUrl[2]}"  ,             
                  "link": {
                    "web": f"{url[2]}"
                  }
                },
                {
                  "title": f"{title[3]}",
                  "imageUrl": f"{imgUrl[3]}",
                  "link": {
                    "web": f"{url[3]}"
                  }
                },
                {
                  "title": f"{title[4]}",
                  "imageUrl": f"{imgUrl[4]}",      
                  "link": {
                    "web": f"{url[4]}"
                  }
              }
              ],
                "buttons": [
            {
              "label": "더 보기",
              "action": "webLink",
              "webLinkUrl": "https://search.naver.com/search.naver?where=news&sm=tab_jum&query=비트코인%7C이더리움%7C가상화폐%7C가상자산"
            }
                
              ]
                  }
              ]  
          }
        }
        ]
        }
        }
    return responseBody







@app.route('/youtube',methods=['POST'])
# 모듈 설치
#pip install --upgrade google_api_python_client
#pip install oauth2client

# 모듈 import 단
#from googleapiclient.discovery import build
#from googleapiclient.errors import HttpError
#from oauth2client.tools import argparser

# 모듈을 requirements 에 추가해줘야 heroku deploy가 작동한다.
# google_api_python_client==2.48.0
# oauth2client==4.1.3

def sayHello1():
    #body1 = request.get_json()
    #print(body1)
    #print(body1['userRequest']['utterance'])

# https://console.cloud.google.com/apis/credentials 여기서 API발급받아 사용
    DEVELOPER_KEY='AIzaSyBa_S65tRPb1mALqTtsDB1e9p6s-7kshJA' # 내 API 키값 입력
    YOUTUBE_API_SERVICE_NAME='youtube'
    YOUTUBE_API_VERSION='v3'

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                            developerKey = DEVELOPER_KEY)

    search_response=youtube.search().list(
        q="비트코인",
        
        part='id, snippet',
        maxResults=5,
        ).execute()
    print(search_response)
    search_title = []
    search_url = []
    thumb_img = []
    for i in range (5):
        search_title.append(search_response['items'][i]['snippet']['title'])
        search_url.append('https://youtube.com/watch?v='+ search_response['items'][i]['id']['videoId'])
        thumb_img.append(search_response['items'][i]['snippet']['thumbnails']['default']['url'])
    print(thumb_img)  
   
    responseBody1 = {"version": "2.0",
                      "template": {
                      "outputs": [
                      {
                          "carousel": {
                          "type":"listCard",
                          "items": [
                              {
                              "header": {
                              "title": "비트코인 영상 보러가기"
                              },
                    "items": [
                      {
                      "title": f"{search_title[0]}",
                      "imageUrl": f"{thumb_img[0]}",  
                      "link": {
                        "web": f"{search_url[0]}"
                              }
                      },
                      {
                        "title": f"{search_title[1]}",
                       "imageUrl": f"{thumb_img[1]}", 
                        "link": {
                          "web": f"{search_url[1]}"
                        }
                      },
                      {
                        "title": f"{search_title[2]}",
                      "imageUrl": f"{thumb_img[2]}", 
                        "link": {
                          "web": f"{search_url[2]}"
                        }
                      },
                      {
                        "title": f"{search_title[3]}",
                        "imageUrl": f"{thumb_img[3]}", 
                        "link": {
                          "web": f"{search_url[3]}"
                        }
                      },
                      {
                        "title": f"{search_title[4]}",
                        "imageUrl": f"{thumb_img[4]}", 
                        "link": {
                          "web": f"{search_url[4]}"
                        }
                    }
                    ],
                      "buttons": [
                  {
                    "label": "더 보기",
                    "action": "webLink",
                    "webLinkUrl": "https://www.youtube.com/results?search_query=비트코인"
                  }
                      
                    ]
                        }
                    ]  
                }
              }
              ]
              }
              }
    return responseBody1







    '''
    
    responseBody1 = {"version": "2.0",
                    "template": {
                    "outputs": [
                    {
                        "carousel": {
                        "type":"listCard",
                        "items": [
                            {
                            "header": {
                            "title": "비트코인 영상 보러가기"
                            },
                  "items": [
                    {
                    "title": f"{search_title[0]}",

                    "link": {
                      "web": f"{search_url[0]}"
                            }
                    },
                    {
                      "title": f"{search_title[1]}",

                      "link": {
                        "web": f"{search_url[1]}"
                      }
                    },
                    {
                      "title": f"{search_title[2]}",

                      "link": {
                        "web": f"{search_url[2]}"
                      }
                    },
                    {
                      "title": f"{search_title[3]}",

                      "link": {
                        "web": f"{search_url[3]}"
                      }
                    },
                    {
                      "title": f"{search_title[4]}",
      
                      "link": {
                        "web": f"{search_url[4]}"
                      }
                  }
                  ],
                    "buttons": [
                {
                  "label": "더 보기",
                  "action": "webLink",
                  "webLinkUrl": "https://www.youtube.com/results?search_query=비트코인"
                }
                    
                  ]
                      }
                  ]  
              }
            }
            ]
            }
            }
    return responseBody1


@app.route('/youtube',methods=['POST'])

def sayHello1():
    body1 = request.get_json()
    print(body1)
    print(body1['userRequest']['utterance'])

# https://console.cloud.google.com/apis/credentials 여기서 API발급받아 사용
    DEVELOPER_KEY='AIzaSyBa_S65tRPb1mALqTtsDB1e9p6s-7kshJA' # 내 API 키값 입력
    YOUTUBE_API_SERVICE_NAME='youtube'
    YOUTUBE_API_VERSION='v3'

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                                            developerKey = DEVELOPER_KEY)

    search_response=youtube.search().list(
        q="비트코인",
        
        part='id, snippet',
        maxResults=5,
        ).execute()

    search_title = []
    search_url = []
    for i in range (5):
        search_title.append(search_response['items'][i]['snippet']['title'])
        search_url.append('https://youtube.com/watch?v='+ search_response['items'][i]['id']['videoId'])
    
    img = []
    for thumbnail in search_response['thumbnail']:
        img.append(thumbnail['snippet']['channelId'])
      
   
    responseBody1 = {"version": "2.0",
                      "template": {
                      "outputs": [
                      {
                          "carousel": {
                          "type":"listCard",
                          "items": [
                              {
                              "header": {
                              "title": "비트코인 영상 보러가기"
                              },
                    "items": [
                      {
                      "title": f"{search_title[0]}",
                      "imageUrl": f"{img[0]}",  
                      "link": {
                        "web": f"{search_url[0]}"
                              }
                      },
                      {
                        "title": f"{search_title[1]}",
                       "imageUrl": f"{img[1]}", 
                        "link": {
                          "web": f"{search_url[1]}"
                        }
                      },
                      {
                        "title": f"{search_title[2]}",
                      "imageUrl": f"{img[2]}", 
                        "link": {
                          "web": f"{search_url[2]}"
                        }
                      },
                      {
                        "title": f"{search_title[3]}",
                        "imageUrl": f"{img[3]}", 
                        "link": {
                          "web": f"{search_url[3]}"
                        }
                      },
                      {
                        "title": f"{search_title[4]}",
                        "imageUrl": f"{img[4]}", 
                        "link": {
                          "web": f"{search_url[4]}"
                        }
                    }
                    ],
                      "buttons": [
                  {
                    "label": "더 보기",
                    "action": "webLink",
                    "webLinkUrl": "https://www.youtube.com/results?search_query=비트코인"
                  }
                      
                    ]
                        }
                    ]  
                }
              }
              ]
              }
              }
    return responseBody1







'''




'''
@app.route('/msg1', methods=['POST'])
def msg1():
    simple = {
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": "test 현 시세 조회를 원하는 가상 화폐의 종류를 선택해주세요.\n그 외의 경우, 가상 화폐 명을 입력해 주세요.\n(ex: 니어프로토콜) " # f-string 수정
                    }
                
                }
            ]
            }
    }
    return(simple)
'''

'''
@app.route('/msg1', methods=['POST'])
def msg1():
    global selection
    global answer
    coin_name = request.get_json()
    print(coin_name)
    #dataReceive = request.get_json() # 사용자가 입력한 데이터
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
    #tickers=pyupbit.get_tickers()
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
    #coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","")
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
        #coin_name = dataReceive["userRequest"]["utterance"].lower().replace(" ","")
        #coin_name = dataReceive["action"]["detailparams"]["koreanname"]['value']
        #coin_name = dataReceive["content"]
        def zero_ticker():
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
                "buttons":[{
                "action": "block",
                "label": "처음으로",
                "blockID": '62849fe8ee59237543308cef'
                }]
            }
            }
            return jsonify(none_ticker)
        zero_ticker()
#print(namedata2['korean_name'])
        #answer = []
#print(namedata2.korean_name[0])
        #for i in namedata2.index:
            #if coin_name == namedata2.korean_name[i] or coin_name == namedata2.english_name[i]:
                #answer.append([namedata2.market[i],namedata2.currency[i]])
    if len(answer) == 1: # 화폐 단위 하나만 있을 때
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
        
        return  jsonify(now_price) # 문제점 : BTC는 소수점을 엄청 길게 표시하는데, 원화와 같은 소수점으로 표시하면 안된다.

@app.route('/msg0', methods=['POST'])
def msg0():
    dataReceive = request.get_json()
    ask_ticker = {
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": "test 현 시세 조회를 원하는 가상 화폐의 종류를 선택해주세요.\n그 외의 경우, 가상 화폐 명을 입력해 주세요.\n(ex: 니어프로토콜) " # f-string 수정
                    }
                
                }
            ],
                "quickReplies": [
           {    
                "messageText":"이더리움",
                "action":"block",
                "label": "이더리움",
                "blockid":"62849fe8ee59237543308cef"}
                ]
                
                #"action": "message",
                
                
                
                
                }
    }
    return jsonify(ask_ticker)






@app.route('/msg0', methods=['POST'])
def msg0():
    dataReceive = request.get_json()
    ask_ticker = {
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": "현 시세 조회를 원하는 가상 화폐의 종류를 선택해주세요.\n그 외의 경우, 가상 화폐 명을 입력해 주세요.\n(ex: 니어프로토콜) " # f-string 수정
                    }
                
                }
            ],
                "quickReplies": [
          {
                "action":"message",
                "label": "이더리움",
                "message": "이더리움"
                
                #"action": "message",
                
                
                
                
                },
          {
                "messageText": "비트코인",
                "action": "message",
                "label": "비트코인"
          },
          {
                "messageText": "도지코인",
                "action": "message",
                "label": "도지코인" # 비트코인의 경우 BTC를 어떻게 처리하지
                }
                ],
                "buttons":[{
                "action": "block",
                "label": "처음으로",
                "blockID":'62849af133d26f492e9e74af'}],

                "context": {
                "values": [{
                "name": 'coin_name',
                "lifespan": 3,
                "params": f'{dataReceive["userRequest"]["utterance"].lower().replace(" ","")}'}
                ]},
                
                }
                
                }                
            
                
                
    #print(ask_ticker[template])
    return jsonify(ask_ticker)


@app.route('/msg', methods=['POST'])
def msg():
    
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
    #tickers=pyupbit.get_tickers()
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
    
    #coin_name = dataReceive["action"]["detailparams"]["koreanname"]['value'] # 에반데
#print(namedata2['korean_name'])
    answer = []
#print(namedata2.korean_name[0])
    for i in namedata2.index:
        if coin_name == namedata2.korean_name[i] or coin_name == namedata2.english_name[i]:
            answer.append([namedata2.market[i],namedata2.currency[i]])
    return responseBody

## 카카오톡 텍스트형 응답
@app.route('/api/sayHello', methods=['POST'])
def sayHello():
    body = request.get_json()
    print(body)
    print(body['userRequest']['utterance'])

    responseBody = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "안녕 hello I'm Ryan"
                    }
                }
            ]
        }
    }

    return responseBody


## 카카오톡 이미지형 응답
@app.route('/api/showHello', methods=['POST'])
def showHello():
    body = request.get_json()
    print(body)
    print(body['userRequest']['utterance'])

    responseBody = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleImage": {
                        "imageUrl": "https://t1.daumcdn.net/friends/prod/category/M001_friends_ryan2.jpg",
                        "altText": "hello I'm Ryan"
                    }
                }
            ]
        }
    }

    return responseBody
'''