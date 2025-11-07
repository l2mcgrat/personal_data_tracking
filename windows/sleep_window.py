
import tkinter as tk
from tkinter import messagebox

class SleepWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Sleep Tracker")
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
        title_font = ("Helvetica", 24, "bold")
        label_font = ("Helvetica", 16)
        entry_font = ("Helvetica", 16)
        button_font = ("Helvetica", 18, "bold")

        # Header + Submit button
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Sleep Summary", font=title_font).pack(side="left")

        tk.Button(
            header_frame,
            text="SUBMIT",
            font=button_font,
            bg="#E8F5E9",
            fg="green",
            width=14,
            height=2,
            relief="raised",
            bd=5,
            activebackground="#C8E6C9",
            activeforeground="darkgreen",
            command=self.submit
        ).pack(side="right")

        # Main sleep entry
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(self.grid_frame, text="Main Sleep", font=("Helvetica", 14, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.sleep_entries = {}
        self._add_entry(self.grid_frame, 0, 1, "Start", "start", 8, self.sleep_entries)
        self._add_entry(self.grid_frame, 0, 3, "End", "end", 8, self.sleep_entries)
        self._add_entry(self.grid_frame, 0, 5, "Duration (mins)", "duration", 4, self.sleep_entries)
        self._add_entry(self.grid_frame, 0, 7, "Quality (1–10)", "quality", 3, self.sleep_entries)

        # Nap checkbox
        self.nap_var = tk.BooleanVar()
        tk.Checkbutton(self.grid_frame, text="Include Nap", variable=self.nap_var, font=label_font, command=self.toggle_nap).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=10)

        # Nap entry placeholder
        self.nap_entries = {}
        self.nap_row = 2

    def _add_entry(self, frame, row, col, label, key, width, entry_dict):
        tk.Label(frame, text=label, font=("Helvetica", 15)).grid(row=row, column=col, sticky="w", padx=3)
        ent = tk.Entry(frame, font=("Helvetica", 14), width=width)
        ent.grid(row=row, column=col + 1, padx=3)
        entry_dict[key] = ent

    def toggle_nap(self):
        if self.nap_var.get():
            tk.Label(self.grid_frame, text="Nap", font=("Helvetica", 15, "bold")).grid(row=self.nap_row, column=0, padx=3, sticky="w")
            self._add_entry(self.grid_frame, self.nap_row, 1, "Start", "start", 8, self.nap_entries)
            self._add_entry(self.grid_frame, self.nap_row, 3, "End", "end", 8, self.nap_entries)
            self._add_entry(self.grid_frame, self.nap_row, 5, "Duration (min)", "duration", 4, self.nap_entries)
            self._add_entry(self.grid_frame, self.nap_row, 7, "Quality (1–10)", "quality", 3, self.nap_entries)
        else:
            for widget in self.grid_frame.grid_slaves():
                if widget.grid_info()["row"] == self.nap_row:
                    widget.destroy()
            self.nap_entries = {}

    def submit(self):
        result = {"Main Sleep": {}}
        for key, entry in self.sleep_entries.items():
            value = entry.get().strip()
            if key in ["duration", "quality"] and not value.isdigit():
                messagebox.showerror("Invalid Input", f"Main Sleep '{key}' must be a whole number.")
                return
            result["Main Sleep"][key] = value if value else "N/A"

        if self.nap_entries:
            result["Nap"] = {}
            for key, entry in self.nap_entries.items():
                value = entry.get().strip()
                if key in ["duration", "quality"] and not value.isdigit():
                    messagebox.showerror("Invalid Input", f"Nap '{key}' must be a whole number.")
                    return
                result["Nap"][key] = value if value else "N/A"

        self.callback("Sleep", result)
        self.top.destroy()
