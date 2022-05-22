from flask import Flask, request, jsonify

app = Flask(__name__)
import datetime
now = datetime.datetime.now()
@app.route('/price', methods=['POST'])
def message():
        while True:
            t = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleImage": {
                                "imageUrl": "http://k.kakaocdn.net/dn/83BvP/bl20duRC1Q1/lj3JUcmrzC53YIjNDkqbWK/i_6piz1p.jpg",
                                "altText": "보물상자입니다"
                            }
                        }
                    ]
                }
            }
            if now.hour != 4:
                break
    
        return jsonify(t)

    



