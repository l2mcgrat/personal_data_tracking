
from tkcalendar import DateEntry
from datetime import date
import tkinter as tk
from tkinter import messagebox

class WorkDayWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Work Day Tracker")
        self.callback = callback

        # Center and size the window
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        window_width = screen_width // 2
        window_height = screen_height // 2
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Fonts
        header_font = ("Helvetica", 20, "bold")
        label_font = ("Helvetica", 16)
        entry_font = ("Helvetica", 14)

        # Header
        tk.Label(self.top, text="Work Day Summary", font=header_font).pack(pady=20)

        # Entry fields
        self.entries = {}
        
        # Date picker
        date_frame = tk.Frame(self.top)
        date_frame.pack(pady=5)
        
        tk.Label(date_frame, text="Select Date:", font=("Helvetica", 14)).pack(side="left", padx=5)
        
        self.date_picker = DateEntry(
            date_frame,
            width=12,
            font=("Helvetica", 14),
            background="darkblue",
            foreground="white",
            borderwidth=2,
            year=date.today().year,
            month=date.today().month,
            day=date.today().day,
            date_pattern="yyyy-mm-dd"
        )
        self.date_picker.pack(side="left", padx=5)

        def add_entry(label_text, key):
            tk.Label(self.top, text=label_text, font=label_font).pack(pady=5)
            entry = tk.Entry(self.top, font=entry_font)
            entry.pack(pady=5)
            self.entries[key] = entry

        add_entry("Minutes worked:", "worked")
        add_entry("Minutes in meetings:", "meetings")
        add_entry("Minutes walking around:", "walking")
        add_entry("Minutes working on projects:", "projects")

        # Fancy Submit button
        tk.Button(
            self.top,
            text="SUBMIT",
            font=("Helvetica", 16, "bold"),
            bg="#1976D2",
            fg="green",
            width=12,            # Ensures enough horizontal space
            height=2,            # Ensures enough vertical space
            padx=20,             # Internal horizontal padding
            pady=10,             # Internal vertical padding
            relief="raised",
            bd=5,
            activebackground="#0D47A1",
            activeforeground="white",
            command=self.submit
        ).pack(pady=30)

    def submit(self):
        data = {}
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if not value.isdigit():
                messagebox.showerror("Invalid Input", f"Please enter a whole number for '{key.replace('_', ' ')}'.")
                return
            data[key] = int(value)

        # Final check: worked == meetings + walking + projects
        total_other = data["meetings"] + data["walking"] + data["projects"]
        if data["worked"] != total_other:
            messagebox.showerror(
                "Mismatch",
                f"Minutes worked ({data['worked']}) must equal the sum of meetings, walking, and projects ({total_other})."
            )
            return

        self.callback("Work Day", data)
        self.top.destroy()



