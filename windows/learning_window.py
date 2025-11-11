
from tkcalendar import DateEntry
from datetime import date
import tkinter as tk
from tkinter import messagebox

class LearningWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Learning Tracker")
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

        # Subjects to track
        self.subjects = [
            "Philosophy", "Mathematics", "Physics", "Chemistry", "Biology",
            "Psychology", "Computer Science", "Business/Finance", "Economics", "Politics"
        ]

        self.vars = {}
        self.entry_widgets = {}

        # Header + Submit button row
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Learning Summary", font=header_font).pack(side="left")

        tk.Button(
            header_frame,
            text="SUBMIT",
            font=("Helvetica", 14, "bold"),
            bg="#2196F3",
            fg="green",
            width=12,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#1976D2",
            activeforeground="white",
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

        # Grid layout for checkboxes and entries
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        for row, subject in enumerate(self.subjects):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.grid_frame, text=subject, variable=var, font=label_font,
                                 command=lambda s=subject: self.toggle_entries(s))
            chk.grid(row=row, column=0, sticky="w", padx=5, pady=5)
            self.vars[subject] = var
            self.entry_widgets[subject] = {}

    def toggle_entries(self, subject):
        row = list(self.vars).index(subject)

        # Clear all widgets in this row except the checkbox
        for widget in self.grid_frame.grid_slaves(row=row):
            if widget.grid_info()["column"] != 0:
                widget.destroy()

        self.entry_widgets[subject] = {}

        if not self.vars[subject].get():
            return

        def add_entry(col, label, key, width=12):
            lbl = tk.Label(self.grid_frame, text=label, font=("Helvetica", 12))
            lbl.grid(row=row, column=col, sticky="w", padx=5)
            ent = tk.Entry(self.grid_frame, font=("Helvetica", 12), width=width)
            ent.grid(row=row, column=col + 1, padx=5)
            self.entry_widgets[subject][key] = ent

        add_entry(1, "Duration (min)", "duration", width=5)
        add_entry(3, "Topic", "topic", width=10)
        add_entry(5, "Concept Learned", "concept", width=20)

    def submit(self):
        selected_date = self.date_picker.get_date().isoformat()
        result = {"Date": selected_date}
        for subject, widgets in self.entry_widgets.items():
            if not self.vars[subject].get():
                continue
            result[subject] = {}
            for key, entry in widgets.items():
                value = entry.get().strip()
                if key == "duration":
                    if not value.isdigit():
                        messagebox.showerror("Invalid Input", f"Please enter a whole number for '{subject} - duration'.")
                        return
                    result[subject][key] = int(value)
                else:
                    if not value:
                        messagebox.showerror("Missing Input", f"Please fill in '{subject} - {key}'.")
                        return
                    result[subject][key] = value

        self.callback("Learning", result)
        self.top.destroy()
