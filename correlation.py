import requests
import pandas as pd
import csv
import os

# Get the correlation of all pair of assets.
# Note that it is not the covariance (need to comûte sharp)

# To prevent pushing the values by mistakes on a public repo
base_url = os.environ["JUMP_BASE_URL"]
auth = (os.environ["JUMP_USER"], os.environ["JUMP_PWD"])

# Read all assets that have a value (all other are dropped)
# and only keep their id (they will be directly refered with that)
ids = sorted(pd.read_csv("dataset/assets.csv").dropna(subset=["value"])["id"].values.tolist())

ratio = 11# Pearson correlation

with open("dataset/correlation.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(["source"] + [str(_id) for _id in ids])

    for current in ids:
        reponse = requests.post(
            base_url + "/ratio/invoke",
            auth=auth,
            data="""{{
                ratio=[{}],
                asset={},
                benchmark={},
                start_date=2013-06-14,
                end_date=2019-05-31,
                frequency=null
            }}""".format(ratio, ids, current))

        content = reponse.json()
        writer.writerow([current] + [
            # The application doesn't return 1.0 for same id
            1.0 if _id == current else content[str(_id)][str(ratio)]["value"].replace(",", ".") for _id in ids

        ])