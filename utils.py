import pandas as pd
import os.path
import assets as base_asssets
import numpy as np
import math

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

def portfolio_is_valid(assets, portfolio):
    # So that unit instead of ratio can be passed if wanted
    normalized_portfolio = portfolio / portfolio.sum()

    assets_values = portfolio * assets["info"]["value"]
    stocks_index = np.where(assets["info"]["type"] == "STOCK")[0]

    return np.all(# Correct ratio range
        np.vectorize(
            lambda value: value == 0.0 or (0.01 <= value and value <= 0.1)
        )(portfolio)
    ) and (# Correct number of assets
        15 <= np.count_nonzero(portfolio) and np.count_nonzero(portfolio) <= 40
    ) and (# Enough ratio of stocks (in value)
        assets_values[stocks_index].sum() / assets_values.sum() >= 0.5
    )

def sharpe(assets, portfolio):
    # So that unit instead of ratio can be passed if wanted
    normalized_portfolio = portfolio / portfolio.sum()

    no_risk = 0.0005# 0.05% (source Fiche Technique)

    Rp = (normalized_portfolio * assets["info"]["rendement"]).sum() - no_risk

    # If the i == j case must not be included in the volatility computation,
    # decomment the end of the next lign.
    mask = np.ones((len(portfolio), len(portfolio)))#1 - np.identity(len(portfolio))

    # stack the portofolio weight n times to easily compute the sharpe ratio
    W = np.repeat(portfolio[:,np.newaxis], len(portfolio), axis=1)
    Vp_2 = (W * W.T * assets["covariance"] * mask).sum()# Compute everything at once
    return Rp / math.sqrt(Vp_2)


#assets = load_assets()
#print(asset_id_to_index(assets, 2122))
#print(index_to_asset_id(assets, 3))
# Warning: Invalid portfolio, don't push it
#portfolio = portfolio_pool_from_id_list(assets, [1845,1846,2122,2123,2124,1428,1847,1848,1849,2154,1429,2063,1430,2064,1431,1858,1433])
#print(portfolio_pool_from_id_list(assets, [1, 2, 3]))
#print(portfolio)
#print(portfolio_is_valid(assets, portfolio))
#print(sharpe(assets, portfolio))