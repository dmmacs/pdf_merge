from pathlib import Path
from datetime import timedelta,datetime
import time
import logging

from pypdf import PdfMerger

import tkinter as tk
from tkinter import Frame
from tkinter import END
from tkinter.messagebox import showinfo
from tkinter import Image
from tkinter import filedialog as fd

from  tkinterdnd2 import *
import json

from PIL import ImageTk,Image


pdfs = ["pdf-statement-details.pdf", "Receipt_2023-09-02_154743.pdf"]

win_width = 770
win_height = 725

win_pad = 50
column_pad = 4
row_pad = 4 
cfg_geo_str = "geometry"
cfg_result_path_str = "ResultPath"
cfg_confirm_overwrite_str = "CofirmOverwrite"
cfg = {}

cfg_Path = (Path(__file__)).parent / "pdf_merge.ini"


class MergePdf(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=0)
        self.bind('x', self.exitkey)
        self.bind('m', self.mergekey)
        self.bind('c', self.clearkey)
        self.protocol("WM_DELETE_WINDOW", self.exitkey)
        self.dest_path = ""
        self.merge_path = ""
        self.merge_folder = Path(cfg.get(cfg_result_path_str))
        self.dest_folder = Path(cfg.get(cfg_result_path_str))


        self.minsize(height=250, width=win_width)
        if cfg.get(cfg_geo_str) is not None and cfg.get(cfg_geo_str) != "":
            self.geometry(cfg.get('geometry'))
        # self.geometry(f"{win_width}x{win_height}")
        # self.geometry()
        self.title("Merge PDF")

        row = 0
        self.label = tk.Label(self, text="Destination PDF")
        self.label.grid(row=row, column=0, sticky=tk.W+tk.E,padx=column_pad, pady=row_pad)

        row += 1
        self.dest_pdf = tk.Entry(self)#, width=180)
        self.dest_pdf.grid(row=row, column=0, sticky=tk.W+tk.E, padx=column_pad, pady=row_pad,columnspan=2)
        self.dest_pdf.drop_target_register(DND_ALL)
        self.dest_pdf.dnd_bind("<<Drop>>", self.get_dest_path)

        # self.dest_pdf.delete(0,tk.END)
        self.dest_browse = tk.Button(self, text="...", command=self.dest_browse_cmd)
        self.dest_browse.grid(row=row,column=2, padx=column_pad, pady=column_pad)

        row += 1
        self.label = tk.Label(self, text="PDF to merge into destination")
        self.label.grid(row=row, column=0, sticky=tk.W+tk.E,padx=column_pad, pady=row_pad)

        row += 1
        self.merge_pdf = tk.Entry(self)#, width=180)
        self.merge_pdf.grid(row=row, column=0, sticky=tk.W+tk.E, padx=column_pad, pady=row_pad,columnspan=2)
        # self.dest_pdf.delete(0,tk.END)
        self.merge_pdf.drop_target_register(DND_ALL)
        self.merge_pdf.dnd_bind("<<Drop>>", self.get_merge_path)

        self.merge_browse = tk.Button(self, text="...",command=self.merge_browse_cmd)
        self.merge_browse.grid(row=row,column=2, padx=column_pad, pady=column_pad)

        # Add merge button
        row +=1 
        self.merge_button = tk.Button(self, text="Merge", command=self.Merge, underline=0)
        self.merge_button.grid(row=row, column=0, sticky=tk.W)

        # Add Clear button
        self.clear_button = tk.Button(self, text="Clear", command=self.Clear, underline=0)
        self.clear_button.grid(row=row, column=0, sticky=tk.E)

        # Add Log Box
        row += 1
        self.log = tk.Text(self)
        self.log.grid(row=row, column=0, columnspan=5, padx=column_pad, pady=row_pad, sticky=tk.W+tk.E+tk.S)

    def get_dest_path(self,event):
        self.dest_pdf.delete(0, tk.END)
        self.dest_pdf.insert(0,event.data)
    
    def get_merge_path(self, event):
        self.merge_pdf.delete(0, tk.END)
        self.merge_pdf.insert(0,event.data)

    def Clear(self):
        self.merge_pdf.delete(0, tk.END)
        self.dest_pdf.delete(0, tk.END)

        self.merge_path = ""
        self.dest_path = ""
        self.log.delete("0.0", tk.END)

    def exitkey(self, event=None):
        self.Quit()
    
    def mergekey(self, event=None):
        self.Merge()
    
    def clearkey(self, event=None):
        self.Clear()

    def Quit(self):
        print("exitkey")
        
        cfg[cfg_geo_str] = f"{self.winfo_width()}x{self.winfo_height()}+{self.winfo_x()}+{self.winfo_y()}"
        print(cfg[cfg_geo_str])
        with open(cfg_Path, "w") as fout:
            json.dump(cfg, fout, indent=4)

        self.quit()
    
    def merge_browse_cmd(self):
        print("merge_browse_cmd")
        filetype = (('Pdf files', "*.pdf"),('All Files', '*.*'))
        initialdir = self.merge_folder
                
        filename = fd.askopenfilename(title="Select a Pdf File", initialdir=initialdir, filetypes=filetype)
        if filename != "":
            print(filename)
            self.merge_pdf.delete(0, tk.END)
            self.merge_pdf.insert(0, filename)
            self.merge_path = Path(filename)
            self.merge_folder = (Path(filename)).parent

    def dest_browse_cmd(self):
        print("dest_browse_cmd")
        filetype = (('Pdf files', "*.pdf"),('All Files', '*.*'))
        initialdir = self.dest_folder
        filename = fd.asksaveasfilename(title="Select a Pdf File", initialdir=initialdir, filetypes=filetype, confirmoverwrite=cfg.get(cfg_confirm_overwrite_str))
        
        if filename != "":
            print(filename)
            self.dest_pdf.delete(0, tk.END)
            self.dest_pdf.insert(0, filename)
            self.dest_folder = (Path(filename)).parent



    
    def add_log_entry(self,tmp):
        self.log.insert(tk.END, tmp)

    def Merge(self):
        self.add_log_entry("Merging Files\n")
        tmp = self.dest_pdf.get()
        self.add_log_entry(f"    Dest File = {tmp}\n")
        if len(tmp) == 0:
            self.add_log_entry(f"        Dest File empty\n")
            # return

        self.dest_path = Path(tmp)
        if self.dest_path.exists() == False:
            self.add_log_entry(f"        Dest File does not exist\n")
            # return

        tmp = self.merge_pdf.get()
        self.add_log_entry(f"    File to Merge in = {tmp}\n")
        if len(tmp) == 0:
            self.add_log_entry(f"        File to Merge empty\n")
            # return

        self.merge_path = Path(tmp)
        if self.merge_path.exists() == False:
            self.add_log_entry(f"        File to Merge does not exist\n")
            # return

        merger = PdfMerger()
        if self.dest_path.exists() == True:
            try:
                merger.append(self.dest_path)
            except PermissionError as e:
                print(e)
                self.add_log_entry(f"    {e}\n")
                merger.close()
            

        try:
            merger.append(self.merge_path)
        except PermissionError as e:
            print(e)
            self.add_log_entry(f"    {e}\n")
            merger.close()
        try:
            merger.write(self.dest_path)
        except PermissionError as e:
            print(e)
            self.add_log_entry(f"    {e}\n")
        finally:
            self.add_log_entry("    Files Merged\n")
            merger.close()

        

if __name__ == "__main__":
    start = time.perf_counter()

    # Load Config File
    with open(cfg_Path, "r") as fin:
        cfg = json.load(fin)

    if cfg.get(cfg_result_path_str) is None or cfg.get(cfg_result_path_str) == "":
        cfg[cfg_result_path_str] = '.'
    
    if cfg.get(cfg_confirm_overwrite_str) is None or cfg.get(cfg_confirm_overwrite_str) == "":
        cfg[cfg_confirm_overwrite_str] = False

    app = MergePdf()

    app.mainloop()
    


    end = time.perf_counter()
    print()
    msg = f'{Path(__file__).stem} completed in {timedelta(seconds=end-start)} ({end-start:02.3F} seconds)'
    print(msg)
    logging.info(msg)
