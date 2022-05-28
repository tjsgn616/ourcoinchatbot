#from flask import Flask
#app = Flask(__name__)
#@app.route('/price', methods=['POST'])
import pandas as pd
def func_11():
    #csv_data = pd.read_csv("./app/filename.csv") 
    csv_data = pd.read_csv("filename.csv")
    print(csv_data)
func_11()
    