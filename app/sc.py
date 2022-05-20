import requests
from pandas import DataFrame
from bs4 import BeautifulSoup
import re
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/price', methods=['POST'])
def message():

    date = str(datetime.now())
    date = date[:date.rfind(':')].replace(' ', '_')
    date = date.replace(':','시') + '분'
    query = "비트코인"
    query = query.replace(' ', '+')
    news_num = 5
    news_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=비트코인'
    req = requests.get(news_url.format(query))
    soup = BeautifulSoup(req.text, 'html.parser')
    news_dict = {}
    idx = 0
    cur_page = 1
    print('크롤링 중...')
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
        cur_page += 1
        pages = soup.find('div', {'class' : 'sc_page_inner'})
        next_page_url = [p for p in pages.find_all('a') if p.text == str(cur_page)][0].get('href')
        req = requests.get('https://search.naver.com/search.naver' + next_page_url)
        soup = BeautifulSoup(req.text, 'html.parser')
    print('크롤링 완료')
    news_df = DataFrame(news_dict)
    #xlsx_file_name = '네이버뉴스_{}_{}.xlsx'.format(query, date)
    #news_df.to_excel(xlsx_file_name)
    print(news_df)
    #print(news_dict)

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
            "title": "비트코인 뉴스 보러가기"
          },
          "items": [
            {
              "title": "header[0]",
              "description": "뉴스 첫줄",
              "imageUrl": "뉴스 이미지",
              "link": {
                "web": "뉴스 링크)"
              }
            },
            {
              "title": "챗봇 관리자센터",
              "description": "카카오톡 채널 챗봇 만들기",
              "imageUrl": "http://k.kakaocdn.net/dn/N4Epz/btqqHCfF5II/a3kMRckYml1NLPEo7nqTmK/1x1.jpg",
              "action": "block",
              "blockId": "6266c1152ec05a4395328d72"
            },
            {
              "title": "Kakao i Voice Service",
              "description": "보이스봇 / KVS 제휴 신청하기",
              "imageUrl": "http://k.kakaocdn.net/dn/bE8AKO/btqqFHI6vDQ/mWZGNbLIOlTv3oVF1gzXKK/1x1.jpg",
              "action": "message",
              "messageText": "Kakao i Voice Service"
            }
          ]
        }
       ]
      }
     }
    ]
  }
}
    return jsonify(abc)