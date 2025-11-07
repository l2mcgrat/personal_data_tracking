
import tkinter as tk
from tkinter import messagebox

class LeetcodeWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Leetcode Tracker")
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

        self.problem_count = 0
        self.problem_entries = []

        # Header + Submit button
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Leetcode Summary", font=title_font).pack(side="left")

        tk.Button(
            header_frame,
            text="SUBMIT",
            font=("Helvetica", 14, "bold"),
            bg="#FF9800",
            fg="green",
            width=12,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#FB8C00",
            activeforeground="white",
            command=self.submit
        ).pack(side="right")

        # Entry area
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Add first problem
        self.add_problem_row()

        # Add/Remove buttons
        button_frame = tk.Frame(self.top)
        button_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(
            button_frame,
            text="Add Another Problem",
            font=("Helvetica", 14, "bold"),
            bg="#4CAF50",
            fg="blue",
            width=16,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#388E3C",
            activeforeground="white",
            command=self.add_problem_row
        ).pack(side="left")

        tk.Button(
            button_frame,
            text="Remove Last Problem",
            font=("Helvetica", 14, "bold"),
            bg="#F44336",
            fg="red",
            width=16,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#D32F2F",
            activeforeground="white",
            command=self.remove_problem_row
        ).pack(side="right")

    def add_problem_row(self):
        row = self.problem_count * 4
        label = f"Problem {chr(65 + self.problem_count)}"
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 16, "bold")).grid(row=row, column=0, padx=5, sticky="w")

        entries = {}

        def add_entry(col, label, key, width):
            tk.Label(self.grid_frame, text=label, font=("Helvetica", 13)).grid(row=row, column=col, sticky="w", padx=2)
            ent = tk.Entry(self.grid_frame, font=("Helvetica", 12), width=width)
            ent.grid(row=row, column=col + 1, padx=2)
            entries[key] = ent

        add_entry(1, "#", "number", 4)
        add_entry(3, "Name", "name", 14)
        add_entry(5, "Difficulty", "difficulty", 4)
        add_entry(7, "Time", "duration", 3)
        add_entry(9, "Concept(s)", "concept", 14)

        self.problem_entries.append(entries)
        self.problem_count += 1

    def remove_problem_row(self):
        if self.problem_count == 0:
            return
        last_row = (self.problem_count - 1) * 4
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.problem_entries.pop()
        self.problem_count -= 1

    def submit(self):
        result = {}
        for i, entries in enumerate(self.problem_entries):
            label = f"Problem {chr(65 + i)}"
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

        self.callback("Leetcode", result)
        self.top.destroy()
