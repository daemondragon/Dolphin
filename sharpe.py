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
ids = sorted(pd.read_csv("dataset/assets.csv").dropna(subset=["id"])["id"].values.tolist())

ratio = 12

with open("dataset/sharpe.csv", "w", newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["id","sharpe"])

    reponse = requests.post(
        base_url + "/ratio/invoke",
        auth=auth,
        data="""{{
            ratio=[{}],
            asset={},
            benchmark={},
            startDate=2013-06-14,
            endDate=2013-06-14,
            frequency=null
        }}""".format(ratio, ids, ids[0]))
    content = reponse.json()
    for _id in ids:
        writer.writerow([_id] + [content[str(_id)][str(ratio)]["value"].replace(",", ".") ])