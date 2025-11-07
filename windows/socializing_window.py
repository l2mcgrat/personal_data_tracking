
import tkinter as tk
from tkinter import messagebox

class SocializingWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Socializing Tracker")
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

        self.plan_count = 0
        self.plan_entries = []

        # Header + Submit button
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Socializing Summary", font=title_font).pack(side="left")

        tk.Button(
            header_frame,
            text="SUBMIT",
            font=("Helvetica", 14, "bold"),
            bg="#FFEB3B",
            fg="green",
            width=12,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#FBC02D",
            activeforeground="white",
            command=self.submit
        ).pack(side="right")

        # Entry area
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Add first plan
        self.add_plan_row()

        # Add/Remove buttons
        button_frame = tk.Frame(self.top)
        button_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(
            button_frame,
            text="Add Another Plan",
            font=("Helvetica", 14, "bold"),
            bg="#03A9F4",
            fg="blue",
            width=18,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#0288D1",
            activeforeground="white",
            command=self.add_plan_row
        ).pack(side="left")

        tk.Button(
            button_frame,
            text="Remove Last Plan",
            font=("Helvetica", 14, "bold"),
            bg="#F44336",
            fg="red",
            width=18,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#D32F2F",
            activeforeground="white",
            command=self.remove_plan_row
        ).pack(side="right")

    def add_plan_row(self):
        row = self.plan_count * 2
        label = f"Plan {chr(65 + self.plan_count)}"
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 16, "bold")).grid(row=row, column=0, padx=5, sticky="w")

        entries = {}

        def add_entry(col, label, key, width):
            tk.Label(self.grid_frame, text=label, font=("Helvetica", 16)).grid(row=row, column=col, sticky="w", padx=5)
            ent = tk.Entry(self.grid_frame, font=("Helvetica", 14), width=width)
            ent.grid(row=row, column=col + 1, padx=5)
            entries[key] = ent

        add_entry(1, "Friend(s)", "friends", 14)
        add_entry(3, "Duration", "duration", 4)
        add_entry(5, "Activity", "activity", 16)

        self.plan_entries.append(entries)
        self.plan_count += 1

    def remove_plan_row(self):
        if self.plan_count == 0:
            return
        last_row = (self.plan_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.plan_entries.pop()
        self.plan_count -= 1

    def submit(self):
        result = {}
        for i, entries in enumerate(self.plan_entries):
            label = f"Plan {chr(65 + i)}"
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

        self.callback("Socializing", result)
        self.top.destroy()

