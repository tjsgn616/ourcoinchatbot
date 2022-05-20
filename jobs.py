from apscheduler.schedulers.blocking import BlockingScheduler
from helper import your_function_a, your_function_b

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes='1')
def print_data():
	print("Have a good day!")

@sched.scheduled_job('cron', day_of_week='sat-sun', hour='8-14', minute='0-59/10')
def update_a():
 	your_function_a()

@sched.scheduled_job('cron', day_of_week='fri', hour='15-19/2')
def update_b():
 	your_function_b()

sched.start()