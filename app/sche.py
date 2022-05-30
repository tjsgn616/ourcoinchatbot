import time
from apscheduler.schedulers.blocking import BlockingScheduler
#from . import KRW
#from . import jobs 
from . import top5
sched = BlockingScheduler(timezone='Asia/Seoul')

# 매일 12시 30분에 실행
@sched.scheduled_job('interval', seconds=10, id='test_1')
def job1():
    #KRW.func_9()
    print(f'job1 : {time.strftime("%H:%M:%S")}')


# 매일 12시 30분에 실행
#@sched.scheduled_job('interval', seconds=10, id='test_2')
@sched.scheduled_job('cron', minutes='2', id='test_2')
def job2():
    top5.si()
    #print(f'job2 : {time.strftime("%H:%M:%S")}')

# 이런식으로 추가도 가능. 매분에 실행

#sched.add_job(job2, 'cron', second='0', id="test_3")


print('sched before~')
sched.start()
print('sched after~')