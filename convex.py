import numpy as np
import utils

def convex_pool(assets,
                nb_iters=100,
                steps=0.005,
                max_weight=0.1,
                stock_ratio=0.5,
                learning_rate=0.1):
    # The used portfolio in the function is always as a ratio of the liquidity (weights * values)

    def normalize(portfolio):
        # Hard limit on the number of times to normalize to prevent
        # Computation times being too big.
        for _ in range(0, 10):

            for kind, ratio in [
                ("STOCK", stock_ratio),
                ("FUND", 1 - stock_ratio),
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

            # Normalize everything to be
            #portfolio = np.clip(portfolio, 0, max_weight)
            #portfolio /= portfolio.sum()

            if len(np.argwhere(portfolio[correct_assets_index] > max_weight)) == 0:
                break# Nothing more to normalize

        return portfolio


    def derivate(portfolio):
        derivate_portfolio = np.zeros(portfolio.shape)
        for i in range(len(derivate_portfolio)):
            derivate_portfolio[i] = (# Centered derivate
                utils.value_sharpe(assets, normalize(portfolio + np.identity(len(derivate_portfolio))[i] * steps)) -
                utils.value_sharpe(assets, normalize(portfolio - np.identity(len(derivate_portfolio))[i] * steps))
            ) / (2 * steps)

        return derivate_portfolio

    # Create the default portfolio
    n = len(assets["info"])
    portfolio = normalize(np.full((n,), 1 / n))

    # Early stopping if needed
    previous_sharpe = utils.value_sharpe(assets, portfolio)
    # Keep the best portfolio currently computed
    top_portfolio = portfolio

    for i in range(nb_iters):
        print("iter: {}, sharpe: {}".format(i, previous_sharpe))
        portfolio = normalize(portfolio + learning_rate * derivate(portfolio))

        current_sharpe = utils.value_sharpe(assets, portfolio)
        if previous_sharpe == current_sharpe:
            # No more thing to optmize
            break
        elif current_sharpe > utils.value_sharpe(assets, top_portfolio):
            # Keep the best portfolio
            top_portfolio = portfolio
        previous_sharpe = current_sharpe

    # Must be before the top_portfolio change
    sorted_index = np.flip(np.argsort(top_portfolio))

    # All the index by importance, and the created portfolio if a base point is needed.
    return (sorted_index, top_portfolio)

assets = utils.load_assets()

index, portfolio = convex_pool(assets, nb_iters=10, stock_ratio=0.52, learning_rate=1)

utils.value_describe(assets, portfolio)
print(utils.value_sharpe(assets, portfolio))
print(utils.value_portfolio_is_valid(assets, portfolio))