#!/usr/bin/env python3
# -------------------------------------------------------
# M O D U L E   M E R G E R   &   H E A L T H   A U D I T
# -------------------------------------------------------
import json
import os
import sys
import time
from datetime import datetime
from rich.console import Console
from rich.console import Group
from rich.panel import Panel
console = Console()
cw = console.width

# --- PATH CONFIGURATION ---
PATH_BACKUP          = "./data/cache/backup-portfolio.json"
PATH_MAPPING         = "./config/reference-mapping.json"
PATH_REPORT          = "./config/report-portfolio.json"
PATH_TEMPLATE_REPORT = "./config/template-report.json"
PATH_PORTFOLIO       = "./data/portfolio.json"
PATH_NEWBORN         = "./data/cache/latest-newborn.json"
PATH_REBORN          = "./data/cache/latest.reborn.json"
PATH_REFRESH         = "./data/cache/latest-refresh.json"

# --- DEVELOPER ---
def pause(msg="Press Enter to continue..."):
    console.input(f"\n[bold yellow]DEBUG PAUSE:[/] {msg}")

# --- CORE HELPERS ---
def load_json(filepath):
    if not os.path.exists(filepath): return {}
    with open(filepath, 'r') as f: return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f: json.dump(data, f, indent=4)

def get_ignore_list(mapping):
    """
    Dynamically extracts all ignored keys and arrays from reference-mapping.
    """
    config = mapping.get("CONFIG", {})
    return config.get("arrays", []) + config.get("ignore", [])

def count_populated_leaves(data, ignore_list, current_path=""):
    """
    Recursively counts leaves while respecting dot-notation paths 
    (e.g., 'COMPANY.facts' or 'NEWS') defined in the ignore_list.
    """
    count = 0
    if isinstance(data, dict):
        for k, v in data.items():
            # Build the path tracker (e.g., "COMPANY" -> "COMPANY.facts")
            path = f"{current_path}.{k}" if current_path else k
            if path in ignore_list: continue
            
            count += count_populated_leaves(v, ignore_list, path)
    elif isinstance(data, list):
        pass # Strict omission of arrays
    else:
        if data is not None and data != "": 
            count += 1
    return count

def abort(issue_type, cause, detail):
    """
    Kills the script and reports the exact data discrepancy.
    """
    console.clear()
    console.print(f"\n[bold red]/// SYSTEM HEALTH FAILURE: {issue_type}[/]")
    console.print(f"[red]CAUSE: [white]{ticker}[/]")
    console.print(f"[yellow]DETAIL: {detail}[/]")
    console.print(f"\n[bold yellow]-- ABORTING MERGER --[/]\n")
    input("\nPress Enter to exit...") 
    sys.exit(1)

def fit_to_width(text, pattern, border_pattern, border_width):
    total_gap = cw - len(text)
    left_count = (total_gap // 2) - border_width
    pL = pattern * left_count
    pR = pattern * ((total_gap - (left_count + border_width)) - border_width)
    return border_pattern + pL + text + pR + border_pattern

# --- BRANCH 1: THE NEWBORN (INSEMINATION) ---
def process_organism(flag):
    # Determine source file based on flag
    source_path = PATH_REBORN if flag == "--reborn" else PATH_NEWBORN
    
    data_payload = load_json(source_path)
    if not data_payload:
        console.print(f"[ERROR] No data found in {source_path}.")
        return

    mapping   = load_json(PATH_MAPPING)
    registry  = load_json(PATH_REPORT)
    portfolio = load_json(PATH_PORTFOLIO)
    template  = load_json(PATH_TEMPLATE_REPORT)

    ignore_list = get_ignore_list(mapping)
    reg_ptf = registry.get("PORTFOLIO", {})
    leaf_nodes_ptf = reg_ptf.get("leafNodesPtf", 31)

    for ticker, data in data_payload.items():
        stock_type = data.get("stockType", "PUBLIC").upper()
        baseline   = reg_ptf["scorePvt"] if stock_type == "PRIVATE" else reg_ptf["scorePlc"]

        # The Census
        p = count_populated_leaves(data, ignore_list)
        score = round((p / leaf_nodes_ptf) * 100, 2)

        # The Gatekeeper
        if score != baseline:
            console.print(f"\n[ABORT] {ticker} DNA mismatch. Score: {score}% (Expected: {baseline}%)")
            os.rename(source_path, f"./data/cache/{ticker}-abortion.json")
            console.print(f"Check fetus at ./data/cache/{ticker}-abortion.json")
            pause()
            return

        # --- HUMAN DASHBOARD ---
        console.print(f"\n[thistle1]Ticker: [/thistle1][bold light_steel_blue1]{ticker}[/bold light_steel_blue1]")
        console.print(f"[thistle1]Score: [/thistle1][bold light_steel_blue1]{score}%[/bold light_steel_blue1]")
        console.print(f"[thistle1]Baseline: [/thistle1][bold light_steel_blue1]{baseline}%[/bold light_steel_blue1]")
        console.print(f"[thistle1]Populated leaves: [/thistle1][bold light_steel_blue1]{p}[/bold light_steel_blue1]")
        pause()

        # --- ORIGINAL MENU SYSTEM ---
        while True:
            console.clear()
            console.print(f"\n[bold green]/// DNA VALIDATED: {score}%[/]")
            console.print(f"\n[white]0. BACK[/]")
            console.print(f"[bold cyan]1. INSEMINATE[/]")
            console.print(f"[white]2. VIEW JSON[/]")
            console.print(f"[white]3. OPEN FILE[/]\n")
            
            cmd = console.input(">_ ")
            
            if cmd == "0":
                return
            elif cmd == "1":
                # Break to proceed to the merge logic below
                break
            elif cmd == "2":
                # --- ORIGINAL JSON PANEL ---
                console.clear()
                console.print(f"\n[bold yellow]/// RAW DNA SEQUENCE: {ticker}[/]\n")
                
                # Checks for jq in Termux for the original formatted look
                if os.path.exists("/system/bin/jq"):
                    os.system(f"cat {source_path} | jq '.'")
                else:
                    # Fallback if jq is missing
                    from rich.json import JSON
                    console.print(JSON.from_data(data))
                
                console.print("\n" + "-"*30)
                pause()
            elif cmd == "3":
                if os.path.exists("/system/bin/termux-info"):
                    os.system(f"termux-open {source_path}")
                else:
                    os.startfile(source_path) if os.name == 'nt' else os.system(f"open {source_path}")

        # --- THE MERGE (INJECTION) ---
        # 1. Update Portfolio
        portfolio[ticker] = data 
        
        if flag == "--newborn":
            # 2. Deactivate old King/Active entry
            for existing_ticker, entry in registry.items():
                if existing_ticker != "PORTFOLIO" and isinstance(entry, dict):
                    if entry.get("active") is True:
                        entry["active"] = False
            
            # 3. Create the new Report Entry from template
            new_entry = json.loads(json.dumps(template.get("TICKER_SYMBOL", {})))
            new_entry["HISTORY"]["birthDate"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            new_entry["active"] = True
            new_entry["score"] = score
            new_entry["corrupt"] = False
            
            # 4. Inject into Registry
            registry[ticker] = new_entry
            
            # 5. Registry Macro Math
            reg_ptf["countPtf"] += 1
            if stock_type == "PRIVATE": 
                reg_ptf["countPvt"] += 1
            else: 
                reg_ptf["countPlc"] += 1

        # Macro Score Re-calculation
        if reg_ptf["countPtf"] > 0:
            reg_ptf["scorePtf"] = round(
                ((reg_ptf["countPlc"] * reg_ptf["scorePlc"]) + 
                 (reg_ptf["countPvt"] * reg_ptf["scorePvt"])) / reg_ptf["countPtf"], 2
            )
        registry["PORTFOLIO"]["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- THE FINAL COMMIT ---
        save_json(PATH_REPORT, registry)
        save_json(PATH_PORTFOLIO, portfolio)
        
        console.print(f"\n[bold gray100][[bold thistle1]SUCCESS[/bold thistle1]] [bold light_pink1]{ticker}[/bold light_pink1] ([bold orchid1]{stock_type}[/bold orchid1]) DNA merged successfully.[/bold gray100]")
        pause("\nPress Enter to finish...")

# --- BRANCH 2: THE MOTHER (BULK UPDATE & AUDIT) ---
def process_refresh():
    title_str     = "X  E  R  X  E  S      H  E  A  L  T  H      R  E  P  O  R  T"
    pad_left      = (" " * (((cw - len(title_str)) // 2)))

    refresh  = load_json(PATH_REFRESH)
    registry = load_json(PATH_REPORT)
    mapping  = load_json(PATH_MAPPING)

    if not refresh or not registry:
        abort("[FILE MISSING]", PATH_REFRESH if not refresh else PATH_REPORT, f"The file {PATH_REFRESH if not refresh else PATH_REPORT} is missing which is required for a succesful portfolio updated.")

    reg_ptf = registry.get("PORTFOLIO", {})
    ignore_list = get_ignore_list(mapping)

    # 1. Macro Census (Pre-Swap Checksum)
    count_ptf = reg_ptf["countPtf"]
    count_plc = sum(1 for d in refresh.values() if d.get("stockType", "").upper() == "PUBLIC")
    count_pvt = sum(1 for d in refresh.values() if d.get("stockType", "").upper() == "PRIVATE")
    total_count = count_plc + count_pvt

    calc_score = round(
        ((count_plc * reg_ptf["scorePlc"]) + (count_pvt * reg_ptf["scorePvt"])) / total_count, 2
    ) if total_count > 0 else 0

    # 2. The Paternity Test
    if total_count != reg_ptf["countPtf"] or calc_score != reg_ptf["scorePtf"]:
        detail = f"[thistle1][[bold light_coral]CRITICAL FAILURE[/bold light_coral] DNA Mismatch. Swap aborted.\nExpected: Count [bold khaki3]{reg_ptf['countPtf']}[/bold khaki3] | Score [bold khaki3]{reg_ptf['scorePtf']}[/bold khakie]\nReceived: Count [bold light_coral]{total_count}[/bold light_coral] | Score [bold light_coral]{calc_score}[/bold light_coral][/thistle1]"
        abort("[CRITICAL FAILURE]", f"total count" if total_count != reg_ptf["countPtf"] else "calculated score", detail)

    # 3. The Swap
    if os.path.exists(PATH_PORTFOLIO):
        os.replace(PATH_PORTFOLIO, PATH_BACKUP)
    os.replace(PATH_REFRESH, PATH_PORTFOLIO)
    console.print(f"\n{pad_left}[navajo_white][[bold cyan1]SUCCESS[/bold cyan1]] Macro DNA verified. Portfolio swapped.[/navajo_white]")

    # 4. Load the updated data into a new 'portfolio' dict and purge the 'refresh' dict
    with open('./data/portfolio.json', 'r') as f:
        portfolio = json.load(f)

    del refresh

    leaf_nodes_ptf = reg_ptf.get("leafNodesPtf")
    leaf_nodes_plc = reg_ptf.get("leafNodesPlc")
    leaf_nodes_pvt = reg_ptf.get("leafNodesPvt")

    pattern       = " "
    brdr_pattern  = ""
    brdr_width    = 0
    title_health  = fit_to_width(title_str, pattern, brdr_pattern, brdr_width)
    title_len     = len(title_str)
    dble_line     = ("=" * title_len)
    line          = ("·" * title_len)
    title_line    = fit_to_width(dble_line, pattern, brdr_pattern, brdr_width)
    divide_line   = fit_to_width(line, pattern, brdr_pattern, brdr_width)
    control_str   = "[CONTROL GROUP]"
    ctrl_str_1_a  = "[dim]Stock count PTF: [/]"
    ctrl_str_1_b  = "    [dim][bold]||[/bold]    Leaf nodes PVT: [/dim]"
    ctrl_str_2_a  = "[dim]Stock count PLC: [/]"
    ctrl_str_2_b  = "    [dim][bold]||[/bold]    Leaf nodes PVT: [/dim]"
    ctrl_str_3_a  = "[dim]Stock count PVT: [/]"
    ctrl_str_3_b  = "    [dim][bold]||[/bold]    Leaf nodes PVT: [/dim]"
    control_str_1 = (f"{ctrl_str_1_a}{count_ptf}{ctrl_str_1_b}{leaf_nodes_ptf}")
    control_str_2 = (f"{ctrl_str_2_a}{count_plc}{ctrl_str_2_b}{leaf_nodes_plc}")
    control_str_3 = (f"{ctrl_str_3_a}{count_pvt}{ctrl_str_3_b}{leaf_nodes_pvt}")
    control_pad   = (" " * (title_len - 15))
    control_mix   = (f"{control_str}{control_pad}")
    control_mix_1 = (control_str_1)
    control_mix_2 = (control_str_2)
    control_mix_3 = (control_str_3)
    control       = fit_to_width(control_mix, pattern, brdr_pattern, brdr_width)
    control_1     = fit_to_width(control_mix_1, pattern, brdr_pattern, brdr_width)
    control_2     = fit_to_width(control_mix_2, pattern, brdr_pattern, brdr_width)
    control_3     = fit_to_width(control_mix_3, pattern, brdr_pattern, brdr_width)

    time.sleep(1)
    console.print(f"\n[bold misty_rose1]{title_health}[/bold misty_rose1]")
    time.sleep(0.1)
    console.print(f"[dim]{title_line}[/dim]")
    time.sleep(0.5)
    console.print(f"[bold thistle1]{control}[/bold thistle1]")
    time.sleep(0.1)
    console.print(f"{pad_left}[thistle1]{control_1}[/thistle1]")
    time.sleep(0.1)
    console.print(f"{pad_left}[thistle2]{control_2}[/thistle2]")
    time.sleep(0.1)
    console.print(f"{pad_left}[thistle3]{control_3}[/thistle3]")
    time.sleep(0.5)
    console.print(f"\n{pad_left}[misty_rose1]Calculated score: [/misty_rose1][bold light_steel_blue1]{calc_score}[/bold light_steel_blue1]")
    time.sleep(0.1)
    console.print(f"{pad_left}[dim]{dble_line}[/dim]")
    time.sleep(0.1)

    for ticker, data in portfolio.items():
        if ticker not in registry:
            abort("[REGISTRY MISSING]", ticker, "Ticker count mismatch between thw registry - config/report-portfolio.json - and the portfolio - data/portfolio.json.")

        reg_entry = registry[ticker]

        stock_type = data.get("stockType").upper()
        baseline   = reg_ptf["scorePvt"] if stock_type == "PRIVATE" else reg_ptf["scorePlc"]

        p = count_populated_leaves(data, ignore_list)
        score = round((p / leaf_nodes_ptf) * 100, 2)

        ticker_field = ticker

        if score != baseline or ticker_field is None:
            registry[ticker]["corrupt"] = True
            registry[ticker]["score"] = score
            console.print(f"\n[thistle1][[bold light_coral]WARNING[/bold light_coral]] [bold light_steel_blue1]{ticker}[/bold light_steel_blue1] flagged as corrupt. (Score: [bold indian_red]{score}%[/bold indian_red], Ticker integrity: [bold light_steel_blue1]{ticker_field}[/bold light_steel_blue1])")
            time.sleep(0.5)
        else:
            registry[ticker]["corrupt"] = False
            registry[ticker]["score"] = score
            console.print(f"{pad_left}[thistle1][[bold thistle1]TEST SUBJECTS[/bold thistle1]]\n{pad_left}Ticker: [bold light_steel_blue1]{ticker}[/bold light_steel_blue1]\n{pad_left}Stock type: [bold light_steel_blue1]{stock_type.lower()}[/bold light_steel_blue1]\n{pad_left}Populated leaves: [bold light_steel_blue1]{p}[/bold light_steel_blue1] (expected: [bold khaki3]{leaf_nodes_pvt if stock_type == 'PRIVATE' else leaf_nodes_plc}[/bold khaki3])\n{pad_left}SCORE: [bold light_steel_blue1]{score}%[/bold light_steel_blue1] (expected: [bold khaki3]{baseline}%[/bold khaki3])\n{pad_left}RESULTS: {'[bold cyan1]PASS[/bold cyan1]' if score == baseline else '[bold light_coral]FAIL[/bold light_coral]'}[/thistle1]")
            console.print(f"[dim]{divide_line}[/dim]")
            time.sleep(0.5)

    registry["PORTFOLIO"]["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_json(PATH_REPORT, registry)
    time.sleep(1)
    console.print(f"\n{pad_left}[navajo_white][[bold light_steel_blue1]FINDINGS[/bold light_steel_blue1]] Health audit complete. Registry signed.[/navajo_white]")
    time.sleep(0.5)
    console.print(f"\n{pad_left}[dodger_blue][[bold light_steel_blue1]AUTOMATION[/bold light_steel_blue1]] Pyyhon script automation completed succesfully.\n{pad_left}Ready to push updated files to FMSLite.[/dodger_blue]\n")
    time.sleep(3)

# --- FINAL ROUTER ---
if __name__ == "__main__":
    if "--refresh" in sys.argv:
        process_refresh()
        sys.exit(0)

    # incubator.py calls: merger.py [TYPE] [TICKER] [FLAG]
    if len(sys.argv) >= 4:
        # We only need the flag to trigger process_organism
        mode_flag = sys.argv[3].lower()
        process_organism(mode_flag)
    else:
        console.print("Usage: python merger.py [TYPE] [TICKER] [--newborn | --reborn]")
        sys.exit(1)
