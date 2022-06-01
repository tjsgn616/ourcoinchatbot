import pandas as pd
from sqlalchemy import create_engine
import pandas.io.sql as psql

import psycopg2    


host = 'ec2-54-157-79-121.compute-1.amazonaws.com'
user = 'etdrsbuvfkhhee'
password = 'e65424e293a012117389160f4f259d5325da7c65962e14cc0a6193efda84391a'
db = 'd5c17nuarv857h'


## 출력 구문


def test():

    connection = psycopg2.connect(host='ec2-54-157-79-121.compute-1.amazonaws.com', dbname='d5c17nuarv857h', user='etdrsbuvfkhhee', password='e65424e293a012117389160f4f259d5325da7c65962e14cc0a6193efda84391a')

    result = psql.read_sql("SELECT * FROM ;", connection) # 괄호안에 SQL 구문 써주면 될듯.. 테이블 읽는 구문도 있던걸로 아는데

    return(result)

