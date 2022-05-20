from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, make_response, jsonify, request

import time
import atexit

scheduler = BackgroundScheduler()
app = Flask(__name__)

@app.route('/msg4', methods=['POST'])

def print_data():
	print(f'job1 : {time.strftime("%H:%M:%S")}')
	now_price = {
            "version": "2.0",
            "template": {
            "outputs": [
            {
            "simpleText": {
               "text": "테스트 텍스트"
                    }
                }
            ]
                }
            }
	return  jsonify(now_price)

scheduler.add_job(func=print_data, trigger="interval", seconds=3)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())
