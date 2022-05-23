import pandas as pd
import json
csv_data = pd.read_csv("top5_coin.csv", sep = ",")
csv_data.to_json("test.json", orient = "records")
with open('test.json', 'r') as f:

    json_data = json.load(f)

#print(json.dumps(json_data) )

k5_price = json_data[0]['market']
print(k5_price)

