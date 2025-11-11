
from tkcalendar import DateEntry
from datetime import date
import tkinter as tk
from tkinter import messagebox

class CareerPrepWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Career Prep Tracker")
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

        self.interview_count = 0
        self.interview_entries = []

        # Header + Submit button
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(header_frame, text="Career Prep Summary", font=title_font).pack(side="left")

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

        # Add first interview
        self.add_interview_row()

        # Add/Remove buttons
        button_frame = tk.Frame(self.top)
        button_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(
            button_frame,
            text="Add Another Interview",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="blue",
            width=16,
            height=1,
            relief="raised",
            bd=5,
            activebackground="#388E3C",
            activeforeground="white",
            command=self.add_interview_row
        ).pack(side="left")

        tk.Button(
            button_frame,
            text="Remove Last Interview",
            font=("Helvetica", 12, "bold"),
            bg="#F44336",
            fg="red",
            width=16,
            height=1,
            relief="raised",
            bd=5,
            activebackground="#D32F2F",
            activeforeground="white",
            command=self.remove_interview_row
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


        # Optional checkboxes
        self.optional_frame = tk.Frame(self.top)
        self.optional_frame.pack(fill="x", padx=10, pady=5)

        self.resume_var = tk.BooleanVar()
        self.linkedin_var = tk.BooleanVar()

        tk.Checkbutton(self.optional_frame, text="Resume", variable=self.resume_var, command=self.toggle_resume).pack(side="left", padx=5)
        tk.Checkbutton(self.optional_frame, text="LinkedIn", variable=self.linkedin_var, command=self.toggle_linkedin).pack(side="left", padx=5)

        # Placeholder for optional rows
        self.resume_entries = {}
        self.linkedin_entries = {}

        # Applications section (bottom center)
        self.application_entries = {}
        app_row = 999
        tk.Label(self.grid_frame, text="# Applications", font=label_font).grid(row=app_row, column=3, padx=2, pady=10, sticky="e")
        app_entry = tk.Entry(self.grid_frame, font=entry_font, width=6)
        app_entry.grid(row=app_row, column=4, padx=2, pady=10, sticky="w")
        self.application_entries["applications"] = app_entry

    def add_interview_row(self):
        row = self.interview_count * 2
        label = f"Interview {chr(65 + self.interview_count)}"
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 12, "bold")).grid(row=row, column=0, padx=2, sticky="w")

        entries = {}
        self._add_entry(self.grid_frame, row, 1, "Title", "title", 12, entries)
        self._add_entry(self.grid_frame, row, 3, "Pay Range", "pay_range", 10, entries)
        self._add_entry(self.grid_frame, row, 5, "Duration", "duration", 4, entries)
        self._add_entry(self.grid_frame, row, 7, "Link", "link", 16, entries)

        self.interview_entries.append(entries)
        self.interview_count += 1

    def remove_interview_row(self):
        if self.interview_count == 0:
            return
        last_row = (self.interview_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.interview_entries.pop()
        self.interview_count -= 1

    def _add_entry(self, frame, row, col, label, key, width, entry_dict):
        tk.Label(frame, text=label, font=("Helvetica", 12)).grid(row=row, column=col, sticky="w", padx=2)
        ent = tk.Entry(frame, font=("Helvetica", 12), width=width)
        ent.grid(row=row, column=col + 1, padx=2)
        entry_dict[key] = ent

    def toggle_resume(self):
        row = self.interview_count * 2 + 100
        if self.resume_var.get():
            tk.Label(self.grid_frame, text="Resume", font=("Helvetica", 12, "bold")).grid(row=row, column=0, padx=2, sticky="w")
            self._add_entry(self.grid_frame, row, 1, "Duration", "duration", 6, self.resume_entries)
            self._add_entry(self.grid_frame, row, 3, "File Name", "file_name", 14, self.resume_entries)
        else:
            for widget in self.grid_frame.grid_slaves():
                if widget.grid_info()["row"] == row:
                    widget.destroy()
            self.resume_entries = {}

    def toggle_linkedin(self):
        row = self.interview_count * 2 + 101
        if self.linkedin_var.get():
            tk.Label(self.grid_frame, text="LinkedIn", font=("Helvetica", 12, "bold")).grid(row=row, column=0, padx=2, sticky="w")
            self._add_entry(self.grid_frame, row, 1, "Duration", "duration", 6, self.linkedin_entries)
            self._add_entry(self.grid_frame, row, 3, "Last Activity", "last_activity", 12, self.linkedin_entries)
        else:
            for widget in self.grid_frame.grid_slaves():
                if widget.grid_info()["row"] == row:
                    widget.destroy()
            self.linkedin_entries = {}

    def submit(self):
        result = {}

        # Interviews
        for i, entries in enumerate(self.interview_entries):
            label = f"Interview {chr(65 + i)}"
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

        # Resume
        if self.resume_entries:
            resume_duration = self.resume_entries["duration"].get().strip()
            if not resume_duration.isdigit():
                messagebox.showerror("Invalid Input", "Resume duration must be a whole number.")
                return
            result["Resume"] = {
                "duration": int(resume_duration),
                "file_name": self.resume_entries["file_name"].get().strip() or "N/A"
            }

        # LinkedIn
        if self.linkedin_entries:
            linkedin_duration = self.linkedin_entries["duration"].get().strip()
            if not linkedin_duration.isdigit():
                messagebox.showerror("Invalid Input", "LinkedIn duration must be a whole number.")
                return
            result["LinkedIn"] = {
                "duration": int(linkedin_duration),
                "last_activity": self.linkedin_entries["last_activity"].get().strip() or "N/A"
            }

        # Applications
        applications = self.application_entries["applications"].get().strip()
        if not applications.isdigit():
            messagebox.showerror("Invalid Input", "Number of job applications must be a whole number.")
            return
        result["Applications"] = {
            "count": int(applications)
        }

        self.callback("Career Prep", result)
        self.top.destroy()



