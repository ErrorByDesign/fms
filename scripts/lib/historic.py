# scripts/lib/historic.py
# --- --- --- --- --- --- --- --- --- --- --- --
# -<< H I S T O R I C >>- --- --- --- --- --- ---
# --- --- --- --- --

# -<< IMPORTS
import json
import numpy as np
import pandas as pd
import sys
import yfinance as yf
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# -<< IMPORTS: LOCAL
import scripts.config.colors as color

# -<< IMPORTS: RICH
from rich.console import Console
console = Console()

# =<< PATHS
DIR_ARCHIVE   = "./data/archive"
PATH_HISTORIC = "./data/historic.json"
PATH_MAPPING  = "./config/CIA/mappings-history-ticker.json"
PATH_TEMPLATE = "./config/CIA/template-history-ticker.json"

# =<< GLOBALS
WINDOWS = {
    "M1": 21,      # ~1 month
    "M3": 63,      # ~3 months
    "M6": 126,     # ~6 months
    "Y1": 252,     # ~1 year
    "Y2": 504,     # ~2 years
    "Y3": 756      # ~3 years
}
EMPTY_HISTORY = {
    "M1": {"priceLow": None, "dateLow": None},
    "M3": {"priceLow": None, "dateLow": None},
    "M6": {"priceLow": None, "dateLow": None},
    "Y1": {"priceLow": None, "dateLow": None},
    "Y2": {"priceLow": None, "dateLow": None},
    "Y3": {"priceLow": None, "dateLow": None}
}



# === === === === === === === === R E F A C T O R
""" REFACTOR IN PROGRESS (Incomplete) :
PRIORITY: Low
OBJECTIVE: Modify the code in this script so that
the 2 functions load_mapping() and load_template()
use the util.load_json() function instead.
"""

# -<< LOAD MAPPING
# --- --- --- --- --- --- --- ---
def load_mapping():
    """Load the column mapping from yFinance to output fields."""
    if not PATH_MAPPING.exists():
        # Fallback to default mapping
        return {"close": "Close", "high": "High", "low": "Low", "open": "Open", "volume": "Volume"}
    with open(PATH_MAPPING, 'r') as f:
        data = json.load(f)
    # Expecting structure: { "TICKER_SYMBOL": { "YYYY-MM-ddT04:00:00.000Z": { ... } } }
    # Actually, we just need the mapping from FMS keys to source columns.
    # The template shows that the mapping is at the leaf level.
    # We can simply use the first entry's mapping.
    ticker_map = data.get("TICKER_SYMBOL", {})
    if ticker_map:
        # Get the first date pattern (any key) to retrieve the mapping
        first_key = next(iter(ticker_map))
        return ticker_map[first_key]
    else:
        return {"close": "Close", "high": "High", "low": "Low", "open": "Open", "volume": "Volume"}

# -<< LOAD TEMPLATE
# --- --- --- --- --- --- --- ---
def load_template():
    """Load the template (for potential validation)."""
    if not PATH_TEMPLATE.exists():
        return None
    with open(PATH_TEMPLATE, 'r') as f:
        return json.load(f)

# END OF REFACTOR ZONE
# === === === === === === === === R E F A C T O R



# -<< FETCH HISTORIC LOWS
# --- --- --- --- --- --- --- ---
def fetch_historic_lows(ticker, period="max", clip_start=None):
    """ H I S T O R I C   L O W S :
    Fetch historic data and return (lows_dict, DataFrame).
    - lows_dict is ready to merge into portfolio[ticker]["HISTORY"].
    - On failure, returns (EMPTY_HISTORY, None).
    - If clip_start (YYYY-MM-DD) is given, only data >= that date is kept.
    """
    try:
        t = yf.Ticker(ticker)
        h = t.history(period=period, interval="1d")
        if h.empty:
            return EMPTY_HISTORY, None

        # Optional clipping to a common start date
        if clip_start is not None:
            if h.index.tz is not None:
                h.index = h.index.tz_localize(None)
            clip_ts = pd.Timestamp(clip_start)
            h = h[h.index >= clip_ts]
            if h.empty:
                return EMPTY_HISTORY, None

        close = h['Close']
        result = {}

        for label, days in WINDOWS.items():
            window = close.tail(min(days, len(close)))

            if len(window) == 0:
                result[label] = {"priceLow": None, "dateLow": None}
                continue

            low_price = round(window.min(), 2)
            low_date  = window.idxmin()

            # Convert to UTC epoch seconds
            if low_date.tz is not None:
                low_date_utc = low_date.tz_convert("UTC")
            else:
                low_date_utc = low_date.tz_localize("UTC")

            epoch_sec = int(low_date_utc.timestamp())
            result[label] = {
                "dateLow": epoch_sec,
                "priceLow": low_price
            }

        return result, h

    except Exception as e:
        console.print_exception()
        return EMPTY_HISTORY, None

# -<< SAVE PER TICKER HISTORY
# --- --- --- --- --- --- --- ---
def save_history(h, ticker, path=None):
    # mapping is a dict: { "close": "Close", "high": "High", "low": "Low", ... }
    # We need to build a dict where keys are the date strings (e.g., "2023-06-06T04:00:00.000Z")
    # and values are dicts with the mapped fields.
    if path is None:
        path = DIR_ARCHIVE / f"{ticker}-history.json"

    mapping = load_mapping()
    output  = {}

    for idx in h.index:
        # Convert index to the ISO string format used in the template
        # yFinance index is already timezone-aware; we want to keep the same format
        # e.g., "2023-06-06T04:00:00.000Z"
        date_key = idx.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        entry    = {}

        for fms_key, src_col in mapping.items():
            if src_col in h.columns:
                entry[fms_key] = float(round(h.loc[idx, src_col], 2))
        output[date_key] = entry

    with open(path, 'w') as f:
        json.dump(output, f, indent=4)

    print(f"✔ [{color.info}][{color.ACTV}]{ticker}[/] historic data fetched[/]")

# -<< SAVE MASTER HISTORIC FILE
# --- --- --- --- --- --- --- ---
def save_historic(tickers, input_dir=DIR_ARCHIVE, output_path=PATH_HISTORIC):
    input_dir   = Path(input_dir)
    output_path = Path(output_path)
    combined    = {}

    for ticker in tickers:
        file_path = input_dir / f"{ticker}-history.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                combined[ticker] = json.load(f)

    with open(output_path, 'w') as f:
        json.dump(combined, f, indent=4)

    print(f"\n[{color.DONE}]Combined history saved to [{color.DOS}]{output_path}[/].[/]")