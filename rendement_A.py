import requests
import json
import csv
import os
import pandas as pd

URL = os.environ["JUMP_BASE_URL"]
AUTH = (os.environ["JUMP_USER"], os.environ["JUMP_PWD"])

ids = sorted(pd.read_csv("dataset/assets.csv").dropna(subset=["value"])["id"].values.tolist())

Rend = 9# Pearson correlation

print("rendement_A.csv")
with open("dataset/rendement_A.csv", "w", newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["id" , "rendement"])

    reponse = requests.post(
        URL + "/ratio/invoke",
        auth=AUTH,
        data="""{{
            ratio=[{}],
            asset={},
            benchmark={},
            start_date=2013-06-14,
            end_date=2019-04-18,
            frequency=null
        }}""".format(Rend, ids,  ids[0]))

    content = reponse.json()
    for _id in ids:
        writer.writerow([_id] + [content[str(_id)][str(Rend)]["value"].replace(",", ".")])