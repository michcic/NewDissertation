import tkinter as tk
from tkinter import ttk, StringVar
from tkinter import messagebox
from DataAccess import DataAccess
import ObjectPreparation as prep
import ActiveRegion as ar
import Sunspot as sp


# Class represents the interface of the software
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
        fil_combo['values'] = ('MEUDON/SPECTTROHELIOGRAPH')

        # Function is called after clicking 'Create Map' button
        # It gathers inputs from fields and create map
        # If some of the values are empty it throws error
        def create():
            # get start and end date of observation
            start = self.start_val.get()
            end = self.end_val.get()
            # get name of observatory and type of instrument
            ar = self.ar_instruments.get().split('/')
            sp = self.sp_instruments.get().split('/')
            fil = self.fil_instruments.get().split('/')

            empty_input_instr = len(ar) < 2 or len(sp) < 2 or len(fil) < 2

            if empty_input_instr:
                messagebox.showerror("Error", "Some of the values are empty!")
            else:
                ar_obs = ar[0]
                ar_instr = ar[1]
                sp_obs = sp[0]
                sp_instr = sp[1]
                fil_obs = fil[0]  # For filaments (work in progress)
                fil_instr = fil[1]

                empty_input_obs = len(start) == 0 or len(end) == 0

                if empty_input_obs:
                    messagebox.showerror("Error", "Some of the values are empty!")
                else:
                    try:
                        create_map(start, end, ar_obs, ar_instr, sp_obs, sp_instr)
                    except Exception as error:
                        print(error)
                        if str(error) == "File not found or invalid input" or str(error) == "list index out of range":
                            messagebox.showinfo("Sorry!", "The software works only with SOHO/MDI and MEUDON/SPECTTROHELIOGRAPH "
                                                 "instruments. Sorry for inconvenience!")

        create_button = ttk.Button(container, text="Create Map", command=create)
        create_button.grid(row=5, column=0)




def create_map(start, end, ar_obs, ar_instr, sp_obs, sp_instr):
    # setting active regions
    data = DataAccess(start, end, 'AR', ar_obs, ar_instr)
    chain_encoded = prep.decode_and_split(data.get_chain_code())
    ar_carr_synthesis, ar_pix_synthesis = ar.get_shapes(chain_encoded, data.get_pixel_start_x(),
                                                        data.get_pixel_start_y(), data.get_filename(),
                                               data.get_noaa_number(), data.get_ar_id(), data.get_date())

    # setting sunspots
    sp_data = DataAccess(start, end, 'SP', sp_obs, sp_instr)

    sp_chain_encoded = prep.decode_and_split(sp_data.get_chain_code())

    sp_carr, sp_pix = sp.get_shapes(sp_chain_encoded, sp_data.get_pixel_start_x(), sp_data.get_pixel_start_y(),
                                sp_data.get_filename(), sp_data.get_sp_id(), sp_data.get_date())

    sp_synthesis = sp.make_sp_synthesis(ar_contour=ar_carr_synthesis, sp_carr=sp_carr)

    prep.display_object(ar_carr_synthesis, sp_synthesis)


if __name__ == '__main__':
    root = tk.Tk()
    MainFrame(root)
    root.mainloop()
