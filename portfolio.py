from selection_pool import get_pool
from utils import load_assets_part
from utils import id_to_index

def sharpe(portfolio):
    rend = load_assets_part(rend= True)

    print([id_to_index("2123")])
    print(rend)
    volatility = load_assets_part(volatility=True)

sharpe(get_pool())