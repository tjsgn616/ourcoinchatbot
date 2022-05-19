from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/keyboard')
def keyboard():
    dataSend = {
        "type" : "buttons",
        "buttons" : ["시작하기"]
    }

    return jsonify(dataSend)

@app.route('/price', methods=['POST'])
def message():

    dataReceive = request.get_json()
    content = dataReceive["userRequest"]["utterance"]

    if content == u"시작하기":
        dataSend ={
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": "나는 쓰레기야"
                    }
                }    
            ]
                }
            }

    elif content == u"안녕하세요":
        dataSend ={
                "version": "2.0",
                "template": {
                "outputs": [
                {
                "simpleText": {
                "text": "맞아 쓰레기야"
                    }
                }    
            ]
                }
            }

    return jsonify(dataSend)

if __name__ == "__main__":
    app.run(host="0.0.0.0")