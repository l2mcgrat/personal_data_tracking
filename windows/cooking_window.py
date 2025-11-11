
from tkcalendar import DateEntry
from datetime import date
import tkinter as tk
from tkinter import messagebox

class CookingWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Cooking Tracker")
        self.callback = callback
        self.meal_counts = {}  # Track meal frequency

        # Make window large and centered
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        window_width = screen_width // 2
        window_height = screen_height // 2
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Fonts
        label_font = ("Helvetica", 16)
        entry_font = ("Helvetica", 14)
        header_font = ("Helvetica", 20, "bold")

        # Header
        tk.Label(self.top, text="Cooking Session", font=header_font).pack(pady=20)

        # Minutes entry
        tk.Label(self.top, text="Minutes spent cooking:", font=label_font).pack(pady=5)
        self.minutes_entry = tk.Entry(self.top, font=entry_font)
        self.minutes_entry.pack(pady=5)

        # Meal name entry
        tk.Label(self.top, text="What meal did you make?", font=label_font).pack(pady=5)
        self.meal_entry = tk.Entry(self.top, font=entry_font)
        self.meal_entry.pack(pady=5)

        # Fancy Submit button
        tk.Button(
            self.top,
            text="SUBMIT",
            font=("Helvetica", 16, "bold"),
            bg="#FF9800",
            fg="green",
            padx=30,
            pady=15,
            relief="raised",
            bd=5,
            activebackground="#F57C00",
            activeforeground="white",
            command=self.submit
        ).pack(pady=30)
        
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


    def submit(self):
        minutes_text = self.minutes_entry.get()
        meal_name = self.meal_entry.get().strip()

        # Validate minutes
        if not minutes_text.isdigit():
            messagebox.showerror("Invalid Input", "Please enter cooking time in whole minutes.")
            return

        minutes = int(minutes_text)

        # Validate meal name
        if not meal_name:
            messagebox.showerror("Missing Meal", "Please enter the name of the meal you made.")
            return

        # Track meal count
        if meal_name in self.meal_counts:
            self.meal_counts[meal_name] += 1
        else:
            self.meal_counts[meal_name] = 1

        # Return data to main
        selected_date = self.date_picker.get_date().isoformat()
        result = {
                "Date": selected_date,
                "minutes": minutes,
                "meal": meal_name
                }
        self.callback("Cooking", result)

        self.top.destroy()


