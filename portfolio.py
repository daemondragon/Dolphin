import pandas as pd
import math

from selection_pool import get_pool
from utils import load_assets_part
from utils import id_to_index
from utils import  index_to_id

def sharpe(portfolio=[]):
    covariance = pd.read_csv("dataset/covariance.csv")
    rend_list = load_assets_part(rend= True)
    rend = 0.
    vol = 0.
    no_risk = 0.2
    print (covariance)
    print(covariance.at[1,"1428"])
    for i in range(len(portfolio)):
        if not portfolio[i] == 0:
            rend += portfolio[i] * float(rend_list.at[i, "rendement"])
        for j in range(len(portfolio)):
            if not j==i and not portfolio[j] == 0:
                vol+= portfolio[i] * portfolio[j] * float(covariance.at[i, str(index_to_id(j))])
    return (rend - no_risk)/math.sqrt(vol)

sharpe(get_pool())