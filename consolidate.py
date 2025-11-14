
import os, string
import pandas as pd
from collections import defaultdict

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
                    id_key = next((k for k in ["title", "type", "name", "purpose", "song", "person", "topic", "game", "friends", "reflection", "subject"] if k in metrics), None)
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
    