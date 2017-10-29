from Strategy import *
import pandas as pd


class AprQuant1(Strategy):
    def calc_position(self, scores):
        # After we built our model,
        # This is where we realize our strategy
        # For example, prediction gave scores over the whole market
        # Then we buy the top quantile 10 %, that is most likely to outperform

        # scores is actually a dataframe
        scores = scores.sort_values('scores')
        cond = scores['scores'] > scores['scores'].quantile(0.1)
        to_buy = scores['tickers'][cond].tolist()
        # Once we have that to_buy information
        # we can formulate a equal weighted portfolio
        new_position = {ticker: 1/len(to_buy) for ticker in to_buy}
        return new_position

    def run(self):
        import datetime
        while self.active:
            if datetime.datetime.today().day == 1:
                feed = pd.read_csv()
            else:
                feed = None
            for event in self.generate_events(feed):
                self.trading_engine.put(event)





