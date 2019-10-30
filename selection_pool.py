import pandas as pd
import csv
from utils import load_assets, portfolio_pool_from_id_list
import utils

""""
return a list of JUMP_ID of size:size_pool of the
best assets sorted by sharpe with exactly stock_nb stocks
"""

def get_pool( size_pool = 20, stock_nb= 5):
    full_assets = load_assets()
    assets = full_assets["info"][["id","type","sharpe"]]

    assets = assets.sort_values("sharpe", 0, ascending=False)

    fund = assets.loc[assets["type"] == "FUND"].head(size_pool- stock_nb)
    stock = assets.loc[assets["type"] == "STOCK"].head(stock_nb)

    pool= fund["id"].values.tolist() + stock["id"].values.tolist()

    return portfolio_pool_from_id_list(full_assets, pool)

assets = utils.load_assets()
utils.push_portfolio(assets, get_pool())