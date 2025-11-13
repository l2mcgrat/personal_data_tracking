
from collections import defaultdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk
import csv
from datetime import date, timedelta
from tkcalendar import DateEntry
import os, string

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
            "Messaging/Calling": TextingCallingWindow,
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
        flat_data = {"Date": data.get("Date", date.today().isoformat())}
        
        for section, values in data.items():
            if section == "Date":
                continue
            if isinstance(values, dict):
                for sublabel, subvalues in values.items():
                    if isinstance(subvalues, dict):
                        for key, value in subvalues.items():
                            flat_data[f"{section} - {sublabel} - {key}"] = value
                    else:
                        flat_data[f"{section} - {sublabel}"] = subvalues
            else:
                flat_data[section] = values
    
        # Step 3: Prepare CSV file
        filename = os.path.join("data", f"{name}.csv")
        rows = []
    
        # Step 4: Load existing data if file exists
        if os.path.isfile(filename):
            with open(filename, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                existing_fieldnames = reader.fieldnames or []
                new_fieldnames = list(flat_data.keys())
                fieldnames = list(dict.fromkeys(existing_fieldnames + new_fieldnames))
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
            print("All windows closed. Consolidating Data into one .csv file...")
            function_caller()
            self.root.quit()

def function_caller():
    # Generate master_log.csv
    consolidate_data()
    
    # Get data as dataframe object
    master_df = pd.read_csv("data/master_log.csv")
    master_df["Date"] = pd.to_datetime(master_df["Date"], errors="coerce")
    
    # Call visualization generator functions
    visualize_daily_activity(master_df, output_dir="data/plots")
    visualize_daily_meals(master_df, output_dir="data/plots")

def consolidate_data():
    from collections import defaultdict

    master_rows = []
    data_dir = "data"

    for filename in os.listdir(data_dir):
        if not filename.endswith(".csv") or filename == "master_log.csv":
            continue

        filepath = os.path.join(data_dir, filename)
        try:
            df = pd.read_csv(filepath)
            if "Date" not in df.columns:
                continue
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

            for _, row in df.iterrows():
                date = row["Date"]

                # Group related fields
                grouped = defaultdict(dict)
                for col in df.columns:
                    if col == "Date":
                        continue
                    value = row[col]
                    if pd.isna(value):
                        continue

                    parts = col.split(" - ")
                    if len(parts) == 3:
                        category, sublabel, metric = parts
                        # normalize category
                        if len(category) >= 2 and category[-2] == " " and category[-1] in string.ascii_uppercase[:23]:
                            category = category[:-2]
                        grouped[(category, sublabel)][metric] = value
                    
                    elif len(parts) == 2:
                        category, metric = parts
                        sublabel = "General"
                        if len(category) >= 2 and category[-2] == " " and category[-1] in string.ascii_uppercase[:23]:
                            category = category[:-2]
                        grouped[(category, sublabel)][metric] = value
                    
                    else:
                        # Always store the value even if the column name doesn't match expected pattern
                        grouped[(filename.replace(".csv", ""), "General")][col] = value
                    
                #print("Grouped:", grouped) 
                # Flatten each group
                for (category, sublabel), metrics in grouped.items():
                    # Case 1: values are primitive (e.g., "Chicken Wrap")
                    id_key = next((k for k in ["title", "type", "name", "purpose", "song", "person", "topic", "game", "friends", "reflection"] if k in metrics), None)
                    identifier = metrics.get(id_key, sublabel) if id_key else sublabel

                    # Case 2: value itself is a dict string
                    for metric, value in metrics.items():
                        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                            try:
                                parsed = eval(value)
                                if isinstance(parsed, dict):
                                    id_key_inner = next((k for k in ["title", "type", "name"] if k in parsed), None)
                                    identifier_inner = parsed.get(id_key_inner, identifier) if id_key_inner else identifier
                                    for k, v in parsed.items():
                                        if k == id_key_inner:
                                            continue
                                        master_rows.append({
                                            "Date": date,
                                            "Category": category,
                                            "Subtype": identifier_inner,
                                            "Metric": k,
                                            "Value": v,
                                            "Source": filename
                                        })
                                    continue
                            except Exception:
                                pass

                        # Normal primitive case
                        if metric == id_key:
                            continue  # skip repeating identifier
                        master_rows.append({
                            "Date": date,
                            "Category": category,
                            "Subtype": identifier,
                            "Metric": metric,
                            "Value": value,
                            "Source": filename
                        })

        except Exception as e:
            print(f"Error consolidating {filename}: {e}")

    master_df = pd.DataFrame(master_rows)
    master_df.sort_values("Date", inplace=True)
    master_df.to_csv(os.path.join(data_dir, "master_log.csv"), index=False)
    print("Master log saved to data/master_log.csv")

def visualize_daily_activity(master_df, output_dir="data/plots"):
    os.makedirs(output_dir, exist_ok=True)

    # Group by day
    for date, group in master_df.groupby(master_df["Date"].dt.date):
        durations = (
            group[group["Metric"].str.lower() == "duration"]
            .assign(Value=pd.to_numeric(group[group["Metric"].str.lower() == "duration"]["Value"], errors="coerce"))
            .groupby(group["Source"].str.replace(".csv", "", regex=False))["Value"]
            .sum()
        )

        # Normalize to 1440 minutes
        total = durations.sum()
        print(total)
        if total > 0:
            durations = durations / total * 1440

        plt.figure(figsize=(8, 8))
        plt.pie(durations, labels=durations.index, autopct="%1.1f%%", startangle=90)
        plt.title(f"Daily Activity Breakdown ({date})")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"activity_pie_{date}.png"))
        plt.close()

def visualize_daily_meals(master_df, output_dir="data/plots"):
    os.makedirs(output_dir, exist_ok=True)

    for date, group in master_df.groupby(master_df["Date"].dt.date):
        meals = group[group["Category"].str.lower() == "meals"]

        if meals.empty:
            continue

        meal_data = {}
        for subtype, meal_group in meals.groupby("Subtype"):
            carbs = pd.to_numeric(meal_group.loc[meal_group["Metric"].str.lower() == "carbs", "Value"], errors="coerce").sum() * 4
            protein = pd.to_numeric(meal_group.loc[meal_group["Metric"].str.lower() == "proteins", "Value"], errors="coerce").sum() * 4
            fat = pd.to_numeric(meal_group.loc[meal_group["Metric"].str.lower() == "fats", "Value"], errors="coerce").sum() * 9
            meal_data[subtype] = {"Carbs": carbs, "Protein": protein, "Fat": fat}

        labels, values, colors = [], [], []
        base_colors = {"Carbs": "saddlebrown", "Protein": "red", "Fat": "gold"}

        # Generate shade variations per meal
        meal_list = list(meal_data.keys())
        shade_factors = np.linspace(0.6, 1.2, len(meal_list))  # noticeable range

        for i, (meal, macros) in enumerate(meal_data.items()):
            shade = shade_factors[i]
            for macro, val in macros.items():
                labels.append(f"{meal} - {macro}")
                values.append(val)

                # Apply shade variation
                base_rgb = np.array(mcolors.to_rgb(base_colors[macro]))
                shaded_rgb = np.clip(base_rgb * shade, 0, 1)
                colors.append(shaded_rgb)

        plt.figure(figsize=(8, 8))
        plt.pie(values, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        plt.title(f"Meal Breakdown ({date})")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"meals_pie_{date}.png"))
        plt.close()

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = CategorySelector(root)
    root.mainloop()
