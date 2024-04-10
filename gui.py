import tkinter as tk
from tkinter import ttk
from analyzer import PokerAnalyzer
import pandas as pd


class Page:
    def __init__(self, analyzer, master=None):
        self.analyzer = analyzer
        self.root = master
        self.width = 1000
        self.height = 750
        self.root.geometry(f"{self.width}x{self.height}")

    def create_page(self):
        self.page = tk.Frame(self.root)
        self.page.pack()

    def back_to_main(self):
        self.page.destroy()
        MainPage(self.analyzer, self.root)


class MainPage(Page):
    def __init__(self, analyzer, master=None):
        super().__init__(analyzer, master)
        self.create_page()

    def create_page(self):
        super().create_page()
        loc_values = list(self.analyzer.data_df['location'].unique())
        loc_values = [""] + loc_values
        self.loc_box = ttk.Combobox(self.page,
                               values=loc_values)
        self.loc_box.grid(row=1, column=1)
        year_values = list(self.analyzer.data_df['date'].dt.year.unique())
        year_values = [""] + list(map(str, year_values))
        self.year_box = ttk.Combobox(self.page,
                                     values=year_values)
        self.year_box.grid(row=1, column=2)
        summary_button = tk.Button(self.page,
                                   text="Show Summary",
                                   command=self.show_summary)
        summary_button.grid(row=1, column=3)
        all_loc_button = tk.Button(self.page,
                                   text='Summary by All Location',
                                   command=self.show_loc_summary)
        all_loc_button.grid(row=2, column=1)
        all_year_button = tk.Button(self.page,
                                    text='Summary by All Year',
                                    command=self.show_loc_summary)
        all_year_button.grid(row=2, column=2)
        add_data_button = tk.Button(self.page,
                                    text="Add Data",
                                    command=self.add_data)
        add_data_button.grid(row=3, column=3)

    def show_loc_summary(self):
        self.page.destroy()
        LocationSummaryPage(self.analyzer, self.root)

    def add_data(self):
        self.page.destroy()
        DataInputPage(self.analyzer, self.root)

    def show_summary(self):
        location = self.loc_box.get()
        year = self.year_box.get()
        if location == "":
            location = None
        if year == "":
            year = None
        else:
            year = int(year)
        self.page.destroy()
        SummaryPage(self.analyzer, self.root, location=location, year=year)


class LocationSummaryPage(Page):
    def __init__(self, analyzer, master=None):
        super().__init__(analyzer, master)
        self.create_page()

    def create_page(self):
        super().create_page()
        summary_table = self.analyzer.summary_table()
        summary_list = list(summary_table.itertuples(index=True, name=None))
        round_numbers = lambda x: round(x, 2) if isinstance(x, float) else x
        round_tuple = lambda x: tuple(map(round_numbers, x))
        summary_list = list(map(round_tuple, summary_list))
        columns = ("location", *tuple(summary_table.columns))
        tree = ttk.Treeview(self.page,
                            columns=columns,
                            show='headings',
                            height=len(summary_list))
        for col in columns:
            tree.column(col, anchor=tk.CENTER, width=100)
            tree.heading(col, text=col)
        for val in summary_list:
            tree.insert('', 'end', values=val)
        tree.pack()
        tree.grid(row=1, column=1)

        back_button = tk.Button(self.page,
                                text='Exit',
                                command=self.back_to_main)
        back_button.grid(row=2, column=1)


class SummaryPage(Page):
    def __init__(self, analyzer, master=None, location=None, year=None):
        super().__init__(analyzer, master)
        self.location = location
        self.year = year
        self.create_page()

    def create_page(self):
        super().create_page()
        data_summary = self.analyzer.summary(location=self.location,
                                             year=self.year)
        columns = tuple(data_summary.columns)
        tree = ttk.Treeview(self.page,
                            columns=columns,
                            show='headings',
                            height=1)
        for col in columns:
            tree.column(col, anchor=tk.CENTER, width=100)
            tree.heading(col, text=col)
        round_numbers = lambda x: round(x, 2) if isinstance(x, float) else x
        round_tuple = lambda x: tuple(map(round_numbers, x))
        tree.insert('', 'end', values=round_tuple(tuple(data_summary.iloc[0])))
        tree.pack()
        tree.grid(row=1, column=1)

        year = self.year
        location = self.location
        title = 'summary.png'
        if year is not None:
            title = str(year) + '_' + title
        if location is not None:
            title = location + '_' + title

        image = tk.PhotoImage(file=('summary/'+title))
        label = ttk.Label(self.page, image=image)
        label.image = image
        label.grid(row=2, column=1)

        back_button = tk.Button(self.page,
                                text='Exit',
                                command=self.back_to_main)
        back_button.grid(row=3, column=1)


class DataInputPage(Page):
    def __init__(self, analyzer, master=None):
        super().__init__(analyzer, master)
        self.create_page()

    def create_page(self):
        super().create_page()
        self.win_bb = tk.StringVar()
        win_bb_label = tk.Label(self.page, text='Win/BB')
        win_bb_label.grid(row=1, column=1)
        self.win_bb_box = tk.Entry(self.page, textvariable=self.win_bb)
        self.win_bb_box.grid(row=1, column=2)

        self.sb_val = tk.StringVar()
        sb_label = tk.Label(self.page, text='SB')
        sb_label.grid(row=2, column=1)
        self.sb_box = tk.Entry(self.page, textvariable=self.sb_val)
        self.sb_box.grid(row=2, column=2)

        self.bb_val = tk.StringVar()
        bb_label = tk.Label(self.page, text='BB')
        bb_label.grid(row=3, column=1)
        self.bb_box = tk.Entry(self.page, textvariable=self.bb_val)
        self.bb_box.grid(row=3, column=2)

        currency_label = tk.Label(self.page, text='Currency')
        currency_label.grid(row=4, column=1)
        self.currency_box = ttk.Combobox(self.page,
                                         values=['USD', 'CNY'])
        self.currency_box.grid(row=4, column=2)

        self.location = tk.StringVar()
        loc_label = tk.Label(self.page, text='Location')
        loc_label.grid(row=5, column=1)
        self.loc_box = tk.Entry(self.page, textvariable=self.location)
        self.loc_box.grid(row=5, column=2)

        self.num_hands = tk.StringVar()
        hand_label = tk.Label(self.page, text='# Hands')
        hand_label.grid(row=6, column=1)
        self.hand_box = tk.Entry(self.page, textvariable=self.num_hands)
        self.hand_box.grid(row=6, column=2)

        self.date = tk.StringVar()
        date_label = tk.Label(self.page, text='Date')
        date_label.grid(row=7, column=1)
        self.date_box = tk.Entry(self.page, textvariable=self.date)
        self.date_box.grid(row=7, column=2)

        back_button = tk.Button(self.page,
                                text='Exit',
                                command=self.back_to_main)
        back_button.grid(row=8, column=1)
        submit_button = tk.Button(self.page,
                                  text='Submit',
                                  command=self.submit)
        submit_button.grid(row=8, column=2)


    def submit(self):
        win_bb = float(self.win_bb.get())
        sb_val = float(self.sb_val.get())
        bb_val = float(self.bb_val.get())
        currency = self.currency_box.get()
        location = self.location.get()
        num_hands = self.num_hands.get()
        date = pd.Timestamp(self.date.get())
        self.analyzer.add_data(win_bb=win_bb,
                               sb_val=sb_val,
                               bb_val=bb_val,
                               currency=currency,
                               location=location,
                               num_hands=num_hands,
                               date=date)
        self.back_to_main()


def gui_start():
    root = tk.Tk()
    root.title("Poker Analyzer")
    analyzer = PokerAnalyzer()
    main_page = MainPage(analyzer, master=root)
    root.mainloop()


if __name__ == "__main__":
    gui_start()
