from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask



app = Flask(__name__)

@app.route('/msg4', methods=['POST'])
def home():
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
	return  (now_price)

    
def sensor():
    print("Scheduler is alive!")
    home()
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(sensor, "interval", seconds=3)
scheduler.start()