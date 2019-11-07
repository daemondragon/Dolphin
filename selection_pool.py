import numpy as np
import pandas as pd
import csv
from utils import load_assets, asset_id_to_index
import utils

""""
return a list of JUMP_ID of size:size_pool of the
best assets sorted by sharpe with exactly stock_nb stocks
"""

def get_pool( val_ref = 1000000, size_pool=30, stock_nb= 20):
    full_assets = load_assets()
    assets = full_assets["info"][["id","type","sharpe","value"]]

    assets = assets.sort_values("sharpe", 0, ascending=False)

    fund = assets.loc[assets["type"] == "FUND"].head(size_pool- stock_nb)
    stock = assets.loc[assets["type"] == "STOCK"].head(stock_nb)
    print(stock)
    print()
    print(fund)
    print()
    pool= fund["id"].values.tolist() + stock["id"].values.tolist()

    portfolio = np.zeros(len(full_assets["info"]))

    for id in pool:

        val = float(assets[assets.id == int(id)].iloc[0].iloc[0])
        portfolio[asset_id_to_index(full_assets,id)] = int((1/size_pool)*val_ref /val)

    return portfolio


print(get_pool())