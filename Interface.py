import tkinter as tk
from tkinter import ttk, StringVar
from tkinter.messagebox import showinfo



'''Login window from where user can login or go
to register window'''


class MainFrame(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        container = ttk.Frame(self).grid(row=0, column=0)

        ttk.Label(container, text="Start date:").grid(row=0, column=0, sticky='W', padx=10)
        ttk.Label(container, text="End date:").grid(row=0, column=1, sticky='W', padx=10)

        self.start_val = StringVar(value="2003-09-25T00:00:00")
        self.end_val = StringVar(value="2003-09-25T00:00:00")

        start_entry = ttk.Entry(container, textvariable=self.start_val)
        start_entry.grid(row=1, column=0, padx=10)
        end_entry = ttk.Entry(container, textvariable=self.end_val).grid(row=1, column=1, padx=10)

        def clickMe():
            print(self.start_val.get())

        regButton = ttk.Button(container, text="Register", command=clickMe)
        regButton.grid(row=2, column=0)


if __name__ == '__main__':
    root = tk.Tk()
    MainFrame(root)
    root.mainloop()
