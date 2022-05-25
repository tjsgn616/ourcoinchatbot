import pandas as pd
df = pd.read_csv("output.csv",encoding='CP949', sep=",")
df.reset_index(inplace=True)
#test = pd.DataFrame(test, index=True)
print(type(df))
print(df.loc[25])
#test.head()
print(df)