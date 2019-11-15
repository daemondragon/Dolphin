import requests
import csv
import os
import utils
import numpy as np

# To prevent pushing the values by mistakes on a public repo
base_url = os.environ["JUMP_BASE_URL"]
auth = (os.environ["JUMP_USER"], os.environ["JUMP_PWD"])

assets = utils.load_assets()

for portfolio_id in [1822, 2201]:
    url = base_url + "/portfolio/{}/dyn_amount_compo".format(portfolio_id)
    content = requests.get(url, auth=auth).json()

    portfolio = np.zeros((len(assets["info"]),))
    date = "2013-06-14"
    if date not in content["values"]:
        print(content)

    for asset in content["values"][date]:
        portfolio[utils.asset_id_to_index(assets, asset["asset"]["asset"])] = asset["asset"]["quantity"]

    print("{}: {} (is_valid: {}) (server value: {})".format(
        content["label"],
        utils.quantity_sharpe(assets, portfolio),
        utils.quantity_portfolio_is_valid(assets, portfolio),
        utils.invoke_ratios([utils.Ratio.SHARPE, utils.Ratio.RENDEMENT, utils.Ratio.VOLATILITY])
    ))

    utils.quantity_describe(assets, portfolio)