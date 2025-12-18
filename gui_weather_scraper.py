
import os
import datetime

import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from weather_scraper import scrape

class WeatherScraperGUI(ttkb.Window):
    def __init__(self):
        super().__init__(title="Weather Scraper", themename="flatly")  # try: "darkly", "cyborg", "cosmo", etc.
        self.geometry("800x600")
        self.resizable(True, True)

        # ---------- State ----------
        self.url_list = []
        self.download_folder = tk.StringVar(value="")
        self.from_date_var = tk.StringVar()
        self.to_date_var = tk.StringVar()

        # ---------- Layout ----------
        self._build_header()
        self._build_url_section()
        self._build_date_section()
        self._build_folder_section()
        self._build_footer()

    # ----- Header -----
    def _build_header(self):
        header = ttkb.Frame(self, padding=(10, 10))
        header.pack(fill=X)
        title_lbl = ttkb.Label(header, text="Weather Scraper", font=("Segoe UI", 16, "bold"))
        title_lbl.pack(side=LEFT)
        subtitle_lbl = ttkb.Label(header, text="Configure sources, date range, and download location", bootstyle=SECONDARY)
        subtitle_lbl.pack(side=LEFT, padx=10)

    # ----- URL Section -----
    def _build_url_section(self):
        section = ttkb.Labelframe(self, text="Station URLs", padding=10)
        section.pack(fill=X, padx=10, pady=(0, 10))

        row = ttkb.Frame(section)
        row.pack(fill=X)

        self.url_entry = ttkb.Entry(row)
        self.url_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 8))
        add_btn = ttkb.Button(row, text="Add", bootstyle=SUCCESS, command=self.add_url)
        add_btn.pack(side=LEFT)

        # URL list display (Treeview)
        list_frame = ttkb.Frame(section)
        list_frame.pack(fill=BOTH, expand=True, pady=(10, 0))

        columns = ("url",)
        self.url_tree = ttkb.Treeview(list_frame, columns=columns, show="headings", height=6)
        self.url_tree.heading("url", text="URL")
        self.url_tree.column("url", width=600, anchor=W)
        self.url_tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Add default value:
        self.url_list.append("https://www.wunderground.com/dashboard/pws/IHEERB4")
        self.url_tree.insert("", tk.END, values=("https://www.wunderground.com/dashboard/pws/IHEERB4",))
        self.url_entry.delete(0, tk.END)

        scroll = ttkb.Scrollbar(list_frame, orient=VERTICAL, command=self.url_tree.yview)
        self.url_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)

        # actions
        actions = ttkb.Frame(section)
        actions.pack(fill=X, pady=(8, 0))
        remove_btn = ttkb.Button(actions, text="Remove selected", bootstyle=DANGER, command=self.remove_selected_url)
        remove_btn.pack(side=LEFT)
        clear_btn = ttkb.Button(actions, text="Clear", bootstyle=SECONDARY, command=self.clear_urls)
        clear_btn.pack(side=LEFT, padx=6)

    def add_url(self):
        url = self.url_entry.get().strip()
        if not url:
            Messagebox.show_warning("Please enter a URL.", "Empty URL")
            return
        # Basic validation hint (you can extend as needed)
        if not (url.startswith("http://") or url.startswith("https://")):
            if not Messagebox.askyesno("Unusual URL", "URL does not start with http(s). Add anyway?"):
                return

        self.url_list.append(url)
        self.url_tree.insert("", tk.END, values=(url,))
        self.url_entry.delete(0, tk.END)

    def remove_selected_url(self):
        sel = self.url_tree.selection()
        if not sel:
            Messagebox.show_info("No selection", "Please select a URL to remove.")
            return
        # Remove from both tree and internal list
        for item in sel:
            url = self.url_tree.item(item, "values")[0]
            self.url_list = [u for u in self.url_list if u != url]
            self.url_tree.delete(item)

    def clear_urls(self):
        if not self.url_list:
            return
        if Messagebox.askyesno("Clear URLs", "Remove all URLs from the list?"):
            self.url_list.clear()
            for item in self.url_tree.get_children():
                self.url_tree.delete(item)

    # ----- Date Section -----

    def _build_date_section(self):
        section = ttkb.Labelframe(self, text="2) Date range", padding=10)
        section.pack(fill=X, padx=10, pady=(0, 10))

        row = ttkb.Frame(section)
        row.pack(fill=X)

        from_frame = ttkb.Frame(row)
        from_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 8))
        ttkb.Label(from_frame, text="From date").pack(anchor=W)
        # DateEntry without textvariable
        self.from_date_entry = ttkb.DateEntry(
            from_frame,
            firstweekday=0,  # Monday=0, Sunday=6
            startdate=datetime.datetime.now() - datetime.timedelta(1),
            dateformat="%Y-%m-%d",  # optional: choose a fixed format for entry text
        )
        self.from_date_entry.pack(fill=X)

        to_frame = ttkb.Frame(row)
        to_frame.pack(side=LEFT, fill=X, expand=True)
        ttkb.Label(to_frame, text="To date").pack(anchor=W)
        self.to_date_entry = ttkb.DateEntry(
            to_frame,
            firstweekday=0,
            startdate=None,
            dateformat="%Y-%m-%d",
        )
        self.to_date_entry.pack(fill=X)

        note = ttkb.Label(section, text="Tip: Ensure 'From' is not after 'To'.", bootstyle=INFO)
        note.pack(anchor=W, pady=(8, 0))


    # ----- Folder Section -----
    def _build_folder_section(self):
        section = ttkb.Labelframe(self, text="3) Download folder", padding=10)
        section.pack(fill=X, padx=10, pady=(0, 10))

        row = ttkb.Frame(section)
        row.pack(fill=X)

        choose_btn = ttkb.Button(row, text="Choose folder…", bootstyle=PRIMARY, command=self.choose_folder)
        choose_btn.pack(side=LEFT)

        self.folder_label = ttkb.Label(row, textvariable=self.download_folder, bootstyle=SECONDARY, anchor=W)
        self.folder_label.pack(side=LEFT, fill=X, expand=True, padx=8)

        default_dir = os.path.join(os.path.expanduser('~'),"Downloads")
        self.download_folder.set(default_dir)

    def choose_folder(self):
        path = filedialog.askdirectory(title="Select download folder")
        if path:
            self.download_folder.set(path)

    # ----- Footer / Start -----
    def _build_footer(self):
        footer = ttkb.Frame(self, padding=10)
        footer.pack(fill=X, side=BOTTOM)

        self.start_btn = ttkb.Button(footer, text="Start Scraper", bootstyle=SUCCESS, command=self.start_scraper)
        self.start_btn.pack(side=RIGHT)
        self.quit_btn = ttkb.Button(footer, text="Quit", bootstyle=SECONDARY, command=self.destroy)
        self.quit_btn.pack(side=RIGHT, padx=8)

    def start_scraper(self):
        # Validate inputs
        if not self.url_list:
            Messagebox.show_warning("Missing URLs", "Please add at least one source URL.")
            return

        from_date = self.from_date_entry.entry.get().strip()
        to_date = self.to_date_entry.entry.get().strip()
        if not from_date or not to_date:
            Messagebox.show_warning("Missing dates", "Please select both 'From' and 'To' dates.")
            return

        # Try parsing the DateEntry strings (they are in locale-specific format)
        # Alternatively, you can get the datetime.date via .date property:
        try:
            from_dt = self.from_date_entry.get_date().date()
            to_dt = self.to_date_entry.get_date().date()
        except Exception as e:
            Messagebox.show_error("Date parsing error", f"Could not parse dates: {e}")
            return

        if from_dt > to_dt:
            Messagebox.show_warning("Invalid range", "'From date' must be earlier than or equal to 'To date'.")
            return

        folder = self.download_folder.get().strip()
        if not folder:
            Messagebox.show_warning("Missing folder", "Please choose a download folder.")
            return

        # Placeholder: integrate your scraping logic here.
        # For now, we just show a summary.
        summary = (
            f"URLs:\n" + "\n".join(self.url_list) +
            f"\n\nDate range:\nFrom: {from_dt.strftime("%Y-%m-%d")}\nTo:   {to_dt.strftime("%Y-%m-%d")}" +
            f"\n\nDownload folder:\n{folder}"
        )

        Messagebox.show_info(title="Scraper parameters", message=summary)

        # Example: call your scraper function
        # run_scraper(urls=self.url_list, from_date=from_dt, to_date=to_dt, output_dir=folder)
        scrape(self.url_list, from_dt, to_dt, folder)

if __name__ == "__main__":
       app = WeatherScraperGUI()
       app.mainloop()
