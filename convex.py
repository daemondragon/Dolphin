import numpy as np
import utils

def convex_pool(assets,
                nb_iters=100,
                steps=0.005,
                max_weight=0.1,
                asset_ratio=0.5):
    # The used portfolio in the function is always as a ratio of the liquidity (weights * values)

    def valued_sharpe(portfolio):
        weighted_portfolio = portfolio / assets["info"]["value"]
        return utils.sharpe(assets, weighted_portfolio / weighted_portfolio.sum())

    def normalize(portfolio):
        # Hard limit on the number of times to normalize to prevent
        # Computation times being too big.
        for _ in range(0, 10):

            for kind, ratio in [
                ("STOCK", asset_ratio),
                ("FUND", 1 - asset_ratio),
            ]:
                portfolio = np.clip(portfolio, 0, max_weight)

                correct_assets_index = np.where(assets["info"]["type"] == kind)[0]
                under_index = np.intersect1d(
                    correct_assets_index,
                    np.argwhere(portfolio < max_weight),
                    assume_unique=True
                )
                full_index = np.setdiff1d(
                    correct_assets_index,
                    under_index,
                    assume_unique=True
                )

                kind_sum = portfolio[correct_assets_index].sum()
                under_sum = portfolio[under_index].sum()
                full_sum = portfolio[full_index].sum()

                # https://stackoverflow.com/questions/18661112/normalize-a-vector-with-one-fixed-value/
                if kind_sum < ratio:
                    # Not enough weight, they will be increasing, so need to prevent 10% from overflowing
                    portfolio[under_index] *= (ratio - full_sum) / under_sum
                else:
                    # Decreasing weight, normalize all the current assets kind
                    portfolio[correct_assets_index] *= ratio / kind_sum

            if len(np.argwhere(portfolio[correct_assets_index] > max_weight)) == 0:
                break# Nothing more to normalize

        return portfolio


    def derivate(portfolio):
        derivate_portfolio = np.zeros(portfolio.shape)
        for i in range(len(derivate_portfolio)):
            derivate_portfolio[i] = (# Centered derivate
                valued_sharpe(normalize(portfolio + np.identity(len(derivate_portfolio))[i] * steps)) -
                valued_sharpe(normalize(portfolio - np.identity(len(derivate_portfolio))[i] * steps))
            ) / (2 * steps)

        return derivate_portfolio

    # Create the default portfolio
    n = len(assets["info"])
    portfolio = normalize(np.full((n,), 1 / n))

    # Early stopping if needed
    previous_sharpe = valued_sharpe(portfolio)
    # Keep the best portfolio currently computed
    top_portfolio = portfolio

    for i in range(nb_iters):
        print("iter: {}, sharpe: {}".format(i, previous_sharpe))
        portfolio = normalize(portfolio + derivate(portfolio))

        current_sharpe = valued_sharpe(portfolio)
        if previous_sharpe == current_sharpe:
            # No more thing to optmize
            break
        elif current_sharpe > valued_sharpe(top_portfolio):
            # Keep the best portfolio
            top_portfolio = portfolio
        previous_sharpe = current_sharpe

    # All the index by importance, and the created portfolio if a base point is needed.
    return (sorted_index, top_portfolio)

assets = utils.load_assets()

convex_pool(assets, nb_iters=10, asset_ratio=0.5)