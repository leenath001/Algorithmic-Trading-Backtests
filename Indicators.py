def simple_moving_average(ticker,period):
    ## moving average function based on close data
    import warnings
    warnings.filterwarnings("ignore")
    import numpy as np
    import Data_Funcs as df
    import pandas as pd

    def form_b(num):
        return f"{num:.2f}"

    data = df.equity_data(ticker, period)
    close = data.loc[:,'Close']
    PMA = np.sum(close)/period
    PMA = PMA.iat[0]

    return form_b(PMA)

