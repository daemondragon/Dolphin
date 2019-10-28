import pandas as pd
import os.path
import assets as base_asssets
import numpy as np

# return a dataframe with all the data specified in options
# return the dataframe of the assets file merged with filename in options
def load_assets_list(assets_path = "dataset/", files=None):
    if files is None:
        files = []
    if not os.path.isfile(assets_path + "assets.csv"):
        base_asssets.main()
    assets = pd.read_csv(assets_path + "assets.csv").dropna(subset=["value"])
    for file in files:
        assets = pd.merge(assets, pd.read_csv(assets_path + file), on="id")
    return assets

def load_assets_part(sharpe = False, volatility = False, rend = False):
    list = []
    if sharpe:
        list.append("sharpe.csv")
    if volatility:
        list.append("volatility.csv")
    if rend:
        list.append("rendement_A.csv")
    return load_assets_list(files= list)

def load_assets(assets_path = "dataset/"):
    assets = load_assets_list(assets_path = assets_path, files = ["sharpe.csv","volatility.csv","rendement_A.csv"])
    return assets

# take an id and return the index it should have in a assets pool
def id_to_index(id):
    ids = sorted(pd.read_csv("dataset/assets.csv").dropna(subset=["value"])["id"].values.tolist())
    if id in ids:
        return ids.index(id)
    return -1

# create the pool from a list of id
# to be improved with a map
def pool_from_list(list=[]):
    ids = sorted(pd.read_csv("dataset/assets.csv").dropna(subset=["value"])["id"].values.tolist())
    res = []
    for id in ids:
        res.append(0)
    for el in list:
        res[id_to_index(el)] = 1
    return res

# not finished
def valid_pool(pool):
    for el in pool:
        if el < 0.01 or el > 1:
            return False
    return  True

# take an index and return the corresponding id in a pool
def index_to_id(index):
    ids = sorted(pd.read_csv("dataset/assets.csv").dropna(subset=["value"])["id"].values.tolist())
    return ids[index]

