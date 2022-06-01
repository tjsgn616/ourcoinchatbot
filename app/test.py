import pandas as pd
from sqlalchemy import create_engine    # DB 접속 엔진을 만들어준다.
host = 'ec2-54-157-79-121.compute-1.amazonaws.com'
user = 'etdrsbuvfkhhee'
password = 'e65424e293a012117389160f4f259d5325da7c65962e14cc0a6193efda84391a'
db = 'd5c17nuarv857h'

# PostgreSQL 데이터베이스 접속 엔진 생성.
local_postgresql_url = "postgresql://etdrsbuvfkhhee:e65424e293a012117389160f4f259d5325da7c65962e14cc0a6193efda84391a@ec2-54-157-79-121.compute-1.amazonaws.com:5432/d5c17nuarv857h"
# "postgresql://user:password@localhost:5432/DB명"

# localhost의 812 포트를 Parallels에 설치된 PostgreSQL 5432 포트로 포트포워딩.
engine_postgresql = create_engine(local_postgresql_url)


df = pd.read_csv("./app/data/market_list.csv") # 데이터 불러오기
# 되는거 확인 top 파일을 import 해서 가져오면 될듯

df.to_sql(name = 'test',
          con = engine_postgresql,
          schema = 'public',
          if_exists = 'append',
          index = False
          )

## 저장 구문

## 출력 구문

import pandas.io.sql as psql

import psycopg2

 

connection = psycopg2.connect(host='ec2-54-157-79-121.compute-1.amazonaws.com', dbname='d5c17nuarv857h', user='etdrsbuvfkhhee', password='e65424e293a012117389160f4f259d5325da7c65962e14cc0a6193efda84391a')

result = psql.read_sql("SELECT * FROM test;", connection) # 괄호안에 SQL 구문 써주면 될듯.. 테이블 읽는 구문도 있던걸로 아는데

print(result)

