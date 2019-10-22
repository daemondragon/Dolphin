import pandas as pd

# return a dataframe with all the data specified in options
# return the dataframe of the assets file merged with filename in options
def load_assets_list(assets_path = "dataset/", files=None):
    if files is None:
        files = []
    assets = pd.read_csv(assets_path + "assets.csv")
    for file in files:
        assets = pd.merge(assets, pd.read_csv(assets_path + file), on="id")
    return assets

def load_assets_part(sharpe = False, volatility = False, rend = False):
    list = []
    if sharpe:
        list += "sharpe.csv"
    if volatility:
        list += "volatility.csv"
    if rend:
        list+= "rendement_A.csv"
    return load_assets(files= list)

def load_assets(assets_path = "dataset/"):
    assets = load_assets_list(assets_path = assets_path, files = ["sharpe.csv","volatility.csv","rendement_A.csv"])
    return assets

print(load_assets())