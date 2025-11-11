
from tkcalendar import DateEntry
from datetime import date
import tkinter as tk
from tkinter import messagebox

class WorkoutsWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Workout Tracker")
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
        label_font = ("Helvetica", 14)
        entry_font = ("Helvetica", 12)

        # Workout categories
        self.muscle_groups = ["Chest", "Back", "Shoulders", "Legs", "Triceps", "Biceps", "Abs"]
        self.cardio = ["Running", "Swimming"]
        self.sport = "Sport"

        self.vars = {}
        self.entry_widgets = {}

        # Header + Submit button row
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Workout Summary", font=header_font).pack(side="left")

        tk.Button(
            header_frame,
            text="SUBMIT",
            font=("Helvetica", 14, "bold"),
            bg="#4CAF50",
            fg="green",
            width=12,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#388E3C",
            activeforeground="white",
            command=self.submit
        ).pack(side="right")

        # Grid layout for checkboxes and entries
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        all_workouts = self.muscle_groups + self.cardio + [self.sport]

        for row, name in enumerate(all_workouts):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.grid_frame, text=name, variable=var, font=label_font,
                                 command=lambda n=name: self.toggle_entries(n))
            chk.grid(row=row, column=0, sticky="w", padx=5, pady=5)
            self.vars[name] = var
            self.entry_widgets[name] = {}
            
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

    def toggle_entries(self, name):
        row = list(self.vars).index(name)
    
        # Clear previous widgets in this row (columns 1–8)
        for col in range(1, 9):
            for widget in self.grid_frame.grid_slaves(row=row, column=col):
                widget.destroy()
    
        self.entry_widgets[name] = {}
    
        if not self.vars[name].get():
            return
    
        def add_entry(col, label, key, width=8):
            lbl = tk.Label(self.grid_frame, text=label, font=("Helvetica", 12))
            lbl.grid(row=row, column=col, sticky="w", padx=5)
            ent = tk.Entry(self.grid_frame, font=("Helvetica", 12), width=width)
            ent.grid(row=row, column=col + 1, padx=5)
            self.entry_widgets[name][key] = ent
    
        if name in self.muscle_groups:
            add_entry(1, "Exercises", "exercises")
            add_entry(3, "Sets", "sets")
            add_entry(5, "Rep Min", "rep_min")
            add_entry(7, "Rep Max", "rep_max")
        elif name in self.cardio:
            add_entry(1, "Distance (m)", "distance")
        elif name == self.sport:
            add_entry(1, "Duration", "duration")
            add_entry(3, "Sport", "type", width=8)

    def submit(self):
        selected_date = self.date_picker.get_date().isoformat()
        result = {"Date": selected_date}
        for name, widgets in self.entry_widgets.items():
            if not self.vars[name].get():
                continue
            result[name] = {}
            for key, entry in widgets.items():
                value = entry.get().strip()
                if key != "type":
                    if not value.isdigit():
                        messagebox.showerror("Invalid Input", f"Please enter a whole number for '{name} - {key}'.")
                        return
                    result[name][key] = int(value)
                else:
                    if not value:
                        messagebox.showerror("Missing Input", f"Please enter the type of sport.")
                        return
                    result[name][key] = value

        self.callback("Workouts", result)
        self.top.destroy()
