from apscheduler.schedulers.background import BackgroundScheduler
schedule = BackgroundScheduler()

def CheckPrice():
    print("Running")

schedule.add_job(func = CheckPrice,trigger='interval',minutes = 1)
schedule.start()

