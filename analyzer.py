import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter

CNY_TO_USD = 0.13837

class PokerAnalyzer:
    def __init__(self, data_path="data.csv"):
        self.data_path = data_path
        self.data = self.read_data()

    def read_data(self) -> pd.DataFrame:
        self.data = pd.read_csv(self.data_path, parse_dates=['date'],
                                date_parser=pd.Timestamp)
        return self.data

    def print_data(self):
        self.drop_unnamed_cols()
        print(self.data)

    def save_data(self):
        self.drop_unnamed_cols()
        self.data.to_csv(self.data_path)

    def get_pnl(self):
        self.data['pnl'] = self.data['win_bb'] * self.data['bb_val']
        self.data.loc[self.data['currency'] == 'CNY','pnl'] *= CNY_TO_USD
        self.data['cum_pnl'] = self.data['pnl'].cumsum()
        self.data = self.data.round({'pnl': 2, 'cum_pnl': 2})

    def get_summary(self, data: pd.DataFrame):
        data_summary = {}
        data_summary['sessions'] = data['pnl'].count()
        data_summary['win_rate'] = (data['pnl'] > 0).mean()
        data_summary['total_pnl'] = data['pnl'].sum()
        data_summary['average_pnl'] = data['pnl'].mean()
        data_summary['total_win_bb'] = data['win_bb'].sum()
        data_summary['average_win_bb'] = data['win_bb'].mean()
        return data_summary

    def summary(self, location=None):
        data = self.data
        if location is not None:
            data = data[data['location'] == location]
        data_summary = pd.Series(self.get_summary(data))
        print(data_summary)

        nan_row = pd.DataFrame([[np.nan] * len(data.columns)], columns=data.columns)
        nan_row['pnl'] = 0.0
        nan_row['win_bb'] = 0.0
        data = nan_row.append(data, ignore_index=True)
        data = data.reset_index()

        cum_pnl = data['pnl'].cumsum()
        fig = plt.figure(figsize=[10,10])
        fig.add_subplot(2,1,1)
        plt.plot(cum_pnl, '--*', c='C0')
        plt.grid()
        plt.xlabel('Session')
        plt.ylabel('PnL/USD')
        fig.add_subplot(2,1,2)
        plt.plot(data['win_bb'].cumsum(), '--*', c='C1')
        plt.grid()
        plt.xlabel('Session')
        plt.ylabel('Win/bb')
        title = 'summary.png'
        if location is not None:
            title = location + '_' + title
        plt.savefig(title)
        self.drop_unnamed_cols()

    def summary_table_by_loc(self):
        summary_table = self.data.groupby('location').apply(self.get_summary).apply(pd.Series)
        print(summary_table)
        return summary_table

    def add_data(self, new_data):
        self.data = self.data.append(new_data)

    def drop_unnamed_cols(self):
        unnamed_cols = [c for c in self.data.columns if c.startswith("Unnamed")]
        self.data = self.data.drop(columns=unnamed_cols)


if __name__ == "__main__":
    analyzer = PokerAnalyzer()
    analyzer.get_pnl()
    analyzer.summary_table_by_loc()
    analyzer.summary(location="Mashu")
    analyzer.save_data()

