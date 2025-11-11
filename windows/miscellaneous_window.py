
from tkcalendar import DateEntry
from datetime import date
import tkinter as tk
from tkinter import messagebox

class MiscellaneousWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Miscellaneous Tracker")
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
        title_font = ("Helvetica", 20, "bold")
        label_font = ("Helvetica", 16)
        entry_font = ("Helvetica", 14)

        self.drug_count = 0
        self.other_count = 0
        self.drug_entries = []
        self.other_entries = []

        # Header + Submit button
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Miscellaneous Summary", font=title_font).pack(side="left")

        tk.Button(
            header_frame,
            text="SUBMIT",
            font=("Helvetica", 14, "bold"),
            bg="#FFF9C4",
            fg="green",
            height=2,
            relief="raised",
            bd=5,
            activebackground="#F0F4C3",
            activeforeground="darkgreen",
            command=self.submit
        ).pack(side="right")
        
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

        # Entry area
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Fixed entries
        self.fixed_entries = {}
        self._add_fixed_entry("Teeth Brushed", 0)
        self._add_fixed_entry("Showers", 1)
        self._add_fixed_entry("Liters of Water Drank", 2)

        # Add first drug and other
        self.add_drug_row()
        self.add_other_row()

        # Add/Remove buttons
        button_frame = tk.Frame(self.top)
        button_frame.pack(fill="x", padx=5, pady=5)

        self._add_button(button_frame, "+ Drug", self.add_drug_row, "#FFAB91", "blue")
        self._add_button(button_frame, "- Drug", self.remove_drug_row, "#FF8A65", "red")
        self._add_button(button_frame, "+ Other", self.add_other_row, "#B39DDB", "purple")
        self._add_button(button_frame, "- Other", self.remove_other_row, "#CE93D8", "darkred")

    def _add_button(self, frame, text, command, bg, fg):
        tk.Button(
            frame,
            text=text,
            font=("Helvetica", 14, "bold"),
            bg=bg,
            fg=fg,
            height=2,
            relief="raised",
            bd=5,
            activebackground=bg,
            activeforeground="white",
            command=command
        ).pack(side="left", padx=3)

    def _add_fixed_entry(self, label, row):
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 16)).grid(row=row, column=0, sticky="w", padx=5)
        ent = tk.Entry(self.grid_frame, font=("Helvetica", 14), width=5)
        ent.grid(row=row, column=1, padx=5)
        self.fixed_entries[label] = ent

    def _add_entry(self, frame, row, col, label, key, width, entry_dict):
        tk.Label(frame, text=label, font=("Helvetica", 16)).grid(row=row, column=col, sticky="w", padx=5)
        ent = tk.Entry(frame, font=("Helvetica", 14), width=width)
        ent.grid(row=row, column=col + 1, padx=5)
        entry_dict[key] = ent

    def add_drug_row(self):
        row = 10 + self.drug_count * 2
        label = f"Drug {chr(65 + self.drug_count)}"
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 16, "bold")).grid(row=row, column=0, padx=5, sticky="w")

        entries = {}
        self._add_entry(self.grid_frame, row, 1, "Name", "name", 12, entries)
        self._add_entry(self.grid_frame, row, 3, "Dosage", "dosage", 4, entries)
        self._add_entry(self.grid_frame, row, 5, "Notes", "notes", 12, entries)

        self.drug_entries.append(entries)
        self.drug_count += 1

    def remove_drug_row(self):
        if self.drug_count == 0:
            return
        last_row = 10 + (self.drug_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.drug_entries.pop()
        self.drug_count -= 1

    def add_other_row(self):
        row = 100 + self.other_count * 2
        label = f"Other {chr(65 + self.other_count)}"
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 16, "bold")).grid(row=row, column=0, padx=5, sticky="w")

        entries = {}
        self._add_entry(self.grid_frame, row, 1, "Description", "description", 12, entries)
        self._add_entry(self.grid_frame, row, 3, "Duration", "duration", 4, entries)
        self._add_entry(self.grid_frame, row, 5, "Notes", "notes", 12, entries)

        self.other_entries.append(entries)
        self.other_count += 1

    def remove_other_row(self):
        if self.other_count == 0:
            return
        last_row = 100 + (self.other_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.other_entries.pop()
        self.other_count -= 1

    def submit(self):
        selected_date = self.date_picker.get_date().isoformat()
        result = {"Date": selected_date,
            "Fixed": {},
            "Drugs": {},
            "Other": {}
        }

        # Validate fixed entries
        for label, entry in self.fixed_entries.items():
            value = entry.get().strip()
            if not value.isdigit():
                messagebox.showerror("Invalid Input", f"{label} must be a whole number.")
                return
            result["Fixed"][label] = int(value)

        # Validate drugs
        for i, entries in enumerate(self.drug_entries):
            label = f"Drug {chr(65 + i)}"
            result["Drugs"][label] = {}
            for key, entry in entries.items():
                value = entry.get().strip()
                result["Drugs"][label][key] = value if value else "N/A"

        # Validate other
        for i, entries in enumerate(self.other_entries):
            label = f"Other {chr(65 + i)}"
            result["Other"][label] = {}
            for key, entry in entries.items():
                value = entry.get().strip()
                if key == "duration":
                    if not value.isdigit():
                        messagebox.showerror("Invalid Input", f"{label} '{key}' must be a whole number.")
                        return
                    result["Other"][label][key] = int(value)
                else:
                    result["Other"][label][key] = value if value else "N/A"

        self.callback("Miscellaneous", result)
        self.top.destroy()






