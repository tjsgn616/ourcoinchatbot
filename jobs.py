from apscheduler.schedulers.blocking import BlockingScheduler
import time
sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=5)
def print_data():
	print(f'job1 : {time.strftime("%H:%M:%S")}')



sched.start()