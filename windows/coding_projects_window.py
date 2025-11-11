
from tkcalendar import DateEntry
from datetime import date
import tkinter as tk
from tkinter import messagebox

class CodingProjectsWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Coding Projects Tracker")
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
        title_font = ("Helvetica", 16, "bold")
        label_font = ("Helvetica", 12)
        entry_font = ("Helvetica", 12)

        self.project_count = 0
        self.project_entries = []

        # Header + Submit button
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(header_frame, text="Coding Projects Summary", font=title_font).pack(side="left")

        tk.Button(
            header_frame,
            text="SUBMIT",
            font=("Helvetica", 12, "bold"),
            bg="#FF9800",
            fg="green",
            width=12,
            height=1,
            relief="raised",
            bd=5,
            activebackground="#FB8C00",
            activeforeground="white",
            command=self.submit
        ).pack(side="right")

        # Entry area
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # Add first project
        self.add_project_row()

        # Add/Remove buttons
        button_frame = tk.Frame(self.top)
        button_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(
            button_frame,
            text="Add Another Project",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="blue",
            width=16,
            height=1,
            relief="raised",
            bd=5,
            activebackground="#388E3C",
            activeforeground="white",
            command=self.add_project_row
        ).pack(side="left")

        tk.Button(
            button_frame,
            text="Remove Last Project",
            font=("Helvetica", 12, "bold"),
            bg="#F44336",
            fg="red",
            width=16,
            height=1,
            relief="raised",
            bd=5,
            activebackground="#D32F2F",
            activeforeground="white",
            command=self.remove_project_row
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

    def add_project_row(self):
        row = self.project_count * 2
        label = f"Project {chr(65 + self.project_count)}"
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 12, "bold")).grid(row=row, column=0, padx=2, sticky="w")

        entries = {}

        def add_entry(col, label, key, width):
            tk.Label(self.grid_frame, text=label, font=("Helvetica", 12)).grid(row=row, column=col, sticky="w", padx=2)
            ent = tk.Entry(self.grid_frame, font=("Helvetica", 12), width=width)
            ent.grid(row=row, column=col + 1, padx=2)
            entries[key] = ent

        add_entry(1, "Name", "name", 20)
        add_entry(3, "Time", "duration", 3)
        add_entry(5, "Change(s)", "changes", 16)
        add_entry(7, "Fix(s)", "fixes", 16)

        self.project_entries.append(entries)
        self.project_count += 1

    def remove_project_row(self):
        if self.project_count == 0:
            return
        last_row = (self.project_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.project_entries.pop()
        self.project_count -= 1

    def submit(self):
        result = {}
        for i, entries in enumerate(self.project_entries):
            label = f"Project {chr(65 + i)}"
            result[label] = {}
            for key, entry in entries.items():
                value = entry.get().strip()
                if key == "duration":
                    if not value.isdigit():
                        messagebox.showerror("Invalid Input", f"Please enter a whole number for '{label} - {key}'.")
                        return
                    result[label][key] = int(value)
                else:
                    result[label][key] = value if value else "N/A"

        self.callback("Coding Projects", result)
        self.top.destroy()











