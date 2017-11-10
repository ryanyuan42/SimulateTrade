from WindPy import *
import os
import pandas as pd
w.start()
# res = w.wsd('603996.SH', 'open, high, low, close, volume', '2007-01-01', '2017-10-07', 'unit=1;PriceAdj=B')
BASEPATH = 'E:\Python Working Space\SimulateTradeData'

with open('tickers') as f:
    tickers = f.read().strip().split(',')


def ts_from_wind(wind_res):
    df = dict()
    df['Times'] = wind_res.Times

    if wind_res.ErrorCode:
        return
    else:
        i = 0
        for field in wind_res.Fields:
            df[field] = wind_res.Data[i]
            i += 1
        return pd.DataFrame(df).set_index('Times')


def get_basic_market_data():
    panel = dict()
    first = True
    for ticker in tickers:
        res = w.wsd(ticker, 'open, high, low, close, volume', '2007-01-01', '2017-11-09', 'unit=1;PriceAdj=B')
        dataframe = ts_from_wind(res)
        if first:
            fields = res.Fields
            first = False
        if dataframe is None:
            print('Something went wrong here, ', ticker)
            print(res)
        else:
            print(ticker)
    panel = pd.Panel(panel)

    for field in fields:
        panel[:, :, field].to_csv(os.path.join(BASEPATH, 'data/' + field + '.csv'))


def get_fundamental_market_data(factor):
    panel = dict()
    first = True
    for ticker in tickers:
        res = w.wsd(ticker, factor, '2010-01-01', '2017-10-07', "unit=1;ruleType=3;currencyType=;PriceAdj=F;Period=M")
        dataframe = ts_from_wind(res)
        if first:
            fields = res.Fields
            first = False
        if dataframe is None:
            print('Something went wrong here, ', ticker)
            print(res)
        else:
            panel[ticker] = dataframe
            print(ticker)
    panel = pd.Panel(panel)

    for field in fields:
        panel[:, :, field].to_csv(os.path.join(BASEPATH, 'data/' + field + '.csv'))


if __name__ == "__main__":
    # factors = "roe_ttm,pe_ttm,pb,pcf_ocf_ttm,mkt_freeshares,mkt_cap_float,mkt_cap_ashare2,turn,roa_ttm,grossmargin,assetsturn,debttoassets"
    factors = "roe, pe, roa, pcf_ocf"
    for factor in factors.split(','):
        get_fundamental_market_data(factor)
        print(factor)

