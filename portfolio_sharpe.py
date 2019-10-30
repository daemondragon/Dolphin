import requests
import csv
import os
import utils
import numpy as np

# To prevent pushing the values by mistakes on a public repo
base_url = os.environ["JUMP_BASE_URL"]
auth = (os.environ["JUMP_USER"], os.environ["JUMP_PWD"])

def invoke_ratio(asset_id):
    response = requests.post(
        base_url + "/ratio/invoke",
        auth=auth,
        data="""{{
            ratio=[9, 10, 12],
            asset=[{}],
            start_date=2013-06-14,
            end_date=2019-05-31,
            frequency=null
        }}""".format(asset_id)).json()

    ratios = [
        {
            { "9":"rendement", "10":"volatility","12":"sharpe" }[ratio_id]:
            {"double": lambda x: x, "percent": lambda x: x / 100 }[
                response[str(asset_id)][ratio_id]["type"]
            ](float(response[str(asset_id)][ratio_id]["value"].replace(",", ".")))
        } for ratio_id in response[str(asset_id)]
    ]

    # Compute the rf as the subject give the wrong one.
    ratios = {key: val for dic in ratios for key, val in dic.items()}
    ratios["rf"] = ratios["rendement"] - ratios["volatility"] * ratios["sharpe"]

    return ratios

assets = utils.load_assets()

for portfolio_id in [1822]:
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
        utils.portfolio_is_valid(assets, portfolio),
        invoke_ratio(portfolio_id)
    ))

    utils.quantity_describe(assets, portfolio)
    #utils.push_portfolio(assets, portfolio)
