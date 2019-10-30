import pandas as pd
import numpy as np
import requests
import math
import os

def load_assets(assets_path = "dataset/"):
    assets = pd.read_csv(assets_path + "assets.csv").dropna(subset=["value"])

    # Add all other values to the assets
    for file in ["sharpe.csv", "volatility.csv", "rendement_A.csv"]:
        assets = pd.merge(assets, pd.read_csv(assets_path + file), on="id")

    # Convert all values to EUR
    rate = pd.read_csv(assets_path + "euros_rate.csv")
    assets["value"] = assets.apply(lambda row: float(rate[rate["source"] == row["currency"]]["rate"] * row["value"]), axis=1)
    assets = assets.drop(columns="currency")# Remove this columns as it is useless now

    covariance = pd.read_csv(assets_path + "covariance.csv").drop(columns="source").values

    return {
        "info": assets,
        "covariance": covariance
    }

def asset_id_to_index(assets, asset_id):
    return np.where(assets["info"]["id"] == asset_id)[0][0]

def index_to_asset_id(assets, index):
    return assets["info"]["id"].values[index]

def portfolio_pool_from_id_list(assets, assets_id_list):
    assets_index_list = [ asset_id_to_index(assets, asset_id) for asset_id in assets_id_list ]

    portfolio = np.zeros(len(assets["info"]))
    portfolio[assets_index_list] = 0.01 # 1%

    # sort the STOCK first, and the FUND after.
    # The stocks are ordered by decreasing rendement
    # The fund are ordered by increasing rendement
    # Max to 10% in the list ordered while 100% are not yet reached.
    # Doing it in this order allows to makes sure that the %NAV contraints are respected,
    # while maximising the chance that at least 50% of portfolio values are in STOCK

    def asset_key(asset_index):
        # Create the correct key so that they are ordered as wanted
        asset = assets["info"].iloc[asset_index]
        return (
            {"STOCK": 0, "FUND": 1}[asset["type"]],
            -asset["value"] if asset["type"] == "STOCK" else asset["value"]
        )

    current_weight = len(assets_index_list) * 0.01
    for index in sorted(assets_index_list, key=asset_key):
        to_add = min(0.09, 1 - current_weight)# Add 9% to 1% to go to 10% (the maximum authorized)
        if to_add <= 0.0:
            break

        portfolio[index] += to_add
        current_weight += to_add

    return portfolio

def quantity_portfolio_is_valid(assets, portfolio):
    return value_portfolio_is_valid(assets, portfolio * assets["info"]["value"])

def value_portfolio_is_valid(assets, portfolio):
    # So that unit instead of ratio can be passed if wanted
    normalized_portfolio = portfolio / portfolio.sum()
    stocks_index = np.where(assets["info"]["type"] == "STOCK")[0]

    correct = [
        # Correct ratio range
        np.all(
            np.vectorize(
                lambda value: value == 0.0 or (0.01 <= value and value <= 0.1)
            )(normalized_portfolio)
        ),

        # Correct number of assets
        15 <= np.count_nonzero(normalized_portfolio) and np.count_nonzero(normalized_portfolio) <= 40,

        # Enough ratio of stocks (in value)
        normalized_portfolio[stocks_index].sum() / normalized_portfolio.sum() >= 0.5
    ]

    print(correct)
    return all(correct)


def quantity_sharpe(assets, portfolio):
    """
    Compute the sharpe coefficient of a portfolio
    where each value in the array represent the quantity of assets
    """
    return value_sharpe(assets, portfolio * assets["info"]["value"])


def value_sharpe(assets, portfolio):
    # So that unit instead of ratio can be passed if wanted
    normalized_portfolio = portfolio / portfolio.sum()

    no_risk = 0.00005# 0.005% (Fiche Technique donne 0.05%, mais le sharpe est alors faux)

    Rp = (normalized_portfolio * assets["info"]["rendement"]).sum() - no_risk

    # If the i == j case must not be included in the volatility computation,
    # decomment the end of the next lign.
    mask = np.ones((len(normalized_portfolio), len(normalized_portfolio)))
    #mask = 1 - np.identity(len(normalized_portfolio))

    # stack the portfolio weight n times to easily compute the sharpe ratio
    W = np.repeat(normalized_portfolio[:,np.newaxis], len(normalized_portfolio), axis=1)
    Vp_2 = (W * W.T * assets["covariance"] * mask).sum()# Compute everything at once

    #print((normalized_portfolio * assets["info"]["rendement"]).sum(), math.sqrt(Vp_2))
    return Rp / math.sqrt(Vp_2)

def push_portfolio(assets, portfolio):
    """
    Expect a quantity portfolio, not a valued one.
    """
    base_url = os.environ["JUMP_BASE_URL"]
    auth = (os.environ["JUMP_USER"], os.environ["JUMP_PWD"])

    portfolio_id = 1822
    portfolio_label = "EPITA_PTF_3"

    url = base_url + "/portfolio/{}/dyn_amount_compo".format(portfolio_id)
    entity="""{{
        "label":"EPITA_PTF_3",
        "currency":{{"code":"EUR"}},
        "type":"front",
        "values":{{ "2013-06-14": [{}] }}
    }}""".format(",".join([
        """{{
            "asset": {{
                "asset":{},
                "quantity":{}
            }}
        }}""".format(
            index_to_asset_id(assets, index)[0],
            portfolio[index][0]
        ) for index in np.argwhere(portfolio)
    ]))

    response = requests.put(url, auth=auth, data=entity)
    print(response)


def quantity_describe(assets, portfolio):
    return value_describe(assets, portfolio * assets["info"]["value"].values)

def value_describe(assets, portfolio):
    """
    print information about the portfolio in a lisible way for the user.
    """

    def nice_name(name, amount):
        if len(name) <= amount:
            return name + (" " * (amount - len(name)))
        else:
            return name[:amount - 3] + "..."

    for kind in ["STOCK", "FUND"]:
        important_index = np.where(assets["info"]["type"] == kind)[0]
        important_index = np.intersect1d(
            important_index,
            np.nonzero(portfolio)[0],
            assume_unique=True
        )
        important_index = np.flip(important_index[np.argsort(portfolio[important_index])])

        print("\nASSET: {} ({})".format(kind, len(important_index)))

        for index in important_index:
            final_value = portfolio[index]
            value = assets["info"]["value"][index]
            quantity = final_value / value

            print("- {} {} quantity {} * value {} = {}".format(
                assets["info"]["id"][index],
                nice_name(assets["info"]["name"][index], 20),
                quantity, value, final_value
            ))