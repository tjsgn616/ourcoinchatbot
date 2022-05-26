from apscheduler.schedulers.background import BackgroundScheduler
schedule = BackgroundScheduler()

def CheckPrice():
    print("Running")

schedule.add_job(id= "Tracker",func = CheckPrice,trigger='interval',hours = 1)
schedule.start()

