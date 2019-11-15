import numpy as np
import utils

def convex_pool(assets,
                nb_iters_first=10,
                nb_iters_second=20,
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

                if ratio == 0.0:
                    portfolio[correct_assets_index] = 0.0
                    continue

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
                    if under_sum != 0:
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

    def index_derivate(portfolio, index):
        """
        Compute the derivate of a single index in the portfolio
        """
        return (# Centered derivate
            utils.value_sharpe(assets, normalize(portfolio + np.identity(len(portfolio))[index] * steps)) -
            utils.value_sharpe(assets, normalize(portfolio - np.identity(len(portfolio))[index] * steps))
        ) / (2 * steps)

    def derivate(portfolio):
        """
        Get the global derivate of the portfolio for the first step
        of the convex pool generation.
        """
        derivate_portfolio = np.zeros(portfolio.shape)
        for i in range(len(derivate_portfolio)):
            derivate_portfolio[i] = index_derivate(portfolio, i)

        return derivate_portfolio

    def single_derivate(portfolio):
        """
        Get only one derivate of the portfolio for the second
        step of the convex pool generation.
        Only portfolio index with non zero value will have their derivate
        computated, as the zero one have already been excluded of the pool.

        The returned derivate only included one index, that is either:
        - the most important (24/20)
        - one random (24/13)
        """
        derivate_portfolio = np.zeros(portfolio.shape)
        for i in range(len(derivate_portfolio)):
            if portfolio[i] > 0.0:
                derivate_portfolio[i] = index_derivate(portfolio, i)

        derivate_portfolio[np.random.permutation(np.nonzero(derivate_portfolio))[1:]] = 0.0
        return derivate_portfolio

    def iterate(nb_iters, portfolio, derivate_funtion):
        top_portfolio, top_portfolio_sharpe = portfolio, utils.value_sharpe(assets, portfolio)
        previous_sharpe = top_portfolio_sharpe

        print("starting: {}".format(top_portfolio_sharpe))

        for i in range(nb_iters):
            portfolio = normalize(portfolio + learning_rate * derivate_funtion(portfolio))
            current_sharpe = utils.value_sharpe(assets, portfolio)

            print("iter {}: {}".format(i, current_sharpe))
            if current_sharpe > top_portfolio_sharpe:
                top_portfolio, top_portfolio_sharpe = portfolio, current_sharpe
            if previous_sharpe == current_sharpe:
                break#Nothing more to optimize
            previous_sharpe = current_sharpe

        return top_portfolio

    # Create the default portfolio
    n = len(assets["info"])
    portfolio = normalize(np.full((n,), 1 / n))

    portfolio = iterate(nb_iters_first, portfolio, derivate)
    #utils.value_describe(assets, portfolio)
    portfolio = iterate(nb_iters_second, portfolio, single_derivate)
    #utils.value_describe(assets, portfolio)

    # All the index that must be used and
    # the created portfolio if a base point is needed.
    return (np.nonzero(portfolio), portfolio)

assets = utils.load_assets()

#for ratio in [0.52, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.0]:
index, portfolio = convex_pool(
    assets,
    nb_iters_first=10,
    nb_iters_second=20,
    stock_ratio=1.0,#Best one found yet (2.634313242669 of sharpe, and is valid)
    learning_rate=1
)

utils.push_value_portfolio(assets, portfolio)

print("{} (local: {} | is_valid: {}): {}".format(
    ratio,
    utils.value_sharpe(assets, portfolio),
    utils.value_portfolio_is_valid(assets, portfolio),
    utils.invoke_ratios([utils.Ratio.SHARPE])
))

#utils.value_describe(assets, portfolio)