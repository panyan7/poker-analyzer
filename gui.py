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

    def show_loc_summary(self):
        self.page.destroy()
        LocationSummaryPage(self.analyzer, self.root)

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


def gui_start():
    root = tk.Tk()
    root.title("Poker Analyzer")
    analyzer = PokerAnalyzer()
    main_page = MainPage(analyzer, master=root)
    root.mainloop()


if __name__ == "__main__":
    gui_start()
