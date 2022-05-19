from flask import Flask, jsonify, request, g
import pyupbit

app = Flask(__name__) 

@app.route('/test', methods=['POST'])
def test():
    t = pyupbit.get_current_price("KRW-BTC")
    print(t)
    test_j ={
        "version" : "2.0",
        "data" : {
            "coin" : f"{coin_name}",
            "money" : f"{selection[]}",
            "price" : f"{t}"
        }
    }
    # return(test_j)