import requests
import pandas as pd
import csv
import os

# Get the volatility of all pair of assets.


# To prevent pushing the values by mistakes on a public repo
base_url = os.environ["JUMP_BASE_URL"]
auth = (os.environ["JUMP_USER"], os.environ["JUMP_PWD"])

# Read all assets that have a value (all other are dropped)
# and only keep their id (they will be directly refered with that)
ids = sorted(pd.read_csv("dataset/assets.csv").dropna(subset=["value"])["id"].values.tolist())

ratio = 10

reponse = requests.post(
    base_url + "/ratio/invoke",
    auth=auth,
    data="""{{
        ratio=[{}],
        asset={},
        start_date=2013-06-14,
        end_date=2019-05-31,
        frequency=null
    }}""".format(ratio, ids))

content = reponse.json()

for column, convert_function in [
    ("volatility", lambda x: str(float(x) / 100)),
    ("volatility_percent", lambda x: x)
]:
    with open("dataset/{}.csv".format(column), "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id", column])


        for _id in ids:
            writer.writerow([
                _id,
                convert_function(content[str(_id)][str(ratio)]["value"].replace(",", "."))
            ])