from flask import Flask, jsonify, request
app = Flask(__name__)
@app.route('/price', methods=['POST'])
def func_9():
    
    qpqwe = {
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
                  "description": "4,500원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_01.jpg"
                },
                {
                  "title": "베이컨 아보카도",
                  "description": "5,500원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_02.jpg"
                },
                {
                  "title": "에그 포테이토",
                  "description": "5,300원",
                  "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_03.jpg"
                },
                {
                  "title": "갈릭 베이컨 토마토",
                  "description": "5,800원",
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
    return (qpqwe)