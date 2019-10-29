import requests
import csv
import os
import utils
import numpy as np

# Compute the sharpe coefficient of pushed portfolio
# to be able to compare them easily if needed.

def correct_float(value):
    return value.replace(",", ".")

# To prevent pushing the values by mistakes on a public repo
base_url = os.environ["JUMP_BASE_URL"]
auth = (os.environ["JUMP_USER"], os.environ["JUMP_PWD"])

assets = utils.load_assets()

for portfolio_id in [1822]:
    url = base_url + "/portfolio/{}/dyn_amount_compo".format(portfolio_id)
    content = requests.get(url, auth=auth).json()

    portfolio = np.zeros((len(assets["info"]),))
    for asset in content["values"]["2013-06-14"]:
        portfolio[utils.asset_id_to_index(assets, asset["asset"]["asset"])] = asset["asset"]["quantity"]

    print("{}: {} (is_valid: {})".format(
        content["label"],
        utils.sharpe(assets, portfolio),
        utils.portfolio_is_valid(assets, portfolio)

    ))
