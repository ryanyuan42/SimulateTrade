from WindPy import *
import os
import datetime
import pandas as pd
import re
w.start()
# res = w.wsd('603996.SH', 'open, high, low, close, volume', '2007-01-01', '2017-10-07', 'unit=1;PriceAdj=B')
BASEPATH = os.path.dirname(__file__)

with open('tickers') as f:
    tickers = f.read().strip().split(',')


def ts_from_wind(wind_res):
    df = dict()
    df['Times'] = wind_res.Times

    if wind_res.ErrorCode:
        return
    i = 0
    for field in wind_res.Codes:
        df[field] = wind_res.Data[i]
        i += 1
    return pd.DataFrame(df).set_index('Times')


def update_basic_market_data():
    fields = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
    for field in fields:
        filename = os.path.join(BASEPATH, 'data/' + field + '.csv')
        df = pd.read_csv(filename).set_index('Times')
        date = re.search(r'\d{4}-\d{2}-\d{2}', df.index[-1]).group()
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        new_df = []
        for ticker in df.columns[:2]:
            res = w.wsd(ticker, field.lower(), date, today, "unit=1;PriceAdj=B")
            dataframe = ts_from_wind(res)
            if dataframe is None:
                print('Something went wrong here, ', ticker)
                print(res)
                break
            else:
                # remove the first date because it already exists
                dataframe = dataframe.drop(dataframe.index[0])
                new_df.append(dataframe)
                print(ticker)
        new_df = pd.concat(new_df, axis=1)
        updated_df = pd.concat(df, new_df)
        updated_df.to_csv(filename)
    return

update_basic_market_data()
