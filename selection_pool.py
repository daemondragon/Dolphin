import pandas as pd
import csv



""""
return a list of JUMP_ID of size:size_pool of the 
best assets sorted by sharpe with exactly stock_nb stocks
"""

def get_pool( size_pool = 20, stock_nb= 5):
    #get all the relevant data from CSVs files
    assets_ = pd.read_csv("dataset/assets.csv")
    sharpe_ = pd.read_csv("dataset/sharpe.csv")
    assets = pd.merge(assets_, sharpe_, on="id",)
    assets = assets[["id","type","sharpe"]]

    assets = assets.sort_values("sharpe", 0, ascending=False)

    fund = assets.loc[assets["type"] != "STOCK"].head(size_pool- stock_nb)
    stock = assets.loc[assets["type"] == "STOCK"].head(stock_nb)

    pool= fund["id"].values.tolist() + stock["id"].values.tolist()

    print(pool)
    return pool

