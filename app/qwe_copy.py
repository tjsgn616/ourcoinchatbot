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


#print(json.dumps(json_data) )

## 9시 , 2시 , 8시
# https://ddolcat.tistory.com/660
app = Flask(__name__)
@app.route('/price', methods=['POST'])
def func_9():
    print(csv_data)
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
    for i in csv_data['market']:
        top5_coins.append(i)
    print(top5_coins)
    #for i in top_5_coin_names:      # 위에꺼랑 합칠수 없나? 될거가튼데
    for i in top5_coins:
        current_price = (pyupbit.get_current_price(i))
        time.sleep(0.05)
        past_price_20 = (pyupbit.get_ohlcv(f'{i}', interval="minute60", to=f'{pastDatetime_YYYY}{pastDatetime_md}{pastDatetime_HM}', count=1).open[0])
        time.sleep(0.05)
        #coin_id = ''.join(i)
        #coin_id_id = coin_id[4:7]
        past_time2 = 0
        #past_price3 = round(100*(past_price2-past_price1)/past_price1,3)
        #past_price4 = round(100*(current_price-past_price_20)/past_price_20,3)
        for num1 in 12,10,8,6,4,2,0 : #[(12,10),(10,8),(8,6),(6,4),(4,2),(2,0)]:#([2,4,6,8,10,12], [0,2,4,6,8,10]:)]
            past_time1 = past_time2
            past_time2 = (datetime.datetime.now()+datetime.timedelta(hours=-num1)).strftime('%Y%m%d%H%M')
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
                    sun = round(100*(past_price2-past_price1)/past_price1,3)
                   
                    #return (sun)
                    # print(past_d1,'일',past_H1,'시: ''\033[31m',past_price1,round(100*(past_price2-past_price1)/past_price1,3),'%, 맑음''\033[0m')
                else:
                    cloud = round(100*(past_price2-past_price1)/past_price1,3)

                    #print(past_d1,'일',past_H1,'시: ''\033[34m',past_price1,round(100*(past_price2-past_price1)/past_price1,3),'%, 흐림''\033[0m')
        
        if current_price >= past_price_20:
                qwe = {
  "version": "2.0",
  "template": {
    "outputs": [
      {
        "carousel": {
          "type": "listCard",
          "items": [
            {
              "header": {
                "title": "샌드위치"
              },
              "items": [
                {
                  "title": "햄치즈",
                  "description": "베이컨 아보카도",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_01.jpg"
                },
                {
                  "title": "베이컨 아보카도",
                  "description": "베이컨 아보카도",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_02.jpg"
                },
                {
                  "title": "에그 포테이토",
                  "description": "베이컨 아보카도",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_03.jpg"
                },
                {
                  "title": "갈릭 베이컨 토마토",
                  "description": "베이컨 아보카도",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_04.jpg"
                }
              ],
              "buttons": [
                {
                  "label": "더보기",
                  "action": "message",
                  "messageText" : "샌드위치 더보기"
                }
              ]
            },
            {
              "header": {
                "title": "커피"
              },
              "items": [
                {
                  "title": "아메리카노",
                  "description": "1,800원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_05.jpg"
                },
                {
                  "title": "카페라떼",
                  "description": "2,000원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_06.jpg"
                },
                {
                  "title": "카페모카",
                  "description": "2,500원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_07.jpg"
                },
                {
                  "title": "소이라떼",
                  "description": "2,200원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_08.jpg"
                }
              ],
              "buttons": [
                {
                  "label": "더보기",
                  "action": "message",
                  "messageText" : "커피 더보기"
                }
              ]
            }
          ]
        }
      }
    ],
    "quickReplies": [
      {
        "messageText": "인기 메뉴",
        "action": "message",
        "label": "인기 메뉴"
      },
      {
        "messageText": "최근 주문",
        "action": "message",
        "label": "최근 주문"
      },
      {
        "messageText": "장바구니",
        "action": "message",
        "label": "장바구니"
      }
    ]
  }
}   
                return (qwe)
        else:
                abc = {
  "version": "2.0",
  "template": {
    "outputs": [
      {
        "carousel": {
          "type": "listCard",
          "items": [
            {
              "header": {
                "title": "샌드위치"
              },
              "items": [
                {
                  "title": "햄치즈",
                  "description": "베이컨 아보카도",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_01.jpg"
                },
                {
                  "title": "베이컨 아보카도",
                  "description": "베이컨 아보카도",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_02.jpg"
                },
                {
                  "title": "에그 포테이토",
                  "description": "베이컨 아보카도",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_03.jpg"
                },
                {
                  "title": "갈릭 베이컨 토마토",
                  "description": "베이컨 아보카도",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_04.jpg"
                }
              ],
              "buttons": [
                {
                  "label": "더보기",
                  "action": "message",
                  "messageText" : "샌드위치 더보기"
                }
              ]
            },
            {
              "header": {
                "title": "커피"
              },
              "items": [
                {
                  "title": "아메리카노",
                  "description": "1,800원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_05.jpg"
                },
                {
                  "title": "카페라떼",
                  "description": "2,000원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_06.jpg"
                },
                {
                  "title": "카페모카",
                  "description": "2,500원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_07.jpg"
                },
                {
                  "title": "소이라떼",
                  "description": "2,200원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_08.jpg"
                }
              ],
              "buttons": [
                {
                  "label": "더보기",
                  "action": "message",
                  "messageText" : "커피 더보기"
                }
              ]
            }
          ]
        }
      }
    ],
    "quickReplies": [
      {
        "messageText": "인기 메뉴",
        "action": "message",
        "label": "인기 메뉴"
      },
      {
        "messageText": "최근 주문",
        "action": "message",
        "label": "최근 주문"
      },
      {
        "messageText": "장바구니",
        "action": "message",
        "label": "장바구니"
      }
    ]
  }
}
                
                return (abc)

#func_9()
#func_14()
#func_20()