import pandas as pd
import csv
from utils import load_assets
from utils import pool_from_list


""""
return a list of JUMP_ID of size:size_pool of the 
best assets sorted by sharpe with exactly stock_nb stocks
"""

def get_pool( size_pool = 20, stock_nb= 5):
    assets = load_assets()
    assets = assets[["id","type","sharpe"]]

    assets = assets.sort_values("sharpe", 0, ascending=False)

    fund = assets.loc[assets["type"] != "STOCK"].head(size_pool- stock_nb)
    stock = assets.loc[assets["type"] == "STOCK"].head(stock_nb)

    pool= fund["id"].values.tolist() + stock["id"].values.tolist()

    return pool_from_list(pool)

