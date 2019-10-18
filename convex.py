import numpy as np

def convex_pool(data, nb_iters=100, steps=0.005, max_weight=0.1, asset_ratio=0.5):

    def normalize(portfolio):
        for kind, ratio in [
            (0, asset_ratio),
            #(0, 1 - asset_ratio),
        ]:
            correct_assets_index = range(len(data))#np.argwhere(data == kind)

            while True:
                portfolio = np.clip(portfolio, 0, max_weight)

                under_index = np.intersect1d(
                    correct_assets_index,
                    np.argwhere(portfolio < max_weight),
                    assume_unique=True
                )

                sum_under = portfolio[under_index].sum()

                print(sum_under)

                if sum_under != 0:
                    print(portfolio)
                    portfolio[under_index] *= ratio / sum_under
                    print(portfolio)

                if len(np.argwhere(portfolio[correct_assets_index] > max_weight)) == 0:
                    break# Nothing more to normalize

        return portfolio


    def derivate(portfolio):
        derivate_portfolio = np.zeros(portfolio.shape)
        for i in range(len(derivate_portfolio)):
            derivate_portfolio[i] = 0#(
                #sharp(normalize(portfolio + np.identity(len(derivate_portfolio))[i] * steps)) -
                #sharp(normalize(portfolio - np.identity(len(derivate_portfolio))[i] * steps))
            #) / (2 * steps)

        return derivate_portfolio

    portfolio = np.full((len(data),), 1 / len(data))

    for _ in range(nb_iters):
        portfolio -= derivate(portfolio)

convex_pool(np.zeros((20,)), nb_iters=1, asset_ratio=1.0)