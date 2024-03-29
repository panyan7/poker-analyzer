import tkinter
from tkinter import ttk
from analyzer import PokerAnalyzer


class Page:
    def __init__(self, analyzer, master=None):
        self.analyzer = analyzer
        self.root = master
        self.width = 800
        self.height = 400
        self.root.geometry(f"{self.width}x{self.height}")


class MainPage(Page):
    def __init__(self, analyzer, master=None):
        super().__init__(analyzer, master)
        self.create_page()

    def create_page(self):
        self.page = tkinter.Frame(self.root)
        self.page.pack()
        table_button = tkinter.Button(self.page,
                                      text='Summary by Location',
                                      command=self.show_loc_summary) \
                               .grid(row=1, column=1)

    def show_loc_summary(self):
        self.page.destroy()
        LocationSummaryPage(self.analyzer, self.root)


class LocationSummaryPage(Page):
    def __init__(self, analyzer, master=None):
        super().__init__(analyzer, master)
        self.create_page()

    def create_page(self):
        self.page = tkinter.Frame(self.root)
        self.page.pack()
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
            tree.column(col, anchor=tkinter.CENTER, width=100)
            tree.heading(col, text=col)
        for val in summary_list:
            tree.insert('', 'end', values=val)

        tree.pack()
        tree.grid(row=1, column=1)

        back_button = tkinter.Button(self.page,
                                     text='Exit',
                                     command=self.back_to_main) \
                             .grid(row=2, column=1)

    def back_to_main(self):
        self.page.destroy()
        MainPage(self.analyzer, self.root)


class SummaryPage(Page):
    def __init__(self, analyzer, master=None):
        super().__init__(analyzer, master)
        self.create_page()

    def create_page(self):
        pass



def gui_start():
    root = tkinter.Tk()
    analyzer = PokerAnalyzer()
    main_page = MainPage(analyzer, master=root)
    root.mainloop()


if __name__ == "__main__":
    gui_start()
