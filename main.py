
import tkinter as tk
import csv
from datetime import date, timedelta
from tkcalendar import DateEntry
import os

# Import all your window classes here
from windows.work_day_window import WorkDayWindow
from windows.cooking_window import CookingWindow
from windows.workouts_window import WorkoutsWindow
from windows.learning_window import LearningWindow
from windows.driving_window import DrivingWindow
from windows.leetcode_window import LeetcodeWindow
from windows.coding_projects_window import CodingProjectsWindow
from windows.career_prep_window import CareerPrepWindow
from windows.sleep_window import SleepWindow
from windows.meditating_window import MeditatingWindow
from windows.music_window import MusicWindow
from windows.gaming_window import GamingWindow
from windows.texting_calling_window import TextingCallingWindow
from windows.socializing_window import SocializingWindow
from windows.eating_window import EatingWindow
from windows.media_window import MediaWindow
from windows.miscellaneous_window import MiscellaneousWindow

from windows.dummy_window import DummyWindow

class CategorySelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Health Tracker")
        self.open_windows = 0

        # Center window and set to half screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = screen_width // 2
        window_height = screen_height // 2
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Fonts
        header_font = ("Helvetica", 18, "bold")
        checkbox_font = ("Helvetica", 14)

        # Map all categories to their window classes
        self.category_windows = {
            "Work Day": WorkDayWindow,
            "Cooking": CookingWindow,
            "Workouts": WorkoutsWindow,
            "Learning": LearningWindow,
            "Driving": DrivingWindow,
            "Leetcode": LeetcodeWindow,
            "Coding Projects": CodingProjectsWindow,
            "Career Prep": CareerPrepWindow,
            "Miscellaneous": MiscellaneousWindow,
            "Sleep": SleepWindow,
            "Meditating": MeditatingWindow,
            "Music": MusicWindow,
            "Gaming": GamingWindow,
            "Messaging_Calling": TextingCallingWindow,
            "Socializing": SocializingWindow,
            "Eating": EatingWindow,
            "Media": MediaWindow
        }

        # Split into breakdown and rebuild categories
        self.breakdown = [key for key in list(self.category_windows)[:9]]
        self.rebuild = [key for key in list(self.category_windows)[9:]]

        self.vars = {}
        self.selected = []

        # Layout frames
        breakdown_frame = tk.LabelFrame(root, text="BREAKDOWN", font=header_font, padx=10, pady=10)
        rebuild_frame = tk.LabelFrame(root, text="REBUILD", font=header_font, padx=10, pady=10)
        breakdown_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        rebuild_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Add checkboxes
        for category in self.breakdown:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(breakdown_frame, text=category, variable=var, font=checkbox_font, anchor="w")
            chk.pack(fill="x", padx=5, pady=2)
            self.vars[category] = var

        for category in self.rebuild:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(rebuild_frame, text=category, variable=var, font=checkbox_font, anchor="w")
            chk.pack(fill="x", padx=5, pady=2)
            self.vars[category] = var

        # Fancy Submit button
        submit_btn = tk.Button(
            root,
            text="SUBMIT",
            font=("Helvetica", 16, "bold"),
            bg="#4CAF50",
            fg="green",
            padx=30,
            pady=15,
            relief="raised",
            bd=5,
            activebackground="#388E3C",
            activeforeground="white",
            command=self.submit)
        submit_btn.pack(pady=30)

    def submit(self):
        self.selected = [name for name, var in self.vars.items() if var.get()]
        print("Selected categories:", self.selected)

        self.root.after(200, self.launch_selected_windows)
        self.root.withdraw()

    def launch_selected_windows(self):
        for name in self.selected:
            window_class = self.category_windows.get(name)
            if window_class:
                self.open_windows += 1
                window_class(tk.Toplevel(), self.handle_data)

    def handle_data(self, name, data):
        print(f"{name} returned:", data)
        self.open_windows -= 1
        print(f"Remaining open windows: {self.open_windows}")
    
        # Step 1: Get selected date from data (or default to today)
        selected_date = data.get("Date", date.today().isoformat())
    
        # Step 2: Flatten nested data
        flat_data = {"Date": selected_date}
        for section, values in data.items():
            if section == "Date":
                continue
            if isinstance(values, dict):
                for key, value in values.items():
                    flat_data[f"{section} - {key}"] = value
            else:
                flat_data[section] = values
    
        # Step 3: Prepare CSV file
        filename = os.path.join("data", f"{name}.csv")
        rows = []
    
        # Step 4: Load existing data if file exists
        if os.path.isfile(filename):
            with open(filename, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or flat_data.keys()
                for row in reader:
                    rows.append(row)
        else:
            fieldnames = flat_data.keys()
    
        # Step 5: Replace row if date matches, else append
        updated = False
        for i, row in enumerate(rows):
            if row.get("Date") == selected_date:
                rows[i] = flat_data
                updated = True
                break
        if not updated:
            rows.append(flat_data)
    
        # Step 6: Write updated data back to file
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
        # Step 7: Exit if all windows are closed
        if self.open_windows == 0:
            print("All windows closed. Exiting app.")
            self.root.quit()


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = CategorySelector(root)
    root.mainloop()
