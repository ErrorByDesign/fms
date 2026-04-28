#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import textwrap
import time
import yfinance as yf
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Confirm
from rich.syntax import Syntax
from rich.table import Table

# --- INITIALIZATION ---
sys.path.append(str(Path("./scripts/lib").resolve()))
console = Console()
cw = console.width

# Pathing
DIR_CACHE      = "./data/cache"
PATH_PORTFOLIO = "./data/portfolio.json"
PATH_MAPPING   = "./config/reference-mapping.json"
PATH_REPORT    = "./config/report-portfolio.json"
PATH_TEMPLATE  = "./config/template-portfolio.json"
PATH_NEWBORN   = "./data/cache/latest-newborn.json"
PATH_REBORN    = "./data/cache/latest-reborn.json"
PATH_REFRESH   = "./data/cache/latest-refresh.json"
PATH_MERGER    = "./scripts/lib/merger.py"

# --- CORE LOGIC HELPERS (RESTORED ENGINE) ---
def load_json(fp):
    if not os.path.exists(fp): return {}
    with open(fp, 'r', encoding='utf-8') as f: return json.load(f)

def save_json(fp, data):
    with open(fp, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

def set_nested_value(target_dict, path, value):
    keys = path.split('.')
    current = target_dict
    for key in keys[:-1]:
        if isinstance(current, list): return
        current = current.setdefault(key, {})
    if isinstance(current, dict):
        current[keys[-1]] = value

def get_nested_value(target_dict, path):
    keys = path.split('.')
    val = target_dict
    for k in keys:
        if isinstance(val, dict): val = val.get(k)
        else: return None
    return val

def format_desc(text):
    if not text: return ""
    clean = re.sub(r'\s+', ' ', str(text)).strip()
    return re.sub(r'\. (?=[A-Z])', '.\n\n', clean)

def recursive_fetch(data, toolbox, ignore_list):
    """RESTORED: Swaps template strings for yFinance data."""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                recursive_fetch(value, toolbox, ignore_list)
            elif isinstance(value, str) and value in toolbox:
                if value not in ignore_list:
                    data[key] = toolbox[value]

# --- UI HELPERS (EXACTLY AS PROVIDED) ---
def fit_to_width(text, pattern, border_pattern, border_width):
    total_gap = cw - len(text)
    left_count = (total_gap // 2) - border_width
    pL = pattern * left_count
    pR = pattern * ((total_gap - (left_count + border_width)) - border_width)
    return border_pattern + pL + text + pR + border_pattern

def is_valid(val):
    return val is not None and val != ""

def truncate(text, length=140):
    if not text: return ""
    return textwrap.shorten(str(text), width=length, placeholder="...")

def add_row(table, label, val, fmt=None):
    if is_valid(val):
        display_val = fmt(val) if fmt else str(val)
        table.add_row(label, display_val)

def show_human_details(ticker, data):
    # 1. COMPANY
    comp = data.get("COMPANY", {})
    t_comp = Table(show_header=False, box=None, padding=(0, 1))
    add_row(t_comp, " ", " ")
    add_row(t_comp, "[light_sky_blue3]Name:[/light_sky_blue3]", comp.get("name"), lambda x: f"[cornflower_blue]{x}[/cornflower_blue]")
    add_row(t_comp, "[light_sky_blue3]Exchange:[/light_sky_blue3]", comp.get("exchange"))
    add_row(t_comp, "[light_sky_blue3]Industry:[/light_sky_blue3]", comp.get("industry"))
    add_row(t_comp, "[light_sky_blue3]Sector:[/light_sky_blue3]", comp.get("sector"))
    add_row(t_comp, "[light_sky_blue3]Country:[/light_sky_blue3]", comp.get("country"))
    add_row(t_comp, "[light_sky_blue3]Website:[/light_sky_blue3]", comp.get("website"))
    add_row(t_comp, "[light_sky_blue3]Year Founded:[/light_sky_blue3]", comp.get("year"))
    add_row(t_comp, " ", " ")
    add_row(t_comp, "[light_sky_blue3]Overview:[/light_sky_blue3]", truncate(comp.get("description", ""), 180))
    # console.clear()
    console.print(Panel(t_comp, title="[bold cornflower_blue]COMPANY[/bold cornflower_blue]", border_style="light_sky_blue3"))

    # 2. FINANCIALS
    fin = data.get("FINANCIALS", {})
    t_fin = Table(show_header=False, box=None, padding=(0, 1))
    add_row(t_fin, " ", " ")
    add_row(t_fin, "[plum3]Market Price:[/plum3]", data.get("price"), lambda x: f"[plum1]${float(x):,.2f}[/plum1]")
    add_row(t_fin, "[plum3]Percentage Change:[/plum3]", fin.get("change"))
    add_row(t_fin, "[plum3]Market Cap:[/plum3]", fin.get("marketCap"), lambda x: f"${int(x):,}")
    add_row(t_fin, "[plum3]52 Week Low:[/plum3]", fin.get("weekLow"), lambda x: f"${float(x):,.2f}")
    add_row(t_fin, "[plum3]52 Week High:[/plum3]", fin.get("weekHigh"), lambda x: f"${float(x):,.2f}")
    add_row(t_fin, "[plum3]Target Price:[/plum3]", fin.get("yearTarget"), lambda x: f"${float(x):,.2f}")
    add_row(t_fin, " ", " ")
    console.print(Panel(t_fin, title="[bold plum1]FINANCIALS[/bold plum1]", border_style="plum3"))

    # 3. RATINGS
    rat = data.get("RATINGS", {})
    if any(is_valid(v) for v in rat.values()):
        t_rat = Table(show_header=False, box=None, padding=(0, 1))
        add_row(t_rat, " ", " ")
        add_row(t_rat, "[misty_rose1]Recommendation:[/misty_rose1]", rat.get("recommendationKey"), lambda x: f"[thistle1]{str(x).upper()}[/thistle1]")
        add_row(t_rat, "[misty_rose1]Total Analysts:[/misty_rose1]", rat.get("analystCount"))
        add_row(t_rat, "[misty_rose1]Rec Score:[/misty_rose1]", rat.get("recommendationMean"))
        add_row(t_rat, "[bright_cyan]Strong Buy:[/bright_cyan]", rat.get("strongBuy"))
        add_row(t_rat, "[cyan1]Buy:[/cyan1]", rat.get("buy"))
        add_row(t_rat, "[bright_sky_blue]Hold:[/bright_sky_blue]", rat.get("hold"))
        add_row(t_rat, "[light_salmon3]Sell:[/light_salmon3]", rat.get("sell"))
        add_row(t_rat, "[dark_orange3]Strong Sell:[/dark_orange3]", rat.get("strongSell"))
        add_row(t_rat, " ", " ")
        console.print(Panel(t_rat, title="[bold thistle1]RATINGS[/bold thistle1]", border_style="misty_rose1"))

    # 4. NEWS
    news_list = data.get("NEWS", [])
    if news_list:
        latest = news_list[0]
        t_news = Table(show_header=False, box=None, padding=(0, 1))
        add_row(t_news, " ", " ")
        add_row(t_news, "[light_salmon1]Source:[/light_salmon1]", latest.get("source"))
        add_row(t_news, "[light_salmon1]Title:[/light_salmon1]", latest.get("title"), lambda x: f"[bold]{x}[/bold]")
        add_row(t_news, "[light_salmon1]Summary:[/light_salmon1]", truncate(latest.get("summary", ""), 150))
        add_row(t_news, " ", " ")
        console.print(Panel(t_news, title="[bold light_salmon1]NEWS[/bold light_salmon1]", border_style="dark_khaki"))

# --- FETCH ENGINE ---
def fetch_dna_sequence(ticker, stock_type, mapping_conf):
    template    = load_json(PATH_TEMPLATE)["TICKER_SYMBOL"]
    type_conf   = mapping_conf.get(stock_type, {})
    ignore_list = mapping_conf.get("CONFIG", {}).get("IGNORE", [])

    # 1. Apply Mapping (Ignore NEWS dots for GPS)
    for path, val in type_conf.items():
        if path not in ["stockType", "default"] and not path.startswith("NEWS."):
            set_nested_value(template, path, val)
    template["stockType"] = stock_type

    fetch_ticker = f"{ticker}.PVT" if stock_type == "PRIVATE" and ".PVT" not in ticker else ticker
    try:
        t_obj = yf.Ticker(fetch_ticker)
        toolbox = t_obj.info
        if not toolbox: raise ValueError("No data")

        # Description & Year Extraction
        desc = toolbox.get("longBusinessSummary") or ""
        toolbox["description"] = format_desc(desc)

        year_val = toolbox.get("dateFounded")
        if not year_val:
            m = re.search(r'founded in (\d{4})|incorporated in (\d{4})', desc, re.I)
            if m: year_val = m.group(1) or m.group(2)
        if year_val: toolbox["year"] = str(year_val)[:4]

        # 2. Run Pseudo-Key Swap
        recursive_fetch(template, toolbox, ignore_list)

        # 3. Recommendations
        if stock_type == "PUBLIC":
            try:
                recs = t_obj.recommendations
                if recs is not None and not recs.empty:
                    toolbox.update(recs.iloc[-1].to_dict())
                    recursive_fetch(template, toolbox, [])
            except: pass

        # 4. News (Restored to 10)
        news_list = []
        for article in t_obj.news[:10]:
            item = {}
            for k in ["title", "description", "summary", "source", "category", "url", "publishDate", "premium", "freemium"]:
                p = type_conf.get(f"NEWS.{k}")
                if p: item[k] = get_nested_value(article, p)
            news_list.append(item)
        template["NEWS"] = news_list
        return template
    except:
        template["COMPANY"]["ticker"] = None
        return template

# --- MAIN BRANCHES ---
def run_headless_update():
    registry  = load_json(PATH_REPORT)
    mother    = load_json(PATH_PORTFOLIO)
    mapping   = load_json(PATH_MAPPING)
    portfolio = load_json(PATH_PORTFOLIO) 

    title_str    = "A U T O M A T E D   H E A D L E S S   U P D A T E   L O G S"
    pattern      = " "
    brdr_pattern = ""
    brdr_width   = 0
    title_auto   = fit_to_width(title_str, pattern, brdr_pattern, brdr_width)
    title_len    = len(title_str)
    line         = ("·" * title_len)
    pad_left     = (" " * (((cw - len(title_str)) // 2) - 1))
    title_line = fit_to_width(line, pattern, brdr_pattern, brdr_width)
    
    console.clear()
    console.print(f"\n[bold plum3]{title_line}[/bold plum3]")
    time.sleep(0.5)
    console.print(f"\n[bold plum1]{title_auto}[/bold plum1]")
    time.sleep(0.5)
    console.print(f"\n[bold plum3]{title_line}[/bold plum3]\n")
    time.sleep(1)

    for ticker, data in portfolio.items():
        try:
            if "stockType" not in data:
                raise KeyError(f"Missing stockType for {ticker}")

            s_type = data["stockType"]

            dna = fetch_dna_sequence(ticker, s_type, mapping)

            if dna["COMPANY"]["ticker"] is not None:
                mother[ticker] = dna
                console.print(f"{pad_left}[dim] • [green]✔[/green] [bold light_steel_blue1]{ticker:<8} [/bold light_steel_blue1][navajo_white] data fetched[/navajo_white][/dim]")
            else:
                console.print(f"[dim][yellow]⚠[/yellow] [bold light_steel_blue1]{ticker:<8}[/bold light_steel_blue1] skipped: DNA fetch returned empty.[/dim]")

        except Exception as e:
            console.print(f"[dim][bold indian_red]✘ ERROR[/bold indian_red]: Could not process [bold light_steel_blue1]{ticker}[/bold light_steel_blue1]. Details: [light_coral]{e}[/light_coral][/dim]")
            continue

    time.sleep(1)
    os.makedirs(DIR_CACHE, exist_ok=True)
    save_json(PATH_REFRESH, mother)
    subprocess.run([sys.executable, PATH_MERGER, "--refresh"])

def run_newborn_search(stock_type, ticker, mode_flag="--newborn"):
    """
    Handles the DNA fetch and branches based on whether it's a new 
    entry or a targeted update (reborn).
    """
    # 1. LOAD CONFIGS (Required for mapping_conf)
    mapping = load_json(PATH_MAPPING)

    # 2. FETCH DNA (Fixed: Passing the required mapping_conf)
    dna_data = fetch_dna_sequence(ticker, stock_type, mapping) 

    # 3. THE BRANCHING LOGIC
    if mode_flag == "--reborn":
        console.print(f"\n[bold cyan]///[/][light_slate_grey]SYSTEM[/][bold cyan]//[/][navajo_white1]TARGETED UPDATE[/][bold cyan]//[/][light_steel_blue1]{ticker}[/]")
        console.print(f"[dim]Performing deep-sync for existing entity...[/]")
        
        # Ensure we wrap the single ticker in a dict for the merger to iterate
        payload = {ticker: dna_data}
        save_json(PATH_REBORN, payload)
        
        console.print(f"[spring_green1]DNA captured. Routing to merger...[/]")
        subprocess.run([sys.executable, "scripts/lib/merger.py", stock_type, ticker, "--reborn"])
        
    else:
        # STANDARD PATH: Human Dashboard for New Tickers
        show_human_details(ticker, dna_data) # Fixed function name
        
        # Ensure we wrap the single ticker in a dict for the merger to iterate
        payload = {ticker: dna_data}
        save_json(PATH_NEWBORN, payload)
        
        console.print(f"[spring_green1]Newborn logged. Routing to merger...[/]")
        subprocess.run([sys.executable, "scripts/lib/merger.py", stock_type, ticker, "--newborn"])

if __name__ == "__main__":
    if "--refresh" in sys.argv:
        run_headless_update()
    elif len(sys.argv) >= 4:
        # Scenario: main.py passed [type, ticker, flag]
        stock_type = sys.argv[1].upper()
        ticker = sys.argv[2].upper()
        mode_flag = sys.argv[3] # This will be "--newborn" or "--reborn"
        
        run_newborn_search(stock_type, ticker, mode_flag)
    elif len(sys.argv) == 3:
        # Fallback: maintain compatibility if called without a flag
        run_newborn_search(sys.argv[1].upper(), sys.argv[2].upper(), "--newborn")
