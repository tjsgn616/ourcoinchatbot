import pyupbit
a = pyupbit.get_ohlcv('KRW-CRE', interval="minute60", to=0, count=1)
print(a)