'''
from flask import Flask
import weather_currency 
weather_currency.marketData
app = Flask(__name__)
@app.route('/price', methods=['POST'])
'''
from cgi import test
import requests
import csv
#import time 
import pandas as pd
#import jobs
def func_9():
    

    url = "https://api.upbit.com/v1/candles/minutes/1?market=KRW-BTC&count=1"

       

    response = requests.get(url)
    response = response.text 

    with open("data/filename.csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(response)
    test = pd.read_csv("./app/data/filename.csv")  
    print(test)
    #print(jobs.func_11) 
func_9()