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
    PMA = np.sum(close)/(period + 1)
    PMA = PMA.iat[0]

    return form_b(PMA)
    
def equity_corr(ticker1,ticker2,period):
    import Data_Funcs as df
    import pandas as pd
    import numpy as np

    pd.set_option('display.max_rows', None)  
    pd.set_option('display.max_columns', None)

    equityone = df.equity_data(ticker1,period)
    equitytwo = df.equity_data(ticker2,period)
    equityone = equityone["Close"]
    equitytwo = equitytwo["Close"]

    combined_df = equityone.join(equitytwo, lsuffix = ticker1,rsuffix = ticker2)
    corr_matrix = combined_df.corr()

    return corr_matrix
