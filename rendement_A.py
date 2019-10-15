import requests
import json
import csv
import os
import pandas as pd

URL = os.environ["JUMP_BASE_URL"]
AUTH = (os.environ["JUMP_USER"], os.environ["JUMP_PWD"])

ids = sorted(pd.read_csv("assets.csv").dropna(subset=["value"])["id"].values.tolist())

Rend = 9# Pearson correlation

print("Rendement_A.csv")
with open("Rendement_A.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(["source"] + [str(_id) for _id in ids])

    for current in ids:
        payload={'_ratio':[Rend],'_asset':[current],'_becnh':"null",
                 '_startDate':"2013-06-14",
                 '_endDate':"2019-05-31",
                 '_frequency':"null"}

        reponse = requests.post(
            URL + "/ratio/invoke",
            auth=AUTH,
            data="""{{
                ratio=[{}],
                asset={},
                benchmark={},
                startDate=2013-06-14,
                endDate=2019-05-31,
                frequency=null
            }}""".format(Rend, ids, current))

        content = reponse.json()
        writer.writerow([current] + [content[str(_id)][str(Rend)]["value"].replace(",", ".") for _id in ids])
