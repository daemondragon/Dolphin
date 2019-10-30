import pandas as pd
import numpy as np

data = pd.read_csv("dataset/correlation.csv")
volatility = pd.read_csv("dataset/volatility.csv")
id_list = data.columns[1:]

covariance = data.copy()
covariance[id_list] = covariance[id_list].apply(lambda x: x * volatility["volatility"].values, axis=0)
covariance[id_list] = covariance[id_list].apply(lambda x: x * volatility["volatility"].values, axis=1)

covariance.to_csv("dataset/covariance.csv", index=False)