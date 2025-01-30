import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from tkinter import messagebox
import os
import csv
from tkinter import filedialog
import numpy as np
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from photutils.aperture import aperture_photometry, CircularAperture, CircularAnnulus
from tabulate import tabulate
import pandas as pd
from astropy.visualization import ZScaleInterval
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import time
matplotlib.use("TkAgg")

class MyGui:

    def __init__(self, root):
        self.root = root
        self.root.geometry("850x600")
        self.root.title("Photometry App")

        # Create a notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create pages
        self.parameters_page = tk.Frame(self.notebook)
        self.plots_page = tk.Frame(self.notebook)
        self.table_page = tk.Frame(self.notebook)
        self.photometry_table_page = tk.Frame(self.notebook)

        # Add pages to the notebook
        self.notebook.add(self.parameters_page, text="Parameters")
        self.notebook.add(self.plots_page, text="Plots")
        self.notebook.add(self.table_page, text="Table")
        self.notebook.add(self.photometry_table_page, text='Photometry Output')

        # Variables for entries
        self.radius_var = tk.DoubleVar()
        self.position_var = tk.StringVar()
        self.inner_radius_var = tk.DoubleVar()
        self.outer_radius_var = tk.DoubleVar()
        self.filepath_var = tk.StringVar()
        self.filename_var = tk.StringVar()
        self.data_index = 0  # Index to keep track of current data entry

        # Initialize placeholders for plot and toolbar
        self.plt_canvas = None
        self.toolbar = None

        # Load input CSV file/textfile
        # Replace with the actual path to your CSV file/ make sure columns are formatted correctly
        self.csv_filename = ""  # Initialize with an empty string
        self.input_list = None  # Initialize with None

        # Labels and Entries on Parameters Page
        filename_label = tk.Label(self.parameters_page, text="Current Filename:")
        filename_label.grid(row=0, column=0, padx=10, pady=5)
        self.filename_entry = tk.Entry(self.parameters_page, textvariable=self.filename_var)
        self.filename_entry.grid(row=0, column=1, padx=10, pady=5)

        radius_label = tk.Label(self.parameters_page, text="Radius:")
        radius_label.grid(row=1, column=0, padx=10, pady=5)
        self.radius_entry = tk.Entry(self.parameters_page, textvariable=self.radius_var)
        self.radius_entry.grid(row=1, column=1, padx=10, pady=5)

        position_label = tk.Label(self.parameters_page, text="Position:")
        position_label.grid(row=2, column=0, padx=10, pady=5)
        self.position_entry = tk.Entry(self.parameters_page, textvariable=self.position_var)
        self.position_entry.grid(row=2, column=1, padx=10, pady=5)

        inner_radius_label = tk.Label(self.parameters_page, text="Inner Radius:")
        inner_radius_label.grid(row=3, column=0, padx=10, pady=5)
        self.inner_radius_entry = tk.Entry(self.parameters_page, textvariable=self.inner_radius_var)
        self.inner_radius_entry.grid(row=3, column=1, padx=10, pady=5)

        outer_radius_label = tk.Label(self.parameters_page, text="Outer Radius:")
        outer_radius_label.grid(row=4, column=0, padx=10, pady=5)
        self.outer_radius_entry = tk.Entry(self.parameters_page, textvariable=self.outer_radius_var)
        self.outer_radius_entry.grid(row=4, column=1, padx=10, pady=5)

        filepath_label = tk.Label(self.parameters_page, text="Filepath:")
        filepath_label.grid(row=5, column=0, padx=10, pady=5)
        self.filepath_entry = tk.Entry(self.parameters_page, textvariable=self.filepath_var)
        self.filepath_entry.grid(row=5, column=1, padx=10, pady=5)

        browse_button = tk.Button(self.parameters_page, text="Browse", command=self.browse_folder)
        browse_button.grid(row=5, column=2, padx=10, pady=5, sticky=tk.E)

        # Buttons on Parameters Page
        button_frame = tk.Frame(self.parameters_page)
        button_frame.grid(row=6, columnspan=3, pady=10)

        photometry_button = tk.Button(button_frame, text="Photometry", command=self.start_process)
        photometry_button.pack(side=tk.LEFT, padx=10)

        stop_button = tk.Button(button_frame, text="Quit", command=self.stop_process)
        stop_button.pack(side=tk.LEFT, padx=10)

        plot_button = tk.Button(button_frame, text="Plot", command=self.plot_data)
        plot_button.pack(side=tk.LEFT, padx=10)

        default_star_button = tk.Button(button_frame, text="Set For All Star Images", command=self.set_star)
        default_star_button.pack(side=tk.LEFT, padx=10)

        default_comet_button = tk.Button(button_frame, text="Set For All Comet Images", command=self.set_comet)
        default_comet_button.pack(side=tk.LEFT, padx=10)

        # Table on Table Page

        #Define the treeview widget
        self.table = tb.Treeview(self.table_page, show='headings', columns=('date', 'filenum', 'type', 'x', 'y','Aperture Radius','Inner Annulus Radius', 'Outer Annulus Radius'))
        # Set the headings and configure columns
        self.table.heading('date', text='Date')
        self.table.heading('filenum', text='File Number')
        self.table.heading('type', text='Type')
        self.table.heading('x', text='X')
        self.table.heading('y', text='Y')
        self.table.heading('Aperture Radius', text='Aperture Radius')
        self.table.heading('Inner Annulus Radius', text='Inner Annulus Radius')
        self.table.heading('Outer Annulus Radius', text='Outer Annulus Radius')

        # Set column widths and anchor
        self.table.column('date', anchor='w', width=100)
        self.table.column('filenum', anchor='center', width=100)
        self.table.column('type', anchor='center', width=100)
        self.table.column('x', anchor='center', width=50)
        self.table.column('y', anchor='center', width=50)
        self.table.column('Aperture Radius', anchor='center', width=100)
        self.table.column('Inner Annulus Radius', anchor='center', width=150)
        self.table.column('Outer Annulus Radius', anchor='e', width=150)

        # Add the table to the frame
        self.table.pack(fill='both', expand=True)

        # Bind the Treeview widget to the TreeviewSelect event
        self.table.bind('<<TreeviewSelect>>', self.item_selected)
        self.table.bind('<Button-3>', self.on_right_click)

        #Add buttons to photometry page

        #self.open_button = tb.Button(self.photometry_table_page, text="Open CSV", command=self.open_csv)
        #self.open_button.pack(side="top", pady=10)

        self.table_frame = tb.Frame(self.photometry_table_page)
        self.table_frame.pack(fill='both', expand=True)

        # Close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def open_csv(self, file_path):
       #Read in final table after photometry process
        df = pd.read_csv(file_path)
        self.show_table(df)

    def show_table(self, df):
        # Clear the previous table if exists
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        columns = df.columns.tolist()
        data = df.values.tolist()

        table = Tableview(
            self.table_frame,
            bootstyle='info',
            coldata=columns,
            rowdata=data,
            paginated=True,
            searchable=True
        )
        table.pack(fill='both', expand=True)

    def load_data(self, csv_filename):
        csv_filename = self.dir_path+'/list_photometry.csv'
        dir_path_final_files=self.dir_path+'/final_files'
        self.dir_path_final_files=dir_path_final_files
        # Load input CSV file/textfile
        self.csv_filename = csv_filename
        #self.input_list = np.loadtxt(self.csv_filename, dtype={'names':('date','filenum', 'type', 'x', 'y'), 'formats':('U6','U6','U6', 'U6', 'U6')}, delimiter=',')
        self.input_list_headerless = np.loadtxt(self.csv_filename, dtype={'names':('date','filenum', 'type', 'x', 'y'), 'formats':('U6','U6','U6', 'U6', 'U6')}, delimiter=',', skiprows=1)
        #print(self.input_list)

        # Create a Treeview widget
        for i in range (len(self.input_list_headerless)):
            self.table.insert('', 'end', values=(self.input_list_headerless['date'][i], self.input_list_headerless['filenum'][i], self.input_list_headerless['type'][i], self.input_list_headerless['x'][i],
                                                 self.input_list_headerless['y'][i], 20, 30, 40))

    def item_selected(self, event):
        self.selected_item = self.table.focus()
        if self.selected_item:
            # Get the values of the selected item
            values = self.table.item(self.selected_item, 'values')
            if values:
                self.filename_var.set(f'processed_{values[0]}_{values[1]}.fits')
                self.filename_entry.delete(0, 'end')
                self.filename_entry.insert(0, f'processed_{values[0]}_{values[1]}.fits')

                self.position_var.set(f'{values[3]}, {values[4]}')
                self.position_entry.delete(0, 'end')
                self.position_entry.insert(0, f'{values[3]}, {values[4]}')

                self.radius_var.set(values[5])
                self.radius_entry.delete(0, 'end')
                self.radius_entry.insert(0, values[5])

                self.inner_radius_var.set(values[6])
                self.inner_radius_entry.delete(0, 'end')
                self.inner_radius_entry.insert(0, values[6])

                self.outer_radius_var.set(values[7])
                self.outer_radius_entry.delete(0, 'end')
                self.outer_radius_entry.insert(0, values[7])

    def on_right_click(self, event):
        if self.selected_item:
            # Retrieve current values from entry boxes
            radius = self.radius_var.get()
            position = self.position_var.get()
            inner_radius = self.inner_radius_var.get()
            outer_radius = self.outer_radius_var.get()

            # Split position into x and y coordinates
            x_str, y_str = position.split(',')
            x_p = int(x_str.strip())
            y_p = int(y_str.strip())

            # Get current values of the selected row
            current_values = self.table.item(self.selected_item, 'values')
            #print(current_values)
            if current_values:
                # Update only specific values in the selected row
                updated_values = list(current_values)
                updated_values[5] = radius    # Update radius
                updated_values[3] = x_p  # Update position
                updated_values[4] = y_p  # Update position
                updated_values[6] = inner_radius  # Update inner radius
                updated_values[7] = outer_radius  # Update outer radius
                #print(updated_values)
                # Update the selected item in the table
                self.table.item(self.selected_item, values=updated_values)

    def browse_folder(self):
        dir_path = filedialog.askdirectory()
        self.dir_path = dir_path
        if dir_path:
            self.filepath_var.set(dir_path)
            self.filepath_entry.insert(0, dir_path)
            # Load data when filepath is selected
            self.load_data(f'{dir_path}/list_photometry.csv')

    def set_star(self):
        for row in self.table.get_children():
            values = self.table.item(row, 'values')
            if values[2] == 'star':
                # Retrieve current values from entry boxes
                radius = self.radius_var.get()
                inner_radius = self.inner_radius_var.get()
                outer_radius = self.outer_radius_var.get()

                # Update specific values in the row
                updated_values = list(values)
                updated_values[5] = radius    # Update radius
                updated_values[6] = inner_radius  # Update inner radius
                updated_values[7] = outer_radius  # Update outer radius

                # Update the row in the table
                self.table.item(row, values=updated_values)

    def set_comet(self):
        for row in self.table.get_children():
            values = self.table.item(row, 'values')
            if values[2] == 'comet':
                # Retrieve current values from entry boxes
                radius = self.radius_var.get()
                inner_radius = self.inner_radius_var.get()
                outer_radius = self.outer_radius_var.get()

                # Update specific values in the row
                updated_values = list(values)
                updated_values[5] = radius    # Update radius
                updated_values[6] = inner_radius  # Update inner radius
                updated_values[7] = outer_radius  # Update outer radius

                # Update the row in the table
                self.table.item(row, values=updated_values)

    def start_process(self):
        #Get the comet and star indices so we can iterate
        #print(f'Photometery is starting.....')
        comet_data = []
        star_data = []
        comet_photometry_data = []
        star_photometry_data = []
        filename_star=[]
        filename_comet=[]

        for row in self.table.get_children():
            values = self.table.item(row, 'values')
            if values[2] == 'comet':
                comet_data.append(values)
            elif values[2] == 'star':
                star_data.append(values)

        #print(comet_data)
        #Process star images
        for index, data in enumerate(star_data):
          #keep in mind that data is a tuple here and index is the element of that tuple
            date_table = data[0]
            filnum_table = data[1]
            type_table = data[2]
            position = [int(data[3]), int(data[4])]
            radii_table = [float(data[5])]
            inner_radii_table = float(data[6])
            outer_radii_table = float(data[7])

            # get current file path
            filename = f'{self.dir_path_final_files}/processed_{data[0]}_{data[1]}.fits'

            #Get the current file name and store it
            filename_star.append(f'processed_{data[0]}_{data[1]}.fits')
            
            data = fits.getdata(filename)
            aperture = [CircularAperture(position, r=r) for r in radii_table]

            annulus = CircularAnnulus(position, inner_radii_table , outer_radii_table)
            masks = annulus.to_mask(method='center')
            annulus_data = masks.multiply(data)

            mask = masks.data
            annulus_data_1d = annulus_data[mask > 0]
            _, median_sigclip, _ = sigma_clipped_stats(annulus_data_1d)

            background = [median_sigclip * a.area for a in aperture]

            img_error = np.sqrt(abs(data) + (5.87 ** 2.0))

            ptable = aperture_photometry(data, aperture[0], error=img_error)
            ptable['aper_bkg'] = median_sigclip * aperture[0].area
            ptable['aper_sum_bkgsub'] = ptable['aperture_sum'] - ptable['aper_bkg']  # bkg subtracted flux

            headers = ["ID", "X Center", "Y Center", "Aperture Sum Background", "Aperture Sum Err", "Aperture Background", "Background-Subtracted Flux"]
            rows = []
            for i, aper in enumerate(aperture):
                row = [
                    i + 1,
                    ptable['xcenter'][i],
                    ptable['ycenter'][i],
                    ptable['aperture_sum'][i],
                    ptable['aperture_sum_err'][i],
                    ptable['aper_bkg'][i],
                    ptable['aper_sum_bkgsub'][i]
                ]
                rows.append(row)
                star_photometry_data.append(row)

        # Convert star_photometry_data to a DataFrame
        fluxcal_df = pd.DataFrame(star_photometry_data, columns=headers)

        #Change ID to show filename
        fluxcal_df['ID'] = filename_star

        # Save fluxcal DataFrame as CSV file
        fluxcal_df.to_csv(self.dir_path+'/final_files/fluxcal_table.csv', index=False)

        #Now do the photometry for the comet images
        for index, data in enumerate(comet_data):
          #keep in mind that data is a tuple here and index is the element of that tuple
            date_table = data[0]
            filnum_table = data[1]
            type_table = data[2]
            position = [int(data[3]), int(data[4])]
            radii_table = [float(data[5])]
            inner_radii_table = float(data[6])
            outer_radii_table = float(data[7])

            # get current file path
            filename = f'{self.dir_path_final_files}/processed_{data[0]}_{data[1]}.fits'
            
            #Get the current file name and store it
            filename_comet.append(f'processed_{data[0]}_{data[1]}.fits')

            data = fits.getdata(filename)

            aperture = [CircularAperture(position, r=r) for r in radii_table]

            annulus = CircularAnnulus(position, inner_radii_table , outer_radii_table)
            masks = annulus.to_mask(method='center')
            annulus_data = masks.multiply(data)

            mask = masks.data
            annulus_data_1d = annulus_data[mask > 0]
            _, median_sigclip, _ = sigma_clipped_stats(annulus_data_1d)

            background = [median_sigclip * a.area for a in aperture]

            img_error = np.sqrt(abs(data) + (5.87 ** 2.0))

            ptable = aperture_photometry(data, aperture[0], error=img_error)
            ptable['aper_bkg'] = median_sigclip * aperture[0].area
            ptable['aper_sum_bkgsub'] = ptable['aperture_sum'] - ptable['aper_bkg']  # bkg subtracted flux

            # print(ptable['aperture_sum_err'])

            # Uncomment the following lines if needed for background annulus photometry
            # bkg_ap = CircularAperture(position, rad[1])
            # ptable2 = aperture_photometry(annulus_data, bkg_ap, error=bkg_error)
            # print(annulus_data.shape)

            # uncert = np.sqrt(ptable['aperture_sum_err'] ** 2 + ptable2['aperture_sum_err'] ** 2)
            # print(uncert)

            headers = ["ID", "X Center", "Y Center", "Aperture Sum Background", "Aperture Sum Err", "Aperture Background", "Background-Subtracted Flux"]
            rows = []
            for i, aper in enumerate(aperture):
                row = [
                    i + 1,
                    ptable['xcenter'][i],
                    ptable['ycenter'][i],
                    ptable['aperture_sum'][i],
                    ptable['aperture_sum_err'][i],
                    ptable['aper_bkg'][i],
                    ptable['aper_sum_bkgsub'][i]
                ]
                rows.append(row)
                comet_photometry_data.append(row)

        # Convert comet_data to a DataFrame
        comet_df = pd.DataFrame(comet_photometry_data, columns=headers)

        #Change ID to show filename
        comet_df['ID'] = filename_comet

        # Save comet DataFrame as CSV file
        comet_df.to_csv(self.dir_path+'/final_files/comet_table.csv', index=False)

        #Merge dataframes
        final_data = pd.concat([fluxcal_df, comet_df], ignore_index=True)

        # Save final DataFrame as CSV file
        final_data.to_csv(self.dir_path+'/final_files/final_table.csv', index=False)

        #Send table to photometry page
        self.open_csv(self.dir_path+'/final_files/final_table.csv')

        #Display a message to show that photometry is done
        Messagebox.ok('Photometry is complete check the folder final_files for csv files or go to photometry output to see the final data. Page 1 is for star data and Page 2 is for comet data.')

    def stop_process(self):
        # Close GUI
        self.root.quit()
        self.root.destroy()

    def plot_data(self):
        # Clear canvas for redraw
        if self.plt_canvas:
            self.plt_canvas.get_tk_widget().destroy()
        if self.toolbar:
            self.toolbar.destroy()

        # Get the current values from the entries
        radius = self.radius_var.get()
        position = self.position_var.get()
        #print(position)
        inner_radius = self.inner_radius_var.get()
        outer_radius = self.outer_radius_var.get()
        filename_current = self.filename_entry.get()
        filename = f'{self.dir_path_final_files}/{filename_current}'
        data = fits.getdata(filename)

        # Split the string by the comma and strip any extra spaces
        x_str, y_str = position.split(',')

        # Convert the string values to integers
        x_p = int(x_str.strip())
        y_p = int(y_str.strip())

        # Create a figure and axis object
        fig, ax = plt.subplots()

        # Create the object for ZScaleInterval
        z = ZScaleInterval()
        # Get min and max values of the data
        z1, z2 = z.get_limits(data)

        # Plot the image with the aperture
        ax.imshow(data, cmap='gray', origin='lower', vmin=z1, vmax=z2)
        aperture = CircularAperture([x_p, y_p], r=int(radius))
        aperture.plot(color='red', lw=0.75, ax=ax)
        aperture2 = CircularAperture([x_p, y_p], r=int(inner_radius))
        aperture2.plot(color='blue', lw=0.75, ax=ax)
        aperture3 = CircularAperture([x_p, y_p], r=int(outer_radius))
        aperture3.plot(color='blue', lw=0.75, ax=ax)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Aperture Size')
        plt.grid(True)
        plt.tight_layout()

        # Display plot in Plots tab
        self.plt_canvas = FigureCanvasTkAgg(plt.gcf(), self.plots_page)
        self.plt_canvas.draw()

        # Add toolbar for navigation
        self.toolbar = NavigationToolbar2Tk(self.plt_canvas, self.plots_page)
        self.toolbar.update()
        self.plt_canvas.get_tk_widget().pack(side=TOP, fill=tk.X, expand=False)

    def on_close(self):
        if Messagebox.yesno('Do you want to quit?')=='Yes':
            self.root.quit()
            self.root.destroy()

if __name__ == "__main__":
    root = tb.Window(themename="simplex")
    app = MyGui(root)
    root.mainloop()