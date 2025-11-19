
import warnings
warnings.filterwarnings("ignore")

import os
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

# --- Media Dictionary ---
media_dict = {
    "BDE": ["Baseball Doesn't Exist","Sports"],
    "Big A": ["Atrioc", "Current Events"],
    "LASSI": ["LASSI", "Sports"],
    "Gachiakuta": ["Classic Shonen", "Anime"],
    "One Punch Man": ["Seinen", "Anime"],
    "Kuroko": ["Sports Shonen", "Anime"],
    "IO":["Idoled Out", "Reality TV"],
    "Shorts":["Shorts", "Shorts"],
    "Music": ["Music","Music"],
    "AIM": ["Anime in Minutes", "Anime"],
    "TDS": ["The Daily Show","Current Events"],
    "Veritasium": ["Veritasium", "Science"],
    "JHR": ["Jimmy High Roller", "Sports"],
    "Nintendo": ["Nintendo", "Gaming"],
    "NBA": ["Basketball", "Sports"],
    "Ethanimale": ["Big Brother", "Reality TV"],
    "Other": ["Other","Other"],
    "HHM": ["Hip Hop Madness", "Music"],
    "Xevi": ["Xevi", "Current Events"],
    "RWJ": ["Ray William Johnson", "Life"],
    "VGD": ["Video Game Dunkey", "Gaming"],
    "SJJ": ["Solid JJ", "Comedy"],
    "Gigguk": ["Gigguk", "Anime"],
    "JA": ["Jaden Animations", "Life"],
    "Tier Zoo": ["Tier Zoo", "Science"],
    "RTwBM": ["Bill Maher", "Current Events"],
    "Shawn Cee": ["Shawn Cee", "Music"],
    "EE": ["Economics Explained", "Science"],
    "Hank Green": ["Hank Green", "Current Events"],
    "Branch Education": ["Branch Education", "Science"],
    "Alenxander Bromley": ["Alexander Bromley", "Science"],
    "CGP": ["CGP Grey", "Science"],
    "poi": ["poi", "Science"]
}

def classify_media(title, media_dict):
    for key, (name, category) in media_dict.items():
        if key.lower() in str(title).lower():
            return name, category
    return None, None

def plot_media_pie(data_dict, title, pdf):
    if not data_dict:
        return
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        data_dict.values(),
        labels=data_dict.keys(),
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 8}
    )
    ax.set_title(title)
    pdf.savefig(fig)
    plt.close(fig)

def visualize_reports(master_df):
    
    output_dir="reports/daily_reports"
    os.makedirs(output_dir, exist_ok=True)

    all_daily_durations = {}

    # --- Daily Reports ---

    for date, group in master_df.groupby(master_df["Date"].dt.date):
        pdf_path = os.path.join(output_dir, f"daily_report_{date}.pdf")
        with PdfPages(pdf_path) as pdf:

            # --- Daily Activity Pie Chart ---
            durations = {}
            
            # Existing explicit durations
            activity = group[group["Metric"].str.lower() == "duration"].copy()
            activity["Value"] = pd.to_numeric(activity["Value"], errors="coerce")
            for src, val in activity.groupby("Source")["Value"].sum().items():
                durations[src.replace(".csv", "")] = val
            
            # Meals & Snacks (virtual durations → grouped as "Eating")
            meal_count = len(group[group["Category"].str.lower() == "meals"]["Subtype"].unique())
            snack_count = len(group[group["Category"].str.lower() == "snacks"]["Subtype"].unique())
            eating_duration = meal_count * 20 + snack_count * 10
            if eating_duration > 0:
                durations["Eating"] = durations.get("Eating", 0) + eating_duration
            
            # Workouts (muscle groups with sets metric × 3 minutes)
            workout_categories = ["chest", "back", "shoulders", "legs", "triceps", "biceps", "abs"]
            for subtype, workout_group in group[group["Category"].str.lower().isin(workout_categories)].groupby("Subtype"):
                sets = pd.to_numeric(
                    workout_group.loc[workout_group["Metric"].str.lower() == "sets", "Value"],
                    errors="coerce"
                ).sum()
                workout_duration = float(sets * 2.5)
                if workout_duration > 0:
                    durations["Workouts"] = durations.get("Workouts", 0) + workout_duration
            
            # Miscellaneous (showers and teeth brushing)
            misc_group = group[group["Category"].str.lower() == "fixed"]
            if not misc_group.empty:
                showers = pd.to_numeric(
                    misc_group.loc[misc_group["Metric"].str.lower() == "showers", "Value"],
                    errors="coerce"
                ).sum()
                teeth = pd.to_numeric(
                    misc_group.loc[misc_group["Metric"].str.lower().isin(["teeth", "teeth brushed"]), "Value"],
                    errors="coerce"
                ).sum()
            
                misc_duration = showers * 15 + teeth * 3
                if misc_duration > 0:
                    durations["Miscellaneous"] = durations.get("Miscellaneous", 0) + misc_duration
            
            # Missing category (whatever is left out of 1440 minutes)
            accounted_total = sum(durations.values())
            missing_duration = max(0, 1440 - accounted_total)
            if missing_duration > 0:
                durations["Missing"] = missing_duration
            
            # Normalize to 1440 minutes
            total = sum(durations.values())
            if total > 0:
                durations = {k: v / total * 1440 for k, v in durations.items()}
            
            all_daily_durations[str(date)] = durations
            
            fig1, ax1 = plt.subplots(figsize=(12, 12))
            ax1.pie(durations.values(), labels=durations.keys(), autopct="%1.1f%%", startangle=90, textprops={"fontsize": 8})
            ax1.set_title(f"Daily Activity Breakdown ({date})")
            pdf.savefig(fig1)
            plt.close(fig1)

            # --- Daily Media Pie Chart ---
            media_counts = {}
            for src, val in activity.groupby("Source")["Value"].sum().items():
                name, category = classify_media(src, media_dict)
                if category:
                    media_counts[category] = media_counts.get(category, 0) + val
            plot_media_pie(media_counts, f"Daily Media Breakdown ({date})", pdf)

            # --- Meals Pie Charts and Tables ---
            meals = group[group["Category"].str.lower().isin(["meals", "snacks"])]
            if not meals.empty:
                meal_data = {}
                for subtype, meal_group in meals.groupby("Subtype"):
                    carbs = pd.to_numeric(meal_group.loc[meal_group["Metric"].str.lower() == "carbs", "Value"], errors="coerce").sum() * 4
                    protein = pd.to_numeric(meal_group.loc[meal_group["Metric"].str.lower() == "proteins", "Value"], errors="coerce").sum() * 4
                    fat = pd.to_numeric(meal_group.loc[meal_group["Metric"].str.lower() == "fats", "Value"], errors="coerce").sum() * 9
                    meal_data[subtype] = {"Carbs": carbs, "Protein": protein, "Fat": fat}
            
                # Flatten into (meal, macro, value)
                flat_data = [(meal, macro, val) for meal, macros in meal_data.items() for macro, val in macros.items()]
            
                # Sort by macro type: Carbs → Protein → Fat
                macro_order = {"Carbs": 0, "Protein": 1, "Fat": 2}
                flat_data.sort(key=lambda x: macro_order[x[1]])
            
                labels, values, colors = [], [], []
                base_colors = {"Carbs": "orange", "Protein": "red", "Fat": "gold"}
                shade_factors = np.linspace(0.6, 1.2, len(meal_data))
            
                def wrap_label_at_space(label, max_width=20):
                    words = label.split(" ")
                    lines, current_line = [], ""
                    for word in words:
                        if len(current_line) + len(word) + 1 <= max_width:
                            current_line += (" " if current_line else "") + word
                        else:
                            lines.append(current_line)
                            current_line = word
                    if current_line:
                        lines.append(current_line)
                    return "\n".join(lines)
            
                for meal, macro, val in flat_data:
                    # Bold macro name
                    bold_macro = r"$\mathbf{" + macro + "}$"
                    label = wrap_label_at_space(f"{meal} - {bold_macro}", 15)
                    labels.append(label)
                    values.append(val)
            
                    # Shade colors by meal index
                    meal_idx = list(meal_data.keys()).index(meal)
                    shade = shade_factors[meal_idx]
                    base_rgb = np.array(mcolors.to_rgb(base_colors[macro]))
                    shaded_rgb = np.clip(base_rgb * shade, 0, 1)
                    colors.append(shaded_rgb)
            
                fig2, ax2 = plt.subplots(figsize=(12, 12))
                ax2.pie(
                    values,
                    labels=labels,
                    colors=colors,
                    autopct="%1.1f%%",
                    startangle=90,
                    textprops={"fontsize": 8}
                )
                ax2.set_title(f"Meal Breakdown ({date})")
                pdf.savefig(fig2)
                plt.close(fig2)
                
                # --- Table of Macronutrients ---
                fig3, ax3 = plt.subplots(figsize=(10, 6))
                ax3.axis("off")
                
                # Define the wrapping function once
                def wrap_label_at_space(label, max_width=20):
                    words = label.split(" ")
                    lines, current_line = [], ""
                    for word in words:
                        if len(current_line) + len(word) + 1 <= max_width:
                            current_line += (" " if current_line else "") + word
                        else:
                            lines.append(current_line)
                            current_line = word
                    if current_line:
                        lines.append(current_line)
                    return "\n".join(lines)
                
                table_data = []
                cumulative_carbs = cumulative_protein = cumulative_fat = cumulative_total = 0
                
                for meal, macros in meal_data.items():
                    total_cal = macros["Carbs"] + macros["Protein"] + macros["Fat"]
                    cumulative_carbs += macros["Carbs"]
                    cumulative_protein += macros["Protein"]
                    cumulative_fat += macros["Fat"]
                    cumulative_total += total_cal
                
                    # Wrap long meal names at spaces instead of fixed character chunks
                    wrapped_meal = wrap_label_at_space(meal, max_width=20)
                
                    table_data.append([
                        wrapped_meal,
                        f"{macros['Carbs']:.0f}",
                        f"{macros['Protein']:.0f}",
                        f"{macros['Fat']:.0f}",
                        f"{total_cal:.0f}"
                    ])
                
                # Add cumulative totals row
                table_data.append([
                    "TOTAL",
                    f"{cumulative_carbs:.0f}",
                    f"{cumulative_protein:.0f}",
                    f"{cumulative_fat:.0f}",
                    f"{cumulative_total:.0f}"
                ])
                
                col_labels = ["Meal/Snack", "Carbs (cal)", "Protein (cal)", "Fat (cal)", "Total (cal)"]
                
                table = ax3.table(cellText=table_data, colLabels=col_labels, loc="center")
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1.2, 1.2)
                
                # Adjust row heights consistently across all columns
                for row_idx in range(len(table_data)):
                    meal_text = table.get_celld()[(row_idx+1, 0)].get_text().get_text()  # +1 because row 0 is header
                    num_lines = meal_text.count("\n") + 1
                    row_height = 0.08 * num_lines
                
                    for col_idx in range(len(col_labels)):
                        cell = table.get_celld()[(row_idx+1, col_idx)]
                        cell.set_height(row_height)
                
                # Optionally adjust header row height too
                for col_idx in range(len(col_labels)):
                    table.get_celld()[(0, col_idx)].set_height(0.1)
                
                ax3.set_title(f"Meal & Snack Macro Table ({date})", pad=20)
                plt.tight_layout()
                pdf.savefig(fig3)
                plt.close(fig3) 
              
    # --- Weekly Reports ---
    weekly_folder = "reports/weekly_reports"
    os.makedirs(weekly_folder, exist_ok=True)
    
    def get_week_start(date_obj):
        # Ensure week starts on Sunday
        return date_obj - timedelta(days=(date_obj.weekday() + 1) % 7)
    
    grouped_weeks = {}
    for date_str, day_durations in all_daily_durations.items():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        week_start = get_week_start(date_obj)
        week_key = week_start.strftime("%Y-%m-%d")
        grouped_weeks.setdefault(week_key, {})[date_obj] = day_durations
    
    for week_start, week_days in grouped_weeks.items():
        # Aggregate totals
        weekly_totals = {}
        for day, durations in week_days.items():
            for cat, mins in durations.items():
                weekly_totals[cat] = weekly_totals.get(cat, 0) + mins
    
        # Rank categories by total minutes
        ranked = sorted(weekly_totals.items(), key=lambda x: x[1], reverse=True)
        top3 = [c for c, _ in ranked[:4]]
        mid = [c for c, _ in ranked[4:8]]
        rest = [c for c, _ in ranked[8:]]
    
        def plot_group(categories, ax, title, day_map, monthly=False):
            """Plot line chart for given categories across days in day_map."""
            days = sorted(day_map.keys())
            for cat in categories:
                y = [day_map.get(day, {}).get(cat, 0) for day in days]
                ax.plot(days, y, marker="o", label=cat)
            ax.set_title(title)
            ax.set_ylabel("Minutes")
    
            # Only add legend if something was plotted
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend()
    
            # Show fewer ticks if many days
            step = max(1, len(days)//10)
            ax.set_xticks(days[::step])
    
            if monthly:
                ax.set_xticklabels([d.strftime("%b %d") for d in days[::step]], rotation=45)
            else:
                ax.set_xticklabels([d.strftime("%a") for d in days[::step]], rotation=45)
    
        # Line charts
        fig, axes = plt.subplots(3, 1, figsize=(12, 18))
        plot_group(top3, axes[0], "Top 3 Categories", week_days, monthly=False)
        plot_group(mid, axes[1], "Ranked 4–8 Categories", week_days, monthly=False)
        plot_group(rest, axes[2], "Remaining Categories", week_days, monthly=False)
        plt.tight_layout()
    
        pdf_path = os.path.join(weekly_folder, f"weekly_report_{week_start}.pdf")
        with PdfPages(pdf_path) as pdf:
            pdf.savefig(fig)
            plt.close(fig)
    
            # --- Weekly Pie Chart ---
            fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
            ax_pie.pie(
                weekly_totals.values(),
                labels=weekly_totals.keys(),
                autopct="%1.1f%%",
                startangle=90,
                textprops={"fontsize": 8}
            )
            ax_pie.set_title(f"Weekly Activity Breakdown (Week of {week_start})")
            pdf.savefig(fig_pie)
            plt.close(fig_pie)
            
            # --- Weekly Media Pie Chart ---
            weekly_media_counts = {}
            for src, mins in weekly_totals.items():
                name, category = classify_media(src, media_dict)
                if category:
                    weekly_media_counts[category] = weekly_media_counts.get(category, 0) + mins
            plot_media_pie(weekly_media_counts, f"Weekly Media Breakdown (Week of {week_start})", pdf)
    
    # --- Monthly Reports ---
    monthly_dir = "reports/monthly_reports"
    os.makedirs(monthly_dir, exist_ok=True)
    
    def get_month_start(date, start_day=9):
        if not (1 <= start_day <= 28):
            raise ValueError("start_day must be between 1 and 28")
    
        # If the day of the month is >= start_day, month start is this month's start_day
        if date.day >= start_day:
            return date.replace(day=start_day)
        else:
            # Otherwise, month start is the previous month's start_day
            prev_month = date.month - 1 or 12
            prev_year = date.year if date.month > 1 else date.year - 1
            return date.replace(year=prev_year, month=prev_month, day=start_day)
    
    grouped_months = {}
    for date_str, day_durations in all_daily_durations.items():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        month_start = get_month_start(date_obj)
        month_key = month_start.strftime("%Y-%m-%d")
        grouped_months.setdefault(month_key, {})[date_obj] = day_durations
    
    for month_start, month_days in grouped_months.items():
        monthly_totals = {}
        for day, durations in month_days.items():
            for cat, mins in durations.items():
                monthly_totals[cat] = monthly_totals.get(cat, 0) + mins
    
        ranked = sorted(monthly_totals.items(), key=lambda x: x[1], reverse=True)
        top3 = [c for c, _ in ranked[:4]]
        mid = [c for c, _ in ranked[4:8]]
        rest = [c for c, _ in ranked[8:]]
    
        # Line charts
        fig, axes = plt.subplots(3, 1, figsize=(12, 18))
        plot_group(top3, axes[0], "Top 3 Categories", month_days, monthly=True)
        plot_group(mid, axes[1], "Ranked 4–8 Categories", month_days, monthly=True)
        plot_group(rest, axes[2], "Remaining Categories", month_days, monthly=True)
        plt.tight_layout()
    
        pdf_path = os.path.join(monthly_dir, f"monthly_report_{month_start}.pdf")
        with PdfPages(pdf_path) as pdf:
            pdf.savefig(fig)
            plt.close(fig)
    
            # Pie chart
            fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
            ax_pie.pie(
                monthly_totals.values(),
                labels=monthly_totals.keys(),
                autopct="%1.1f%%",
                startangle=90,
                textprops={"fontsize": 8}
            )
            ax_pie.set_title(f"Monthly Activity Breakdown (Starting {month_start})")
            pdf.savefig(fig_pie)
            plt.close(fig_pie)
            
            # --- Monthly Media Pie Chart ---
            monthly_media_counts = {}
            for src, mins in monthly_totals.items():
                name, category = classify_media(src, media_dict)
                if category:
                    monthly_media_counts[category] = monthly_media_counts.get(category, 0) + mins
            plot_media_pie(monthly_media_counts, f"Monthly Media Breakdown (Starting {month_start})", pdf)


