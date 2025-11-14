
import os, string
import pandas as pd
from collections import defaultdict

def consolidate_data():
    master_rows = []
    data_dir = "data/window_data"

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
                grouped = defaultdict(lambda: defaultdict(list))
                for col in df.columns:
                    if col == "Date":
                        continue
                    value = row[col]
                    if pd.isna(value):
                        continue

                    parts = col.split(" - ")
                    if len(parts) == 3:
                        category, sublabel, metric = parts
                        # normalize category (strip trailing " A", " B", etc.)
                        if len(category) >= 2 and category[-2] == " " and category[-1] in string.ascii_uppercase[:23]:
                            category = category[:-2]
                        grouped[(category, sublabel)][metric].append(value)

                    elif len(parts) == 2:
                        category, metric = parts
                        sublabel = "General"
                        if len(category) >= 2 and category[-2] == " " and category[-1] in string.ascii_uppercase[:23]:
                            category = category[:-2]
                        grouped[(category, sublabel)][metric].append(value)

                    else:
                        # Always store the value even if the column name doesn't match expected pattern
                        grouped[(filename.replace(".csv", ""), "General")][col].append(value)

                # Flatten each group
                for (category, sublabel), metrics in grouped.items():
                    # Try to find identifier key (title, song, person, etc.)
                    id_key = next((k for k in [
                        "title", "type", "name", "purpose", "song", "person",
                        "topic", "game", "friends", "reflection", "subject"
                    ] if k in metrics), None)

                    identifier = sublabel
                    if id_key:
                        # Use the first identifier value if available
                        identifier = metrics[id_key][0] if metrics[id_key] else sublabel

                    for metric, values in metrics.items():
                        # Skip repeating identifier metric itself
                        if metric == id_key:
                            continue

                        for value in values:
                            # Handle dict-like strings
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
    master_df.to_csv(os.path.join("data", "master_log.csv"), index=False)
    print("Master log saved to data/master_log.csv")

    