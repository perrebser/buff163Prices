import tkinter as tk
from tkinter import ttk


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Buff Price Checker")

        self.geometry('600x400+200+200')
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        entry = ttk.Entry()
        btn = ttk.Button(text="Search item")
        btn.place(x=60, y=80)
        entry.place(x=50, y=50)

        ttk.Label(self, text='Insert skin name').pack()
