
from tkcalendar import DateEntry
from datetime import date
import tkinter as tk
from tkinter import messagebox

class DrivingWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Driving Tracker")
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

        self.drive_count = 0
        self.drive_entries = []

        # Header + Submit button
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Driving Summary", font=title_font).pack(side="left")

        tk.Button(
            header_frame,
            text="SUBMIT",
            font=("Helvetica", 14, "bold"),
            bg="#FF5722",
            fg="green",
            width=12,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#E64A19",
            activeforeground="white",
            command=self.submit
        ).pack(side="right")

        # Drive entry area
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Add first drive
        self.add_drive_row()

        # Add/Remove buttons
        button_frame = tk.Frame(self.top)
        button_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(
            button_frame,
            text="Add Another Drive",
            font=("Helvetica", 14, "bold"),
            bg="#2196F3",
            fg="blue",
            width=14,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#1976D2",
            activeforeground="white",
            command=self.add_drive_row
        ).pack(side="left")

        tk.Button(
            button_frame,
            text="Remove Last Drive",
            font=("Helvetica", 14, "bold"),
            bg="#F44336",
            fg="red",
            width=14,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#D32F2F",
            activeforeground="white",
            command=self.remove_drive_row
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


    def add_drive_row(self):
        row = self.drive_count * 4  # Add vertical spacing between rows
        drive_label = f"Drive {chr(65 + self.drive_count)}"
        tk.Label(self.grid_frame, text=drive_label, font=("Helvetica", 16, "bold")).grid(row=row, column=0, padx=5, sticky="w")

        entries = {}

        def add_entry(col, label, key, width):
            tk.Label(self.grid_frame, text=label, font=("Helvetica", 16)).grid(row=row, column=col, sticky="w", padx=5)
            ent = tk.Entry(self.grid_frame, font=("Helvetica", 14), width=width)
            ent.grid(row=row, column=col + 1, padx=5)
            entries[key] = ent

        # Purpose and destination first
        add_entry(1, "Purpose", "purpose", 10)
        add_entry(3, "Destination", "destination", 8)
        # Then duration and distance (compact)
        add_entry(5, "Duration", "duration", 4)
        add_entry(7, "Distance", "distance", 4)

        self.drive_entries.append(entries)
        self.drive_count += 1

    def remove_drive_row(self):
        if self.drive_count == 0:
            return
        last_row = (self.drive_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.drive_entries.pop()
        self.drive_count -= 1

    def submit(self):
        result = {}
        for i, entries in enumerate(self.drive_entries):
            drive_label = f"Drive {chr(65 + i)}"
            result[drive_label] = {}
            for key, entry in entries.items():
                value = entry.get().strip()
                if key in ["duration", "distance"]:
                    if not value.isdigit():
                        messagebox.showerror("Invalid Input", f"Please enter a whole number for '{drive_label} - {key}'.")
                        return
                    result[drive_label][key] = int(value)
                else:
                    result[drive_label][key] = value if value else "N/A"

        self.callback("Driving", result)
        self.top.destroy()










