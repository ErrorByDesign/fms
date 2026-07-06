#!/usr/bin/env python3
# === === === === === === === === === === === === ===
# F M S   T E R M I N A L   -   I N C U B A T O R
# === === === === ===

# -<< IMPORTS
import copy
import json
import os
import re
import subprocess
import sys
import time
import yfinance as yf
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# -<< IMPORTS: LOCAL
import scripts.config.breadcrumbs as crumb
import scripts.config.colors as color
import scripts.config.globals as glob
import scripts.config.ui as ui
import scripts.config.utils as util
import scripts.lib.dashboard as dash
import scripts.lib.historic as hist

# -<< IMPORTS: RICH
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Confirm
from rich.table import Table
console = Console()

# =<< PATHS
DIR_ARCHIVE    = "./data/archive"
DIR_CACHE      = "./data/cache"
PATH_HISTORIC  = "./data/historic.json"
PATH_MAPPINGS  = "./config/CIA/mappings-portfolio.json"
PATH_MERGER    = "./scripts/lib/merger.py"
PATH_NEWBORN   = "./data/cache/latest-newborn.json"
PATH_PORTFOLIO = "./data/portfolio.json"
PATH_REBORN    = "./data/cache/latest-reborn.json"
PATH_REFRESH   = "./data/cache/latest-refresh.json"
PATH_TEMPLATE  = "./config/CIA/template-portfolio.json"
PATH_WHITELIST = "./config/CIA/whitelist-toolbox.json"



# -<< SET NESTED VALUE
# --- --- --- --- --- --- --- ---
def set_nested_value(target_dict, path, value):
    keys    = path.split('.')
    current = target_dict
    for key in keys[:-1]:
        if isinstance(current, list): return
        current = current.setdefault(key, {})
    if isinstance(current, dict):
        current[keys[-1]] = value

# -<< GET NESTED VALUE
# --- --- --- --- --- --- --- ---
def get_nested_value(target_dict, path):
    keys = path.split('.')
    val  = target_dict
    for k in keys:
        if isinstance(val, dict): val = val.get(k)
        else: return None
    return val

# -<< HISTORIC DATA
# --- --- --- --- --- --- --- ---
def archive_history(ticker, clip_start="2023-01-06"):
    """Fetch and archive historic data for a ticker. Returns lows dict."""
    history_data, h = hist.fetch_historic_lows(ticker, period="max", clip_start=clip_start)
    if h is not None:
        hist.save_history(h, ticker)
    return history_data

# -<< PSEUDO PROCESSING
# --- --- --- --- --- --- --- ---
def pseudo_processing(toolbox, ticker):
    """:
    Compute all pseudo keys and store them in toolbox.
    These are then used by recursive_fetch via the mapping.
    """
    # ---- Description ----
    raw_desc = toolbox.get("longBusinessSummary") or ""
    toolbox["pseudoDescription"] = util.newline(raw_desc)

    # ---- Year ----
    year_val = toolbox.get("dateFounded")
    if not year_val:
        m = re.search(r'founded in (\d{4})|incorporated in (\d{4})', raw_desc, re.I)
        if m:
            year_val = m.group(1) or m.group(2)
    toolbox["pseudoYear"] = str(year_val)[:4] if year_val else ""

    # ---- History lows ----
    history_data = archive_history(ticker)
    for period in ["M1", "M3", "M6", "Y1", "Y2", "Y3"]:
        entry = history_data.get(period, {})
        toolbox[f"pseudoDate{period}"]  = entry.get("dateLow")
        toolbox[f"pseudoPrice{period}"] = entry.get("priceLow")

# -<< RECURSIVE FETCH
# --- --- --- --- --- --- --- ---
def recursive_fetch(data, toolbox, current_path=""):
    """Recursively traverse the template, resolve dot-paths in toolbox."""
    if isinstance(data, dict):
        for key, value in data.items():
            path = f"{current_path}.{key}" if current_path else key
            if isinstance(value, dict):
                recursive_fetch(value, toolbox, path)
            elif isinstance(value, list):
                list_path = f"{path}.[]" if not path.endswith(".[]") else path
                for item in value:
                    if isinstance(item, dict):
                        recursive_fetch(item, toolbox, list_path)
            elif isinstance(value, str) and value in toolbox:
                data[key] = toolbox[value]
            elif isinstance(value, str) and '.' in value:
                resolved = get_nested_value(toolbox, value)
                if resolved is not None:
                    data[key] = resolved

# -<< FETCH DNA SEQUENCE
# --- --- --- --- --- --- --- ---
def fetch_dna_sequence(ticker, stock_type, mapping_conf):
    """Build a portfolio entry from yFinance using the mapping structure."""
    template     = util.load_json(PATH_TEMPLATE)["TICKER_SYMBOL"]
    whitelist    = util.load_json(PATH_WHITELIST)
    yfinance_map = mapping_conf.get(stock_type, {})

    # Set root template values from mapping (skip meta keys and NEWS)
    for fms_path, source_path in yfinance_map.items():
        if fms_path not in ["stockType", "default", "updated"] and not fms_path.startswith("NEWS"):
            set_nested_value(template, fms_path, source_path)

    template["stockType"] = stock_type
    template["default"]   = True
    template["updated"]   = True

    # Append .PVT suffix for private tickers if not already present
    fetch_ticker = f"{ticker}.PVT" if stock_type == "PRIVATE" and ".PVT" not in ticker else ticker

    try:
        t_obj       = yf.Ticker(fetch_ticker)
        i_whitelist = whitelist.get("info", [])
        toolbox     = {k: t_obj.info.get(k) for k in i_whitelist if k in t_obj.info}

        if not toolbox:
            raise ValueError("No data returned from yFinance")

        # Compute pseudo keys (description, year, history lows)
        pseudo_processing(toolbox, ticker)

        # Populate template from toolbox via recursive mapping
        recursive_fetch(template, toolbox)

        # Analyst recommendations (public stocks only)
        if stock_type == "PUBLIC":
            try:
                recs = t_obj.recommendations
                if recs is not None and not recs.empty:
                    set_nested_value(template, "RATINGS.strongBuy",  int(recs.strongBuy[0]))
                    set_nested_value(template, "RATINGS.buy",        int(recs.buy[0]))
                    set_nested_value(template, "RATINGS.hold",       int(recs.hold[0]))
                    set_nested_value(template, "RATINGS.sell",       int(recs.sell[0]))
                    set_nested_value(template, "RATINGS.strongSell", int(recs.strongSell[0]))
            except Exception:
                pass

        # News articles
        news_mapping = yfinance_map.get("NEWS", [])
        if news_mapping and isinstance(news_mapping, list) and len(news_mapping) > 0:
            blueprint = template["NEWS"][0] if template.get("NEWS") else {}
            field_map = news_mapping[0]
            raw_news  = t_obj.news[:10]
            clean_news = []
            for article in raw_news:
                item = copy.deepcopy(blueprint)
                for fms_field, source_path in field_map.items():
                    if source_path:
                        val = get_nested_value(article, source_path) if '.' in source_path else article.get(source_path)
                        if val is not None:
                            item[fms_field] = val
                clean_news.append(item)
            template["NEWS"] = clean_news
        else:
            template["NEWS"] = []

        return template

    except Exception: 
        console.print_exception()
        template["COMPANY"]["ticker"] = None
        return template



# =<< BRANCH 1. RUN BORN (--newborn | --reborn)
# === === === === === === === ===
def run_born(stock_type, ticker, mode_flag="--newborn"):
    mappings = util.load_json(PATH_MAPPINGS)
    dna_data = fetch_dna_sequence(ticker, stock_type, mappings)

    # REBORN SUB-BRANCH
    if mode_flag == "--reborn":
        ui.show_menu(
            breadcrumb=crumb.c_incubator_reborn,
            options=[],
            instruction=f"🔄 [{color.info}]Performing deep-sync for existing embryo...[/]",
            choice=False,
            prompt="XRXS"
        )
        time.sleep(3)
        # SAVE REBORN FILE
        payload = {ticker: dna_data}
        util.save_json(PATH_REBORN, payload)

        # CALL MERGER WITH REBORN FLAG
        console.print(f"✅ [{color.info}][{color.DONE}]DNA captured[/]. Routing to merger for pre-insemination health checks...[/]") 
        time.sleep(3)
        subprocess.run([sys.executable, PATH_MERGER, stock_type, ticker, "--reborn"])

    # NEWBORN SUB-BRANCH
    else:
        # HUMAN-READABLE DNA INSPECTION DASHBOARD
        accepted = dash.show_human_details(ticker, dna_data)

        # NEWBORN REJECTED
        if not accepted:
            msg = f"❎ [{color.info}][{color.ERR}]Newborn rejected[/]. Insemination aborted, returning to main menu.[/]"
            util.pause(reason="f",message=msg, enter="c")
            return

        # NEWBORN DNA SEQUENCING COMPLETE
        payload = {ticker: dna_data}
        util.save_json(PATH_NEWBORN, payload)

        # CALL MERGER WITH NEWBORN FLAG
        console.print(f"✅ [{color.info}][{color.DONE}]Newborn logged[/]. Routing to merger for comprehensive health report...[/]")
        subprocess.run([sys.executable, PATH_MERGER, stock_type, ticker, "--newborn"])

# =<< BRANCH 2. RUN REFRESH (headless portfolio update)
# === === === === === === === ===
def run_refresh(debug):
    mapping   = util.load_json(PATH_MAPPINGS)
    portfolio = util.load_json(PATH_PORTFOLIO)

    ui.merger_headless_banner()

    for ticker, data in portfolio.items():
        try:
            if "stockType" not in data:
                raise KeyError(f"[{color.info}][{color.ERR}]ERROR[/]: Missing stockType for [{color.FAIL}]{ticker}[/].[/]")

            s_type = data["stockType"]
            dna    = fetch_dna_sequence(ticker, s_type, mapping)

            if dna["COMPANY"]["ticker"] is not None:
                portfolio[ticker] = dna
                console.print(f"✔ [{color.info}][{color.ACTV}]{ticker:<8}[/] data fetched.[/]")
            else:
                console.print(f"⚠ [{color.info}][{color.WARN}][{color.ACTV}]{ticker:<8}[/] skipped[/]: DNA fetch returned empty.[/]")
        except Exception as e:
            console.print(f"✘ [{color.info}][{color.ERR}][{color.ACTV}]{ticker:<8}[/] error[/]: {e}.[/]")
            continue

    # Save updated portfolio to the refresh staging file
    os.makedirs(DIR_CACHE, exist_ok=True)
    util.save_json(PATH_REFRESH, portfolio)

    # Hand off to merger for integrity checks and swap
    result = subprocess.run([sys.executable, PATH_MERGER, "--refresh"])
    if result.returncode == 0:
        # Merger succeeded — consolidate per-ticker history into master historic.json
        all_tickers = list(portfolio.keys())
        hist.save_historic(all_tickers, DIR_ARCHIVE, PATH_HISTORIC)
        console.print(f"\n[{color.info}][{color.PASS}]Refresh completed successfully[/]. Historic data consolidated.[/]")
    else:
        # Merger failed — back up existing historic.json to avoid data loss
        if os.path.exists(PATH_HISTORIC):
            backup_path = f"{DIR_CACHE}/backup-historic.json"
            os.replace(PATH_HISTORIC, backup_path)
            console.print(f"\n[{color.info}][{color.FAIL}]Merger failed[/]. Historic data backed up to [{color.DOS}]{backup_path}[/].[/]")



# === === === === === === === ===
# == =<< MAIN >>- --- --- --- ---
if __name__ == "__main__":
    debug = True if "--debug" in sys.argv else False
    if "--refresh" in sys.argv:
        run_refresh(debug)
    elif len(sys.argv) >= 4:
        stock_type = sys.argv[1].upper()
        ticker     = sys.argv[2].upper()
        mode_flag  = sys.argv[3]
        run_born(stock_type, ticker, mode_flag, debug)
    elif len(sys.argv) == 3:
        run_born(sys.argv[1].upper(), sys.argv[2].upper(), f"--newborn", debug)
    else:
        console.print(f"[[{color.ACTV}]USAGE[/]]: python incubator.py [--refresh | TYPE TICKER [--newborn|--reborn]]")
        sys.exit(1)