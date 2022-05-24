responseBody = {"version": "2.0",
                "template": {
                "outputs": [
                {
                    "carousel": {
                    "type":"listCard",
                    "items": [
                        {
                        "header": {
                        "title": "비트코인 뉴스 보러가기"
                        },
              "items": [
                {
                "title": f"{title[0]}",
                "imageUrl": f"{img[0]}",
                "link": {
                  "web": f"{url[0]}"
                        }
                },
                {
                  "title": f"{title[1]}",
                  "imageUrl": f"{img[1]}",
                  "link": {
                    "web": f"{url[1]}"
                  }
                },
                {
                  "title": f"{title[2]}",
                 "imageUrl": f"{img[2]}"  ,             
                  "link": {
                    "web": f"{url[2]}"
                  }
                },
                {
                  "title": f"{title[3]}",
                  "imageUrl": f"{img[3]}",
                  "link": {
                    "web": f"{url[3]}"
                  }
                },
                {
                  "title": f"{title[4]}",
                  "imageUrl": f"{img[4]}",      
                  "link": {
                    "web": f"{url[4]}"
                  }
              }
              ],
                "buttons": [
            {
              "label": "더 보기",
              "action": "webLink",
              "webLinkUrl": "https://search.naver.com/search.naver?where=news&sm=tab_jum&query=비트코인"
            }
                
              ]
                  }
              ]  
          }
        }
        ]
        }
        }