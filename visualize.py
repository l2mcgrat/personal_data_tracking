
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

def visualize_daily_reports(master_df, output_dir="data/reports"):
    os.makedirs(output_dir, exist_ok=True)

    for date, group in master_df.groupby(master_df["Date"].dt.date):
        pdf_path = os.path.join(output_dir, f"daily_report_{date}.pdf")
        with PdfPages(pdf_path) as pdf:

            # --- Activity Pie Chart ---
            durations = group[group["Metric"].str.lower() == "duration"].copy()
            durations["Value"] = pd.to_numeric(durations["Value"], errors="coerce")
            durations = durations.groupby(durations["Source"].str.replace(".csv", "", regex=False))["Value"].sum()

            total = durations.sum()
            if total > 0:
                durations = durations / total * 1440

            fig1, ax1 = plt.subplots(figsize=(8, 8))
            ax1.pie(durations, labels=durations.index, autopct="%1.1f%%", startangle=90)
            ax1.set_title(f"Daily Activity Breakdown ({date})")
            pdf.savefig(fig1)
            plt.close(fig1)

            # --- Meals Pie Chart ---
            meals = group[group["Category"].str.lower().isin(["meals", "snacks"])]
            if not meals.empty:
                meal_data = {}
                for subtype, meal_group in meals.groupby("Subtype"):
                    carbs = pd.to_numeric(meal_group.loc[meal_group["Metric"].str.lower() == "carbs", "Value"], errors="coerce").sum() * 4
                    protein = pd.to_numeric(meal_group.loc[meal_group["Metric"].str.lower() == "proteins", "Value"], errors="coerce").sum() * 4
                    fat = pd.to_numeric(meal_group.loc[meal_group["Metric"].str.lower() == "fats", "Value"], errors="coerce").sum() * 9
                    meal_data[subtype] = {"Carbs": carbs, "Protein": protein, "Fat": fat}

                labels, values, colors = [], [], []
                base_colors = {"Carbs": "orange", "Protein": "red", "Fat": "gold"}
                shade_factors = np.linspace(0.6, 1.2, len(meal_data))

                for i, (meal, macros) in enumerate(meal_data.items()):
                    shade = shade_factors[i]
                    for macro, val in macros.items():
                        labels.append(f"{meal} - {macro}")
                        values.append(val)
                        base_rgb = np.array(mcolors.to_rgb(base_colors[macro]))
                        shaded_rgb = np.clip(base_rgb * shade, 0, 1)
                        colors.append(shaded_rgb)

                fig2, ax2 = plt.subplots(figsize=(6, 6))
                ax2.pie(values, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
                ax2.set_title(f"Meal Breakdown ({date})")
                pdf.savefig(fig2)
                plt.close(fig2)
                
                # --- Table of macros ---
                fig3, ax3 = plt.subplots(figsize=(10, 6))
                ax3.axis("off")
                
                table_data = []
                cumulative_carbs = cumulative_protein = cumulative_fat = cumulative_total = 0
                
                for meal, macros in meal_data.items():
                    total_cal = macros["Carbs"] + macros["Protein"] + macros["Fat"]
                    cumulative_carbs += macros["Carbs"]
                    cumulative_protein += macros["Protein"]
                    cumulative_fat += macros["Fat"]
                    cumulative_total += total_cal
                
                    # Wrap long meal names by inserting line breaks every ~20 characters
                    wrapped_meal = "\n".join([meal[i:i+20] for i in range(0, len(meal), 20)])
                
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
                    # Get the meal/snack cell text for this row
                    meal_text = table.get_celld()[(row_idx+1, 0)].get_text().get_text()  # +1 because row 0 is header
                    num_lines = meal_text.count("\n") + 1
                    row_height = 0.08 * num_lines
                
                    # Apply the same height to all cells in this row (including header row separately)
                    for col_idx in range(len(col_labels)):
                        cell = table.get_celld()[(row_idx+1, col_idx)]
                        cell.set_height(row_height)
                
                # Optionally adjust header row height too
                for col_idx in range(len(col_labels)):
                    table.get_celld()[(0, col_idx)].set_height(0.1)
                
                ax3.set_title(f"Meal & Snack Macro Table ({date})", pad=20)  # push title down
                plt.tight_layout()
                pdf.savefig(fig3)
                plt.close(fig3)
                