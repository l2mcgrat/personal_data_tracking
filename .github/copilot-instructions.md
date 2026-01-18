# AI Coding Instructions — Personal Data Tracking

## Quick Summary
Personal data tracking app with Tkinter GUI for daily time logging across 17+ categories. Workflow: **GUI captures data → per-category CSVs → master consolidation → PDF reports**.

**Key entry points:**
- **Interactive**: `python main.py` — launches category picker, spawns input windows, auto-consolidates on close
- **Headless**: `from consolidate import consolidate_data; consolidate_data()` → generates master log; `from visualize import visualize_reports` → generates PDF reports

## Architecture & Critical Files

### Data Flow
1. **`main.py`** — `CategorySelector` class manages the UI selector (17 categories split into "BREAKDOWN" and "REBUILD" panes). Displays checkboxes, launches selected windows via `Toplevel()`, collects results, flattens nested dicts, writes per-category CSVs.
2. **`windows/{category}_window.py`** — 17 window classes (e.g., `WorkDayWindow`, `LearningWindow`). Each follows pattern: `__init__(master, callback)` → build Tkinter UI → `submit()` calls `callback(category_name, data_dict)`. Data dict **must include** `"Date"` key (ISO format: `YYYY-MM-DD`) and hierarchical structure (nested dicts allowed).
3. **`consolidate.py`** — `consolidate_data()` reads all CSVs from `data/window_data/`, flattens rows into normalized format, outputs `data/master_log.csv` (columns: `Date, Category, Subtype, Metric, Value, Source`).
4. **`visualize.py`** — `visualize_reports(master_df)` generates daily/weekly/monthly PDF reports under `reports/{daily,weekly,monthly}_reports/`. Includes media classification dictionary for content analysis.

### Data Storage
- **Per-category CSVs**: `data/window_data/{Category}.csv` (exact category name from `CategorySelector.category_windows` dict keys, e.g., `Work Day.csv`)
- **Master consolidation**: `data/master_log.csv` — read-only, generated from per-category CSVs
- **PDF outputs**: `reports/{daily,weekly,monthly}_reports/` — organized by report type and date

## Project-Specific Patterns & Conventions

### Window Data Structure
- Windows return nested dicts with **mandatory** `"Date"` key (ISO 8601: `YYYY-MM-DD`)
- Nested structure is flattened into column names using `Section - Subsection - Metric` format
- Example: `{"Date": "2026-01-14", "Block": {"Meetings": {"duration": 90, "notes": "grinding"}}}` → CSV columns: `Date`, `Block - Meetings - duration`, `Block - Meetings - notes`

### CSV Deduplication
- When `main.handle_data()` receives a window's data, it **replaces** any row with matching `Date` (upsert pattern)
- Fieldnames are merged with existing columns (preserves historical data structure)
- Writing logic in `main.py` lines 170–180: check for existing file, merge fieldnames, replace or append row

### Consolidation Heuristics
- **Category normalization**: strips trailing letter suffixes (e.g., `Work Day A` → `Work Day`) used internally for variants
- **Subtype identification**: searches for identifier keys in order: `title, type, name, purpose, song, person, topic, game, friends, reflection, subject`
- **Dict-in-dict parsing**: `consolidate.py` uses `eval()` on strings starting/ending with `{}`—intentional but risky (see "Safety Notes")

### Visualization Specifics
- Duration inference: explicit `duration` metrics, meals as virtual durations, workouts from `sets` metrics
- Weekly windows: start on Sunday (not Monday)
- Monthly windows: start on the 9th by default
- Media classification: hardcoded dictionary maps shorthand keys (e.g., `"CGP"`) to content names and categories

## Known Issues & Gotchas

### ⚠️ Work Day Filename Mismatch (Active Bug)
- **Symptom**: `main.py` writes `data/window_data/Work Day.csv` (with space), but `visualize.py` line 76 reads `Work_Day.csv` (with underscore)
- **Impact**: Work-specific visualizations fail silently; falls back to generic behavior
- **Fix required**: Either update `visualize.py` line 76 to use `Work Day.csv` OR rename the CSV file output in `main.py`

### `eval()` Security Risk in consolidate.py
- Line ~64 uses `eval()` to parse dict-like strings from CSV cells (flexible but dangerous)
- **Mitigation**: Consider replacing with `ast.literal_eval()` for safer parsing; verify input validation if user-facing

### Date Coercion Behavior
- `consolidate.py` uses `pd.to_datetime(..., errors='coerce')` → invalid dates silently become `NaT`
- Rows with `NaT` dates are dropped during consolidation (no warning)

## How to Add a New Category

1. **Create window class**: `windows/{snake_case}_window.py` with class `CamelCaseWindow` (see `LearningWindow` or `WorkDayWindow` as template)
   - Constructor: `__init__(self, master, callback)`
   - Build UI with consistent fonts and layout
   - `submit()` method calls `self.callback(category_display_name, data_dict)` where dict includes `"Date"`
2. **Register in main.py**: Import class, add entry to `CategorySelector.category_windows` dict (line 55–72). Key = display name (used as CSV filename), value = class
3. **Test end-to-end**:
   - Run `python main.py`, select new category, submit data
   - Verify `data/window_data/{DisplayName}.csv` exists with correct columns
   - Run `consolidate_data()`, check `data/master_log.csv` for new rows
   - If adding visualizations: extend `visualize.py` logic for new category specifics

## Running & Debugging

### Interactive Mode
```bash
python -m pip install pandas numpy matplotlib tkcalendar
python main.py
# Submit categories, inspect data/window_data/{Category}.csv
```

### Headless Consolidation & Reporting
```python
from consolidate import consolidate_data
from visualize import visualize_reports
import pandas as pd

consolidate_data()
df = pd.read_csv('data/master_log.csv')
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
visualize_reports(df)
```

### Debug Checklist
- Verify per-category CSVs created in `data/window_data/` after window submit
- Check `data/master_log.csv` columns: `Date, Category, Subtype, Metric, Value, Source`
- Missing report content? Inspect `Source` column (CSV filename) and category name case/whitespace
- Invalid dates? Look for `NaT` in master log and trace back to window date picker

## Safety & Maintenance

- **eval() risk**: Replace with `ast.literal_eval()` if user-submitted CSV strings are possible
- **Category renames**: Update both `main.py` `category_windows` dict AND `visualize.py` file path references
- **CSV filename stability**: Maintain consistency between `main.py` CSV output names and `visualize.py` read paths
- **No test suite**: Consider adding unit tests for CSV parsing, consolidation grouping logic, and date handling
