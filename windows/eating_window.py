
import tkinter as tk
from tkinter import messagebox

class EatingWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Eating Tracker")
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

        self.meal_count = 0
        self.snack_count = 0
        self.meal_entries = []
        self.snack_entries = []

        # Header + Submit button
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Eating Summary", font=title_font).pack(side="left")

        tk.Button(
            header_frame,
            text="SUBMIT",
            font=("Helvetica", 14, "bold"),
            bg="#C8E6C9",
            fg="green",
            width=14,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#A5D6A7",
            activeforeground="darkgreen",
            command=self.submit
        ).pack(side="right")

        # Entry area
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Add first meal and snack
        self.add_meal_row()
        self.add_snack_row()

        # Add/Remove buttons
        button_frame = tk.Frame(self.top)
        button_frame.pack(fill="x", padx=20, pady=10)

        self._add_button(button_frame, "Add Meal", self.add_meal_row, "#FFCC80", "blue")
        self._add_button(button_frame, "Remove Meal", self.remove_meal_row, "#FF8A65", "red")
        self._add_button(button_frame, "Add Snack", self.add_snack_row, "#B39DDB", "purple")
        self._add_button(button_frame, "Remove Snack", self.remove_snack_row, "#CE93D8", "darkred")

    def _add_button(self, frame, text, command, bg, fg):
        tk.Button(
            frame,
            text=text,
            font=("Helvetica", 14, "bold"),
            bg=bg,
            fg=fg,
            width=16,
            height=2,
            relief="raised",
            bd=5,
            activebackground=bg,
            activeforeground="white",
            command=command
        ).pack(side="left", padx=5)

    def _add_entry(self, frame, row, col, label, key, width, entry_dict):
        tk.Label(frame, text=label, font=("Helvetica", 16)).grid(row=row, column=col, sticky="w", padx=5)
        ent = tk.Entry(frame, font=("Helvetica", 14), width=width)
        ent.grid(row=row, column=col + 1, padx=5)
        entry_dict[key] = ent

    def add_meal_row(self):
        row = self.meal_count * 2
        label = f"Meal {chr(65 + self.meal_count)}"
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 16, "bold")).grid(row=row, column=0, padx=5, sticky="w")

        entries = {}
        self._add_entry(self.grid_frame, row, 1, "Type", "type", 10, entries)
        self._add_entry(self.grid_frame, row, 3, "Carbs", "carbs", 5, entries)
        self._add_entry(self.grid_frame, row, 5, "Fats", "fats", 5, entries)
        self._add_entry(self.grid_frame, row, 7, "Proteins", "proteins", 5, entries)

        self.meal_entries.append(entries)
        self.meal_count += 1

    def remove_meal_row(self):
        if self.meal_count == 0:
            return
        last_row = (self.meal_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.meal_entries.pop()
        self.meal_count -= 1

    def add_snack_row(self):
        row = 100 + self.snack_count * 2
        label = f"Snack {chr(65 + self.snack_count)}"
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 16, "bold")).grid(row=row, column=0, padx=5, sticky="w")

        entries = {}
        self._add_entry(self.grid_frame, row, 1, "Type", "type", 10, entries)
        self._add_entry(self.grid_frame, row, 3, "Carbs", "carbs", 5, entries)
        self._add_entry(self.grid_frame, row, 5, "Fats", "fats", 5, entries)
        self._add_entry(self.grid_frame, row, 7, "Proteins", "proteins", 5, entries)

        self.snack_entries.append(entries)
        self.snack_count += 1

    def remove_snack_row(self):
        if self.snack_count == 0:
            return
        last_row = 100 + (self.snack_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.snack_entries.pop()
        self.snack_count -= 1

    def submit(self):
        result = {"Meals": {}, "Snacks": {}}

        def validate(entries_list, label_prefix, target_dict):
            for i, entries in enumerate(entries_list):
                label = f"{label_prefix} {chr(65 + i)}"
                target_dict[label] = {}
                for key, entry in entries.items():
                    value = entry.get().strip()
                    if key in ["carbs", "fats", "proteins"]:
                        if not value.isdigit():
                            messagebox.showerror("Invalid Input", f"{label} '{key}' must be a whole number.")
                            return False
                        target_dict[label][key] = int(value)
                    else:
                        target_dict[label][key] = value if value else "N/A"
            return True

        if not all([
            validate(self.meal_entries, "Meal", result["Meals"]),
            validate(self.snack_entries, "Snack", result["Snacks"])
        ]):
            return

        self.callback("Eating", result)
        self.top.destroy()




