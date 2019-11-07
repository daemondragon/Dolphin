import pandas as pd
import numpy as np

data = pd.read_csv("dataset/correlation.csv")

for suffix in ["", "_percent"]:
    volatility = pd.read_csv("dataset/volatility{}.csv".format(suffix))
    id_list = data.columns[1:]

    covariance = data.copy()
    covariance[id_list] = covariance[id_list].apply(lambda x: x * volatility["volatility{}".format(suffix)].values, axis=0)
    covariance[id_list] = covariance[id_list].apply(lambda x: x * volatility["volatility{}".format(suffix)].values, axis=1)

    covariance.to_csv("dataset/covariance{}.csv".format(suffix), index=False)