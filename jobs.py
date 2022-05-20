from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('cron', seconds='5')
def print_data():
	print("Have a good day!")



sched.start()