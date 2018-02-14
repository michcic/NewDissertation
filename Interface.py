import tkinter as tk
from tkinter import ttk, StringVar
from tkinter.messagebox import showinfo
from DataAccess import DataAccess
import ObjectPreparation as prep
import ActiveRegion as ar



'''Login window from where user can login or go
to register window'''


class MainFrame(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        container = ttk.Frame(self).grid(row=0, column=0)

        ttk.Label(container, text="Start date:").grid(row=0, column=0, sticky='W', padx=10)
        ttk.Label(container, text="End date:").grid(row=0, column=1, sticky='W', padx=10)
        ttk.Label(container, text="Active regions:").grid(row=2, column=1, sticky='W', padx=10)
        ttk.Label(container, text="Sunspots:").grid(row=2, column=0, sticky='W', padx=10)
        ttk.Label(container, text="Filaments:").grid(row=4, column=1, sticky='W', padx=10)

        self.start_val = StringVar(value="2003-09-26T00:00:00")
        self.end_val = StringVar(value="2003-10-24T00:00:00")

        ttk.Entry(container, textvariable=self.start_val).grid(row=1, column=0, padx=10)
        ttk.Entry(container, textvariable=self.end_val).grid(row=1, column=1, padx=10)

        self.ar_instruments = StringVar()
        ar_combo = ttk.Combobox(parent, textvariable=self.ar_instruments)
        ar_combo.grid(row=3, column=1, sticky='W', padx=10)
        ar_combo['values'] = ('SOHO/MDI', 'SOHO/EIT', 'SDO/AIA')

        self.sp_instruments = StringVar()
        sp_combo = ttk.Combobox(parent, textvariable=self.sp_instruments)
        sp_combo.grid(row=3, column=0, sticky='W', padx=10)
        sp_combo['values'] = ('SOHO/MDI', 'SDO/HMI')

        self.fil_instruments = StringVar()
        fil_combo = ttk.Combobox(parent, textvariable=self.fil_instruments)
        fil_combo.grid(row=5, column=1, sticky='W', padx=10)
        fil_combo['values'] = ('Meudon_H_Alpha_Spectroheliograph')

        def create():
            start = self.start_val.get()
            end = self.end_val.get()
            instrument = self.ar_instruments.get()
            create_map(start=start, end=end,instrument=instrument)


        createButton = ttk.Button(container, text="Create Map", command=create)
        createButton.grid(row=5, column=0)


def create_map(start, end, instrument):
    data = DataAccess(start, end, 'AR')
    chain_encoded = prep.encode_and_split(data.get_chain_code())
    carr_synthesis, pix_synthesis = ar.get_shapes(chain_encoded, data.get_pixel_start_x(), data.get_pixel_start_y(),
                                               data.get_filename(),
                                               data.get_noaa_number(), data.get_ar_id(), data.get_date())
    prep.display_object(carr_synthesis)



if __name__ == '__main__':
    root = tk.Tk()
    MainFrame(root)
    root.mainloop()
