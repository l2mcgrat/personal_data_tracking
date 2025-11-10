import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import date

class MediaWindow:
    def __init__(self, master, callback):
        self.top = master
        self.top.title("Media Tracker")
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

        self.youtube_count = 0
        self.anime_count = 0
        self.series_count = 0

        self.youtube_entries = []
        self.anime_entries = []
        self.series_entries = []

        # Header + Submit button
        header_frame = tk.Frame(self.top)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Media Summary", font=title_font).pack(side="left")

        tk.Button(
            header_frame,
            text="SUBMIT",
            font=("Helvetica", 14, "bold"),
            bg="#FFF176",
            fg="green",
            height=2,
            relief="raised",
            bd=5,
            activebackground="#FDD835",
            activeforeground="darkgreen",
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

        # Entry area
        self.grid_frame = tk.Frame(self.top)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Add first entries
        self.add_youtube_row()
        self.add_anime_row()
        self.add_series_row()

        # Add/Remove buttons
        button_frame = tk.Frame(self.top)
        button_frame.pack(fill="x", padx=5, pady=5)

        self._add_button(button_frame, "+ YouTube", self.add_youtube_row, "#FF8A65", "blue")
        self._add_button(button_frame, "- YouTube", self.remove_youtube_row, "#FF7043", "red")
        self._add_button(button_frame, "+ Anime", self.add_anime_row, "#CE93D8", "purple")
        self._add_button(button_frame, "- Anime", self.remove_anime_row, "#BA68C8", "darkred")
        self._add_button(button_frame, "+ Series", self.add_series_row, "#90CAF9", "navy")
        self._add_button(button_frame, "- Series", self.remove_series_row, "#64B5F6", "darkblue")

    def _add_button(self, frame, text, command, bg, fg):
        tk.Button(
            frame,
            text=text,
            font=("Helvetica", 14, "bold"),
            bg=bg,
            fg=fg,
            height=2,
            relief="raised",
            bd=5,
            activebackground=bg,
            activeforeground="white",
            command=command
        ).pack(side="left", padx=3)

    def _add_entry(self, frame, row, col, label, key, width, entry_dict):
        tk.Label(frame, text=label, font=("Helvetica", 16)).grid(row=row, column=col, sticky="w", padx=5)
        ent = tk.Entry(frame, font=("Helvetica", 14), width=width)
        ent.grid(row=row, column=col + 1, padx=5)
        entry_dict[key] = ent

    def _add_media_row(self, label_prefix, count, entries_list, row_offset):
        row = row_offset + count * 2
        label = f"{label_prefix} {chr(65 + count)}"
        tk.Label(self.grid_frame, text=label, font=("Helvetica", 16, "bold")).grid(row=row, column=0, padx=5, sticky="w")

        entries = {}
        self._add_entry(self.grid_frame, row, 1, "Title", "title", 20, entries)
        self._add_entry(self.grid_frame, row, 3, "Duration", "duration", 5, entries)
        self._add_entry(self.grid_frame, row, 5, "Rating (1–100)", "rating", 5, entries)

        entries_list.append(entries)

    def add_youtube_row(self):
        self._add_media_row("YouTube", self.youtube_count, self.youtube_entries, 0)
        self.youtube_count += 1

    def remove_youtube_row(self):
        if self.youtube_count == 0:
            return
        last_row = (self.youtube_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.youtube_entries.pop()
        self.youtube_count -= 1

    def add_anime_row(self):
        self._add_media_row("Anime", self.anime_count, self.anime_entries, 100)
        self.anime_count += 1

    def remove_anime_row(self):
        if self.anime_count == 0:
            return
        last_row = 100 + (self.anime_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.anime_entries.pop()
        self.anime_count -= 1

    def add_series_row(self):
        self._add_media_row("Series", self.series_count, self.series_entries, 200)
        self.series_count += 1

    def remove_series_row(self):
        if self.series_count == 0:
            return
        last_row = 200 + (self.series_count - 1) * 2
        for widget in self.grid_frame.grid_slaves():
            if widget.grid_info()["row"] == last_row:
                widget.destroy()
        self.series_entries.pop()
        self.series_count -= 1

    def submit(self):
        selected_date = self.date_picker.get_date().isoformat()
        result = {
            "Date": selected_date,
            "YouTube": {},
            "Anime": {},
            "Series": {}
        }

        def validate_and_store(entries_list, label_prefix, target_dict):
            for i, entries in enumerate(entries_list):
                label = f"{label_prefix} {chr(65 + i)}"
                target_dict[label] = {}
                for key, entry in entries.items():
                    value = entry.get().strip()
                    if key == "duration":
                        if not value.isdigit():
                            messagebox.showerror("Invalid Input", f"{label} '{key}' must be a whole number.")
                            return False
                        target_dict[label][key] = int(value)
                    elif key == "rating":
                        if not value.isdigit() or not (1 <= int(value) <= 100):
                            messagebox.showerror("Invalid Input", f"{label} '{key}' must be a number from 1 to 100.")
                            return False
                        target_dict[label][key] = int(value)
                    else:
                        target_dict[label][key] = value if value else "N/A"
            return True

        if not all([
            validate_and_store(self.youtube_entries, "YouTube", result["YouTube"]),
            validate_and_store(self.anime_entries, "Anime", result["Anime"]),
            validate_and_store(self.series_entries, "Series", result["Series"])
        ]):
            return

        self.callback("Media", result)
        self.top.destroy()






