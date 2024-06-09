import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None
RMB_TO_USD = 0.13837


class PokerAnalyzer:
    def __init__(self, data_path="data.csv"):
        self.columns = ['win_val','sb_val','bb_val','win_bb','currency',
                        'location','pnl','date','num_hands',]
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
        self.data_df['win_bb'] = self.data_df['win_val'] / self.data_df['bb_val']
        self.data_df = self.data_df.round(2)
        self.data_df['pnl'] = self.data_df['win_val']
        self.data_df.loc[self.data_df['currency'] == 'RMB','pnl'] *= RMB_TO_USD
        self.data_df['cum_pnl'] = self.data_df['pnl'].cumsum()
        self.data_df = self.data_df.round(2)
        return self.data_df

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
        win_df = data_df[data_df['pnl'].gt(0)]
        streak_sizes = win_df.groupby('streak_id')['pnl'].transform('size')
        if streak_sizes.count() == 0:
            data_summary['longest_streak'] = 0
        else:
            data_summary['longest_streak'] = int(streak_sizes.max())
        return data_summary

    def summary(self, location=None, year=None):
        data_df = self.data_df
        if location is not None:
            data_df = data_df[data_df['location'] == location]
        if year is not None:
            data_df = data_df[data_df['date'].dt.year == year]
        data_summary = self.get_summary(data_df)
        data_summary = {k: [v] for k, v in data_summary.items()}
        data_summary = pd.DataFrame(data_summary)
        data_summary_df = pd.DataFrame(columns=data_summary.columns)
        data_summary_df = pd.concat([data_summary_df, data_summary], ignore_index=True)

        nan_row = pd.DataFrame([[np.nan] * len(data_df.columns)],
                               columns=data_df.columns)
        nan_row['pnl'] = 0.0
        nan_row['win_bb'] = 0.0
        data_df = pd.concat([nan_row, data_df], ignore_index=True)
        data_df = data_df.reset_index()

        pnl = data_df['pnl']
        cum_pnl = data_df['pnl'].cumsum()
        fig = plt.figure(figsize=[8,8])
        plt.subplots_adjust(hspace=0.5)
        fig.add_subplot(3,1,1)
        plt.plot(cum_pnl, '--*', c='C0')
        plt.grid()
        plt.xlabel('Session')
        plt.ylabel('PnL/USD')
        fig.add_subplot(3,1,2)
        plt.plot(data_df['win_bb'].cumsum(), '--*', c='C1')
        plt.grid()
        plt.xlabel('Session')
        plt.ylabel('Win/BB')
        fig.add_subplot(3,2,5)
        plt.hist(pnl, color='C0')
        plt.grid()
        plt.xlabel('PnL')
        fig.add_subplot(3,2,6)
        plt.hist(data_df['win_bb'], color='C1')
        plt.grid()
        plt.xlabel('Win/BB')
        title = 'summary.png'
        if year is not None:
            title = str(year) + '_' + title
        if location is not None:
            title = location + '_' + title
        plt.savefig('summary/' + title, bbox_inches='tight')
        self.drop_unnamed_cols()
        return data_summary_df

    def summary_table(self, index=None):
        assert index is not None
        if index == 'year':
            self.data_df['year'] = self.data_df['date'].dt.year
        if index == 'stake':
            self.data_df['stake'] = self.data_df['sb_val'].astype(str) + '/' \
                                    + self.data_df['bb_val'].astype(str) + \
                                    + self.data_df['currency'].astype(str)
        summary_table = self.data_df.groupby(index) \
                                    .apply(self.get_summary) \
                                    .apply(pd.Series)
        return summary_table

    def add_data(self, new_data=None, **kwargs):
        if new_data is None:
            new_data = kwargs
        if isinstance(new_data, dict):
            new_data = {k: [v] for k, v in new_data.items()}
            new_data = pd.DataFrame(new_data)
        self.data_df = pd.concat([self.data_df, new_data], ignore_index=True)
        self.get_pnl()
        self.save_data()

    def drop_unnamed_cols(self):
        unnamed_cols = [c for c in self.data_df.columns if c.startswith("Unnamed")]
        self.data_df = self.data_df.drop(columns=unnamed_cols)

