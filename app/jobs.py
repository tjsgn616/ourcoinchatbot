#from flask import Flask
#app = Flask(__name__)
#@app.route('/price', methods=['POST'])
import pandas as pd
csv_data = pd.read_csv("./app/top5_coin.csv")
def func_11():
     #  둘다 CSV 파일을 읽어들이지 못하는 문제 . 읽어들이지 못하는건지 생성하지 못하는건지 모르겠음
    #csv_data = pd.read_csv("filename.csv")
    print(csv_data)
func_11()
    