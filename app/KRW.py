'''
from flask import Flask
import weather_currency 
weather_currency.marketData
app = Flask(__name__)
@app.route('/price', methods=['POST'])
'''
import requests
import csv
def func_9():
    

    url = "https://api.upbit.com/v1/candles/minutes/1?market=KRW-BTC&count=1"

       

    response = requests.get(url)
    response = response.text 

    with open("filename.csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(response)
    print("ㅅㄷㄴㅅ ㅁㄴㅇ")      
func_9()