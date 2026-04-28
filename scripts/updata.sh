#!/bin/bash
# -------------------------------------------------------
# S C R I P T   U P D A T E   P O R T F O L I O   D A T A
#------------

# Define relative paths (Assuming execution from FMSLite root)
MASTER_FILE="./data/portfolio.json"
CACHE_DIR="./data/cache"
# TODAY=$(date +%Y-%m-%d)
CACHE_FILE="$CACHE_DIR/latest-update-portfolio.json"

# 1. Extract Top-Level Keys (Tickers) dynamically
if [ -f "$MASTER_FILE" ]; then
    # Extracts top-level keys: ROIV, SSRM, SPAX, etc.
    SYMBOLS=$(jq -r 'keys | join(" ")' "$MASTER_FILE")
else
    echo "[ERROR] Master file not found at $MASTER_FILE"
    exit 1
fi

# 2. Run Python Fetcher
python -c "
import yfinance as yf
import json
import os
from datetime import date

symbols = '$SYMBOLS'.split()
# Keys to fetch, including private valuation field
keep = ['regularMarketPrice', 'regularMarketChangePercent', 'marketCap', 'latestImpliedValuation', 'recommendationKey', 'recommendationMean']

os.makedirs('$CACHE_DIR', exist_ok=True)

try:
    tickers = yf.Tickers(' '.join(symbols))
    full_data = {}
    print(f'\n--- PORTFOLIO DAILY DELTA ($TODAY) ---')
    
    for s in symbols:
        try:
            info = tickers.tickers[s].info
            # Create sub-dictionary for this ticker
            full_data[s] = {k: info.get(k) for k in keep}
            
            price = info.get('regularMarketPrice') or 0.0
            change = info.get('regularMarketChangePercent') or 0.0
            print(f'{s:<10} | Price: {price:>8.2f} | Change: {change:>+7.2f}%')
        except Exception:
            print(f'{s:<10} | [SKIP] Ticker not found or fetch error')

    with open('$CACHE_FILE', 'w') as f:
        json.dump(full_data, f, indent=4)
    print(f'\n[SUCCESS] Daily cache saved: $CACHE_FILE')
except Exception as e:
    print(f'\n[ERROR] Fetch process failed: {e}')
    exit(1)
"
