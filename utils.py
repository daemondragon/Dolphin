import pandas as pd
import numpy as np
import requests
import math
import os

def load_assets(assets_path = "dataset/"):
    assets = pd.read_csv(assets_path + "assets.csv").dropna(subset=["value"])

    # Add all other values to the assets
    for file in [
        "sharpe.csv",
        "volatility.csv", "volatility_percent.csv",
        "rendement.csv", "rendement_percent.csv",
        "rendement_A.csv", "rendement_A_percent.csv"
    ]:
        assets = pd.merge(assets, pd.read_csv(assets_path + file), on="id")

    # Convert all values to EUR
    rate = pd.read_csv(assets_path + "euros_rate.csv")
    assets["value"] = assets.apply(lambda row: float(rate[rate["source"] == row["currency"]]["rate"] * row["value"]), axis=1)
    assets = assets.drop(columns="currency")# Remove this columns as it is useless now

    result = { "info": assets }

    for name in ["covariance", "covariance_percent"]:
        result[name] = pd.read_csv("{}{}.csv".format(assets_path, name)).drop(columns="source").values

    return result

def asset_id_to_index(assets, asset_id):
    return np.where(assets["info"]["id"] == asset_id)[0][0]

def index_to_asset_id(assets, index):
    return assets["info"]["id"].values[index]

def portfolio_pool_from_id_list(assets, assets_id_list):
    assets_index_list = [ asset_id_to_index(assets, asset_id) for asset_id in assets_id_list ]

    portfolio = np.zeros(len(assets["info"]))
    portfolio[assets_index_list] = 0.01 # 1%

    # sort the STOCK first, and the FUND after.
    # The stocks are ordered by decreasing value
    # The fund are ordered by increasing value
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
    """
    Compute the sharpe coefficient of a portfolio
    where each value in the array represent the quantity of assets
    """

    # So that unit instead of ratio can be passed if wanted
    normalized_portfolio = portfolio / portfolio.sum()

    no_risk = 0.00005# 0.005% (Fiche Technique say 0.05%, but the sharpe becone wrong)

    Rp = (normalized_portfolio * assets["info"]["rendement_A"]).sum() - no_risk

    # stack the portfolio weight n times to easily compute the sharpe ratio
    W = np.repeat(normalized_portfolio[:,np.newaxis], len(normalized_portfolio), axis=1)
    Vp_2 = (W * W.T * assets["covariance"]).sum()# Compute everything at once
    Vp = math.sqrt(Vp_2)

    #print(Rp + no_risk, Vp)
    return Rp / Vp

def push_value_portfolio(assets, portfolio):
    return push_quantity_portfolio(assets, portfolio / assets["info"]["value"].values)

def push_quantity_portfolio(assets, portfolio):
    """
    Expect a quantity portfolio, not a valued one.
    """

    # Correctly convert the portfolio to the unit version
    # so that the constraint on the portfolio is correct
    portfolio = to_unit(portfolio)

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

    for _ in range(2):
        # Need to be pushed twice to update the ratio computation
        response = requests.put(url, auth=auth, data=entity)

    return (response.status_code / 100) == 2 # 200-like response code

def to_unit(portfolio):
    """
    Transform a portfolio of either value or quantity
    into and unit equivalent by multiplying by 10 the portfolio
    while the resulting result is still equivalent.
    This can be done as there is no limit on the amount of assets that can
    be returned.
    """

    previous_portfolio = portfolio
    new_portfolio = previous_portfolio * 10
    while not np.array_equal(np.round(new_portfolio), new_portfolio) and np.allclose(portfolio / portfolio.sum(), new_portfolio / new_portfolio.sum()):
        previous_portfolio, new_portfolio = new_portfolio, new_portfolio * 10

    return np.round(previous_portfolio).astype(int)

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

        print("\nASSET: {} {} ({:.2f}%)".format(len(important_index), kind, portfolio[important_index].sum() / portfolio.sum() * 100))

        for index in important_index:
            final_value = portfolio[index]
            value = assets["info"]["value"][index]
            quantity = final_value / value

            print("- {} {} quantity {} * value {:9.9f} = {:9.9f} ({:.5f}%)".format(
                assets["info"]["id"][index],
                nice_name(assets["info"]["name"][index], 20),
                quantity, value, final_value, final_value / portfolio.sum() * 100
            ))