# AI Coding Instructions for Personal Data Tracking

## Project Overview
A Python-based time tracking application that captures daily activity data through 17 category-specific Tkinter GUIs (windows), stores data in CSV files, consolidates them into a master log, and generates visualization reports.

## Architecture & Data Flow

### Three-Phase Pipeline
1. **Data Capture** (`main.py`): Launches category-specific windows that collect user input
2. **Data Consolidation** (`consolidate.py`): Merges window-specific CSVs into `master_log.csv` with normalized structure
3. **Visualization** (`visualize.py`): Generates PDF reports from consolidated data

### Category Classification
- **Breakdown** (first 9 categories): Core tracked activities requiring detailed breakdown analysis
  - Work Day, Cooking, Workouts, Learning, Driving, Leetcode, Coding Projects, Career Prep, Miscellaneous
- **Rebuild** (last 8 categories): Behavioral/lifestyle tracking
  - Sleep, Meditating, Music, Gaming, Messaging/Calling, Socializing, Eating, Media

The categories are mapped in `main.py:category_windows` dict and split by index position into these groups.

### Data Flow
1. **Window** → captures data as nested dict (flattened in `handle_data()`)
2. **CSV Layer** → saves to `data/window_data/{category}.csv` with date-based deduplication
3. **Consolidation** → converts CSV rows to normalized master log format with columns: Date, Category, Subtype, Metric, Value, Source
4. **Master Log** → `data/master_log.csv` (normalized schema)
5. **Reports** → PDF reports in `reports/{daily,weekly,monthly}_reports/`

## Window Architecture Pattern

All window classes follow this structure:
```python
class {Category}Window:
    def __init__(self, master, callback):
        self.top = master
        self.callback = callback  # Called with (category_name, data_dict)
        # UI setup with Tkinter
        
    def submit(self):
        data = {
            "Date": selected_date.isoformat(),
            # Nested structure: "Section" → "Subsection" → {"metric": value}
            # OR flat: "Metric": value
        }
        self.callback(category_name, data)
        self.top.destroy()
```

Key conventions:
- Use `DateEntry` from `tkcalendar` for date selection
- Return data with ISO-formatted "Date" key
- Support nested dicts for structured data (flattened in `main.py`)
- Window title = category name (e.g., "Work Day Tracker")
- Center windows at screen midpoint with half-screen dimensions
- Use `self.callback(name, data)` to return data, then `self.top.destroy()`

## Consolidation Logic

### Column Naming Pattern
Input window data uses hierarchical keys: `"{Section} - {Subsection} - {Metric}"`

The consolidator:
- Strips trailing letter suffixes from categories (e.g., "Work Day A" → "Work Day")
- Extracts identifier fields (title, type, name, purpose, song, etc.) as `Subtype` column
- Flattens multi-level dicts recursively
- Parses dict-like string values as nested data
- Validates date format with `pd.to_datetime(..., errors="coerce")`

### CSV Handling
Each window has a CSV file in `data/window_data/{category}.csv`. When submitting:
1. Load existing rows if file exists
2. Merge fieldnames (preserve old columns, add new ones)
3. **Replace rows by matching Date** (if same date exists, update; else append)
4. Write back with all fieldnames to preserve schema history

## Key Implementation Details

### Data Deduplication (main.py)
When a window submits data for an existing date:
```python
# Step 5: Replace row if date matches, else append
for i, row in enumerate(rows):
    if row.get("Date") == selected_date:
        rows[i] = flat_data  # Replace entire row
```

### Identifier Extraction (consolidate.py)
The consolidator prioritizes these fields as subtypes:
```python
id_key = next((k for k in [
    "title", "type", "name", "purpose", "song", "person",
    "topic", "game", "friends", "reflection", "subject"
] if k in metrics), None)
```
Useful for grouping media by title, workouts by type, etc.

### Media Dictionary (visualize.py)
`media_dict` maps short codes (e.g., "BDE") to full titles and categories for media content classification. Extend this when adding new media tracking.

## Development Workflows

### Adding a New Category Window
1. Create `windows/{category_name}_window.py` inheriting the standard pattern
2. Add import in `main.py`
3. Add entry to `category_windows` dict in `main.py`
4. Window automatically receives data via callback chain
5. CSV created automatically on first submit

### Testing Data Flow
- Check `data/window_data/` for individual CSVs (raw submissions)
- Check `data/master_log.csv` for consolidated view (normalized schema)
- Reports in `reports/` show visualization output

### Common Debugging Patterns
- Print statements in window `submit()` show raw data before flattening
- Check `consolidate_data()` for normalization issues (field renaming, date parsing)
- Master log missing data? Verify window returned dict with "Date" key
- Schema mismatches? Check fieldnames list merging in Step 4 of `handle_data()`

## File Organization
- **Entry point**: `main.py` (CategorySelector class)
- **Window modules**: `windows/*.py` (one per category)
- **Pipeline scripts**: `consolidate.py`, `visualize.py` (called sequentially)
- **Data layer**: `data/window_data/*.csv` (inputs), `data/master_log.csv` (output)
- **Reports output**: `reports/{daily,weekly,monthly}_reports/*.pdf`

## Dependencies
- `tkinter` + `tkcalendar` (GUI)
- `pandas`, `numpy` (data processing)
- `matplotlib` + `PdfPages` (visualization)
- `csv` (manual I/O for deduplication logic)
