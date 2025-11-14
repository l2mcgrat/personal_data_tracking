
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
        title_font = ("Helvetica", 20, "bold")
        label_font = ("Helvetica", 16)
        entry_font = ("Helvetica", 14)

        self.subject_count = 0
        self.subject_entries = []

        # Header + Submit button
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Learning Summary", font=title_font).pack(side="left")

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

        # Entry area
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Add first subject row
        self.add_subject_row()

        # Add/Remove buttons
        button_frame = tk.Frame(self.top)
        button_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(
            button_frame,
            text="Add Another Subject",
            font=("Helvetica", 14, "bold"),
            bg="#03A9F4",
            fg="blue",
            width=18,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#0288D1",
            activeforeground="white",
            command=self.add_subject_row
        ).pack(side="left")

        tk.Button(
            button_frame,
            text="Remove Last Subject",
            font=("Helvetica", 14, "bold"),
            bg="#F44336",
            fg="red",
            width=18,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#D32F2F",
            activeforeground="white",
            command=self.remove_subject_row
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

    def add_subject_row(self):
        row = self.subject_count * 2
        label = f"Subject {chr(65 + self.subject_count)}"
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 13, "bold")).grid(row=row, column=0, padx=5, sticky="w")

        entries = {}

        # Dropdown for subject selection
        subjects = [
            "Philosophy", "Art", "Mathematics", "Physics", "Chemistry", "Biology",
            "Psychology", "Computer Science", "Business/Finance", "Economics", "Politics"
        ]
        subject_var = tk.StringVar(value=subjects[0])
        tk.Label(self.grid_frame, text="Subject", font=("Helvetica", 13)).grid(row=row, column=1, sticky="w", padx=5)
        subject_menu = tk.OptionMenu(self.grid_frame, subject_var, *subjects)
        subject_menu.config(font=("Helvetica", 12))
        subject_menu.grid(row=row, column=2, padx=5)
        entries["subject"] = subject_var

        # Duration
        tk.Label(self.grid_frame, text="Duration", font=("Helvetica", 13)).grid(row=row, column=3, sticky="w", padx=5)
        duration_entry = tk.Entry(self.grid_frame, font=("Helvetica", 12), width=3)
        duration_entry.grid(row=row, column=4, padx=5)
        entries["duration"] = duration_entry

        # Topic
        tk.Label(self.grid_frame, text="Topic", font=("Helvetica", 13)).grid(row=row, column=5, sticky="w", padx=5)
        topic_entry = tk.Entry(self.grid_frame, font=("Helvetica", 12), width=9)
        topic_entry.grid(row=row, column=6, padx=5)
        entries["topic"] = topic_entry

        # Concept Learned
        tk.Label(self.grid_frame, text="Learned", font=("Helvetica", 13)).grid(row=row, column=7, sticky="w", padx=5)
        concept_entry = tk.Entry(self.grid_frame, font=("Helvetica", 12), width=16)
        concept_entry.grid(row=row, column=8, padx=5)
        entries["concept"] = concept_entry

        self.subject_entries.append(entries)
        self.subject_count += 1

    def remove_subject_row(self):
        if self.subject_count == 0:
            return
        last_row = (self.subject_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.subject_entries.pop()
        self.subject_count -= 1

    def submit(self):
        selected_date = self.date_picker.get_date().isoformat()
        result = {"Date": selected_date}
        for i, entries in enumerate(self.subject_entries):
            label = f"Subject {chr(65 + i)}"
            result[label] = {}
            subject = entries["subject"].get()
            result[label]["subject"] = subject

            # Validate duration
            duration_val = entries["duration"].get().strip()
            if not duration_val.isdigit():
                messagebox.showerror("Invalid Input", f"Please enter a whole number for '{label} - duration'.")
                return
            result[label]["duration"] = int(duration_val)

            # Topic
            topic_val = entries["topic"].get().strip()
            if not topic_val:
                messagebox.showerror("Missing Input", f"Please fill in '{label} - topic'.")
                return
            result[label]["topic"] = topic_val

            # Concept Learned
            concept_val = entries["concept"].get().strip()
            if not concept_val:
                messagebox.showerror("Missing Input", f"Please fill in '{label} - concept'.")
                return
            result[label]["concept"] = concept_val

        self.callback("Learning", result)
        self.top.destroy()

