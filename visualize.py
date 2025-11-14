
import os
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

def visualize_daily_reports(master_df):
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
              
    print(all_daily_durations)  
              
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
        mid = [c for c, _ in ranked[4:9]]
        rest = [c for c, _ in ranked[9:]]
    
    def plot_group(categories, ax, title, week_days):
        days = sorted(week_days.keys())
        for cat in categories:
            y = [week_days.get(day, {}).get(cat, 0) for day in days]
            ax.plot(days, y, marker="o", label=cat)
        ax.set_title(title)
        ax.set_ylabel("Minutes")
        ax.legend()
        ax.set_xticks(days)
        ax.set_xticklabels([d.strftime("%a") for d in days])
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 18))
    plot_group(top3, axes[0], "Top 3 Categories", week_days)
    plot_group(mid, axes[1], "Ranked 4–8 Categories", week_days)
    plot_group(rest, axes[2], "Remaining Categories", week_days)
    
    plt.tight_layout()
    pdf_path = os.path.join("reports/weekly_reports", f"weekly_report_{week_start}.pdf")
    plt.savefig(pdf_path)
    plt.close()
