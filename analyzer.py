import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None
CNY_TO_USD = 0.13837


class PokerAnalyzer:
    def __init__(self, data_path="data.csv"):
        self.columns = ['win_bb','sb_val','bb_val','currency',
                        'location','pnl','date','num_hands']
        self.data_path = data_path
        self.data_df = self.read_data()

    def read_data(self) -> pd.DataFrame:
        try:
            self.data_df = pd.read_csv(self.data_path, parse_dates=['date'],
                                       date_parser=pd.Timestamp)
        except FileNotFoundError:
            self.data_df = pd.DataFrame(columns=self.columns)
        return self.data_df

    def print_data(self):
        self.drop_unnamed_cols()
        print(self.data_df)

    def save_data(self):
        self.drop_unnamed_cols()
        self.data_df = self.data_df[self.columns]
        self.data_df.to_csv(self.data_path)

    def get_pnl(self):
        self.data_df['pnl'] = self.data_df['win_bb'] * self.data_df['bb_val']
        self.data_df.loc[self.data_df['currency'] == 'CNY','pnl'] *= CNY_TO_USD
        self.data_df['cum_pnl'] = self.data_df['pnl'].cumsum()
        self.data_df = self.data_df.round({'pnl': 2, 'cum_pnl': 2})

    def get_summary(self, data_df: pd.DataFrame):
        data_summary = {}
        data_summary['sessions'] = data_df['pnl'].count()
        data_summary['win_rate'] = (data_df['pnl'] > 0).mean()
        data_summary['total_pnl'] = data_df['pnl'].sum()
        data_summary['average_pnl'] = data_df['pnl'].mean()
        data_summary['total_win_bb'] = data_df['win_bb'].sum()
        data_summary['average_win_bb'] = data_df['win_bb'].mean()
        if data_df['num_hands'].count() > 0:
            mean_hands = data_df['num_hands'].mean()
            num_hands = data_df['num_hands'].fillna(mean_hands).sum()
            data_summary['win_bb_per_hand'] = data_df['win_bb'].sum() / num_hands
            data_summary['pnl_per_hand'] = data_df['pnl'].sum() / num_hands

        data_df['streak_id'] = data_df['pnl'].lt(0).cumsum()
        streak_sizes = data_df.groupby('streak_id')['pnl'].transform('size')
        streak_df = data_df[streak_sizes == streak_sizes.max()]
        if streak_df['pnl'].iloc[0] <= 0:
            streak_df = streak_df.iloc[1:]
        data_summary['longest_streak'] = int(streak_df['pnl'].count())
        return data_summary

    def summary(self, location=None, year=None):
        data_df = self.data_df
        if location is not None:
            data_df = data_df[data_df['location'] == location]
        if year is not None:
            data_df = data_df[data_df['date'].dt.year == year]
        data_summary = pd.Series(self.get_summary(data_df))
        data_summary_df = pd.DataFrame(columns=data_summary.index)
        data_summary_df = data_summary_df.append(data_summary, ignore_index=True)
        data_summary = data_summary_df

        nan_row = pd.DataFrame([[np.nan] * len(data_df.columns)],
                               columns=data_df.columns)
        nan_row['pnl'] = 0.0
        nan_row['win_bb'] = 0.0
        data_df = nan_row.append(data_df, ignore_index=True)
        data_df = data_df.reset_index()

        cum_pnl = data_df['pnl'].cumsum()
        fig = plt.figure(figsize=[8,6])
        fig.add_subplot(2,1,1)
        plt.plot(cum_pnl, '--*', c='C0')
        plt.grid()
        plt.xlabel('Session')
        plt.ylabel('PnL/USD')
        fig.add_subplot(2,1,2)
        plt.plot(data_df['win_bb'].cumsum(), '--*', c='C1')
        plt.grid()
        plt.xlabel('Session')
        plt.ylabel('Win/bb')
        title = 'summary.png'
        if year is not None:
            title = str(year) + '_' + title
        if location is not None:
            title = location + '_' + title
        plt.savefig('summary/' + title)
        self.drop_unnamed_cols()
        return data_summary

    def summary_table(self):
        summary_table = self.data_df.groupby('location') \
                                    .apply(self.get_summary) \
                                    .apply(pd.Series)
        return summary_table

    def add_data(self, new_data=None, **kwargs):
        if new_data is None:
            new_data = kwargs
        if isinstance(new_data, dict):
            new_data = pd.Series(new_data)
        self.data_df = self.data_df.append(new_data, ignore_index=True)
        self.get_pnl()
        self.save_data()

    def drop_unnamed_cols(self):
        unnamed_cols = [c for c in self.data_df.columns if c.startswith("Unnamed")]
        self.data_df = self.data_df.drop(columns=unnamed_cols)

