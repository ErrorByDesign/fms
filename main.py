#!/usr/bin/env python3
# =================================================
# X E R X E S   M A I N   P Y T H O N   S C R I P T
# ===========
import json
import os
import random
import subprocess
import sys
import time

from datetime import date
from pathlib import Path
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text

from scripts.lib.verifier import verify_stock

console = Console()
cw = console.width

# CONFIG
# ------
LIBRARY_DIR        = Path("./scripts/lib")
MODULES_DIR        = Path("./modules")
SCRIPTS_DIR        = Path("./scripts")
DOCUMENTATION_FILE = Path("./documentation/wiki.json")
OPERATIONS_FILE    = Path("./modules/operations.py")
PORTFOLIO_FILE     = Path("./data/portfolio.json")

# BANNERS
# -------
BANNERS = [
    ":: F I N A N C I A L ::: M O D E L I N G ::: S H E L L ::\n:: ::: ::: ::: ::: O P E R A T I O N S ::: ::: ::: ::: ::\n\n\n",
    "═━═━═ XERXES FMS OPERATIONS ═━═━═\n═━═━═ ═━═━═ ═━═━ ━═━═ ═━═━═ ═━═━═\n\n\n",
    "                          ★ OPERATION XERXES ★                         \n· • THE OPERATIC FINE ANNE SHALL MODEL IN MICHELLE OPERATING TABLE • ·\n\n\n"
]

BANNER  = random.choice(BANNERS)

# DISPLAY
# -------
def show_banner():
    console.print(f"\n[bold khaki3]{BANNER}[/bold khaki3]\n")

# DESIGN
# ------
def fit_to_width(text, pattern, border_pattern, border_width):
    total_gap = cw - len(text)
    left_count = (total_gap // 2) - border_width
    pL = pattern * left_count
    pR = pattern * ((total_gap - (left_count + border_width)) - border_width)
    return border_pattern + pL + text + pR + border_pattern

# INTRO PAGE
# ----------
def intro_page():
    is_headless      = False
    portfolio_exists = os.path.exists("./data/portfolio.json")
    system_ready     = portfolio_exists and os.path.getsize("./data/portfolio.json") > 0
    heartbeat_stable = system_ready
    
    xerxes_str = "M  O  T  H  E  R      P  R  O  J  E  C  T"
    fms_str = "F I N A N C I A L   M O D E L L E I N G   S H E L L   L i t e"
    fms_str_mini = "FINANCIAL MODELLING SHELL: Lite"

    # Welcome page globals
    health_str = ":   ::   :::   H  E  A  L  T  H    S  T  A  B  L  E   :::   ::   :" if heartbeat_stable else "DIAGNOSTICS REQUIRED"
    online_str = "·   ··   •••   S  Y  S  T  E  M    O  N  L  I  N  E   •••   ··   ·" if system_ready else "DATABASE MISSING"
    status_color_health = "blink red" if heartbeat_stable else "blink light_coral"
    status_color_online = "plum3" if system_ready else "bold light_coral"
    status_msg_health = Text(health_str, style=status_color_health, no_wrap=True)
    status_msg_online = Text(online_str, style=status_color_online, no_wrap=True)

    text = "|  PRESS ENTER TO ENTER  |"
    pattern = ":"
    border_width = 1
    border_pattern = "|"
    enter = fit_to_width(text, pattern, border_pattern, border_width)
    textLen = len(text)
    text = ("|" + ("⁻" * (textLen - 2)) + "|")
    paddingT = fit_to_width(text, pattern, border_pattern, border_width)
    text = ("|" + ("_" * (textLen - 2)) + "|")
    paddingB = fit_to_width(text, pattern, border_pattern, border_width)
    top_bottom = ("|" + ("=" * (cw - 2)) + "|")
    
    console.print(Panel(
        Align.center(f"[khaki3]{fms_str_mini if cw < 50 else fms_str}[/]"),
        title="[coral_green]xerxes[/]",
        title_align="left",
        padding=(0,0),
        border_style="navajo_white1",
        subtitle="MOTHER—PROJECT",
        subtitle_align="right"
    ))

    console.print(f"[misty_rose1]{top_bottom}[/misty_rose1]")
    console.print((("[bold misty_rose1]|[/bold misty_rose1]" + ("[bold medium_orchid3]:[/bold medium_orchid3]" * (cw - 2))) + "[bold misty_rose1]|[/bold misty_rose1]" + "\n") * 7 + (("[bold misty_rose1]|[/bold misty_rose1]" + ("[bold medium_orchid3]:[/bold medium_orchid3]" * (cw - 2))) + "[bold misty_rose1]|[/bold misty_rose1]"))
    console.print(Panel(
        Align.center(f"[{status_color_health}]{status_msg_health}[/]"), 
        title="[bold misty_rose3]XERXES FINANCIAL MODELLING SHELL OS v2.0[/bold misty_rose3]", 
        title_align="center",
        padding=(1, 1),
        border_style="misty_rose1",
        subtitle=f"MODE: {'AUTOMATED' if is_headless else 'DIVINE INTERVENTION'}",
        subtitle_align="right"
    ))
    console.print((("[bold misty_rose3]|[/bold misty_rose3]" + ("[bold pale_violet_red1]:[/bold pale_violet_red1]" * (cw - 2))) + "[bold misty_rose3]|[/bold misty_rose3]" + "\n") * 2 + (("[bold misty_rose3]|[/bold misty_rose3]" + ("[bold pale_violet_red1]:[/bold pale_violet_red1]" * (cw - 2))) + "[bold misty_rose3]|[/bold misty_rose3]"))
    console.print(f"[plum3]{paddingT}[/plum3]")
    console.print(f"[plum1]{enter}[/plum1]")
    console.print(f"[plum3]{paddingB}[/plum3]")
    console.print((("[bold misty_rose3]|[/bold misty_rose3]" + ("[bold pale_violet_red1]:[/bold pale_violet_red1]" * (cw - 2))) + "[bold misty_rose3]|[/bold misty_rose3]" + "\n") * 2 + (("[bold misty_rose3]|[/bold misty_rose3]" + ("[bold pale_violet_red1]:[/bold pale_violet_red1]" * (cw - 2))) + "[bold misty_rose3]|[/bold misty_rose3]"))
    console.print(Panel(
        Align.center(status_msg_online), 
        title="[bold misty_rose3]XERXES CORE[/bold misty_rose3]",
        title_align="center",
        padding=(1, 2),
        border_style="misty_rose1",
        subtitle=f"LOGIC: {'STABLE' if system_ready else 'CRITICAL FAILURE'}",
        subtitle_align="right"
    ))
    console.print((("[bold misty_rose1]|[/bold misty_rose1]" + ("[bold medium_orchid3]:[/bold medium_orchid3]" * (cw - 2))) + "[bold misty_rose1]|[/bold misty_rose1]" + "\n") * 7 + (("[bold misty_rose1]|[/bold misty_rose1]" + ("[bold medium_orchid3]:[/bold medium_orchid3]" * (cw - 2))) + "[bold misty_rose1]|[/bold misty_rose1]"))
    console.print(f"[misty_rose1]{top_bottom}[/misty_rose1]")
    input()

    main_menu()

# LOAD EXTERNAL DATA
# ------------------
def load_wiki():
    if DOCUMENTATION_FILE.exists():
        try:
            with open(DOCUMENTATION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"DIRECTORY_STRUCTURE.SCRIPTS": {}}
    return {"DIRECTORY_STRUCTURE.SCRIPTS": {}}

def get_disp_name(name):
    return name.replace('incubator.py', 'search').replace('updata.sh', 'update').title().upper()

def get_scripts():
    if not SCRIPTS_DIR.exists():
        SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        return []
    return sorted([f.name for f in SCRIPTS_DIR.iterdir() if f.is_file() and f.suffix in ['.py', '.sh']])

# MAIN MENU
# ---------
def main_menu():
    wiki = load_wiki()
    scripts = get_scripts()
    while True:
        console.clear()
        show_banner()
        console.print("[misty_rose1][bold]///[light_steel_blue1]MAIN[/light_steel_blue1][/bold][/misty_rose1]\n")
        if not scripts:
            console.print("[indian_red1]No scripts found in ./scripts/[/indian_red1]")
            input("\nPress Enter to exit...")
            break
        console.print("0. [light_salmon3]EXIT[/light_salmon3]")
        for i, script in enumerate(scripts, 1):
            console.print(f"{i}. [honeydew2]{get_disp_name(script)}[/honeydew2]")
        console.print()
        choice = IntPrompt.ask(">_ ", default=0, show_default=False, show_choices=False)
        if choice == 0:
            if Confirm.ask("\n[bold light_salmon3]Exit program?[/bold light_salmon3][pale_turquoise1][y/n][/pale_turquoise1]", default=True, show_default=False):
                console.print("[pale_turquoise1]\nGoodbye!\n[/pale_turquoise1]")
                break
        elif 1 <= choice <= len(scripts):
            selected_file = scripts[choice - 1]
            script_menu(selected_file, wiki)

def script_menu(script_file, wiki):
    disp_name   = get_disp_name(script_file)
    script_path = SCRIPTS_DIR / script_file
    while True:
        console.clear()
        show_banner()
        console.print(f"[misty_rose1][bold]///[light_slate_grey]MAIN[/light_slate_grey]//[/bold][light_steel_blue1]{disp_name}[/light_steel_blue1][/misty_rose1]\n")
        console.print("0. [light_goldenrod3]BACK[/light_goldenrod3]")
        console.print("1. [sky_blue1]EXECUTE[/sky_blue1]")
        console.print("2. [plum3]INFO[/plum3]\n")
        choice = IntPrompt.ask(">_ ", default=0, show_default=False, show_choices=False)
        if choice == 0:
            return
        elif choice == 1:
            if script_file == "incubator.py":
                execute_newborn(script_path)
            elif script_file == "update_portfolio.sh":
                run_refresh_process()
            else:
                execute_script(script_path, disp_name)
        elif choice == 2:
            show_info(script_file, script_path, wiki)

# RUN PROCESS
# -----------
def run_backup_process():
    """Helper to run the operations.py backup script."""
    subprocess.run([sys.executable, OPERATIONS_FILE])
    time.sleep(3)

def run_newborn_process(ticker, stock_type, script_path):
    """Path for brand new stocks."""
    run_backup_process()
    subprocess.run([sys.executable, str(script_path), stock_type, ticker, "--newborn"])

def run_reborn_process(ticker, stock_type):
    """Path for existing stocks (Targeted Update)."""
    run_backup_process()
    # Note: Using 'incubator.py' directly since we know the name
    subprocess.run([sys.executable, "scripts/incubator.py", stock_type, ticker, "--reborn"])

def run_refresh_process():
    """Path for global portfolio health check."""
    run_backup_process()
    subprocess.run([sys.executable, "scripts/incubator.py", "--refresh"])

# EXECUTE SCRIPT
# --------------
def execute_newborn(script_path):
    while True:
        console.clear()
        show_banner()
        console.print("[misty_rose1][bold]///[light_slate_grey]MAIN[/light_slate_grey]//[light_slate_grey]SEARCH[/light_slate_grey]//C:>[/bold][light_steel_blue1]Choose stock type[/light_steel_blue1][bold]_[/bold][/misty_rose1]\n")
        console.print("0. [light_goldenrod3]BACK[/light_goldenrod3]")
        console.print("1. [sky_blue2]PRIVATE[/sky_blue2]")
        console.print("2. [sky_blue1]PUBLIC[/sky_blue1]\n")
        t_choice = IntPrompt.ask(">_ ", default=0, show_default=False, show_choices=False)
        if t_choice == 0: return
        elif t_choice in [1, 2]: break
        
    # --- FIXED: Define stock_type BEFORE using it in the UI print ---
    types = {1: "PRIVATE", 2: "PUBLIC"}
    stock_type = types[t_choice]
    
    console.clear()
    show_banner()
    # RESTORED & CORRECTED: This print now has access to stock_type
    console.print(f"[misty_rose1][bold]///[light_slate_grey]MAIN[/light_slate_grey]//[light_slate_grey]SEARCH[/light_slate_grey]//[light_slate_grey]TYPE[/light_slate_grey]:[navajo_white1]{stock_type}[/navajo_white1]//C:>[/bold][light_steel_blue1]{'Enter ticker symbol' if stock_type == 'PUBLIC' else 'Enter company name'}[/light_steel_blue1][bold]_[/bold][/misty_rose1]\n")
    console.print("0. [light_goldenrod3]BACK[/light_goldenrod3]\n")
    
    user_input = input(">_ ").upper().strip()
    if user_input == "0" or not user_input: return
    
    # Check portfolio
    with open(PORTFOLIO_FILE, 'r') as f:
        portfolio = json.load(f)

    if user_input in portfolio:
        console.clear()
        show_banner()
        # RESTORED: Satisfied requirement line
        console.print(f"[misty_rose1][bold]///[light_slate_grey]MAIN[/light_slate_grey]//[light_slate_grey]SEARCH[/light_slate_grey]//[light_slate_grey]TYPE[/light_slate_grey]:[navajo_white1]{stock_type}[/navajo_white1]//[light_slate_grey]{'TICKER' if stock_type == 'PUBLIC' else 'COMPANY'}[/light_slate_grey]:[navajo_white1]{user_input}[/navajo_white1]//C:>[/bold][light_steel_blue1]Requirement already satisfied:[/light_steel_blue1] [bold khaki3]{user_input}[/bold khaki3] in ./data/[bold honeydew2]portfolio[/bold honeydew2].json[bold]_[/bold][/misty_rose1]\n")
        
        console.print("0. BACK")
        console.print("1. TARGETED UPDATE (REBORN)")
        console.print("2. FULL PORTFOLIO UPDATE (REFRESH)")
        
        fork_choice = IntPrompt.ask("\n>_ ", default=0, show_default=False, show_choices=False)
        
        if fork_choice == 1:
            run_reborn_process(user_input, stock_type)
            return
        elif fork_choice == 2:
            run_refresh_process()
            return
        else:
            return

    # Validating new stock...
    verified_ticker = verify_stock(user_input, stock_type)
    if not verified_ticker:
        return

    run_newborn_process(verified_ticker, stock_type, script_path)

# EXECUTE
# -------
def execute_script(script_path, disp_name):
    console.clear()
    console.print(f"[light_coral][bold]EXECUTING[/bold]: [bold steel_blue1]{disp_name}[/bold steel_blue1]...[/light_coral]\n")
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TimeElapsedColumn()) as progress:
        task = progress.add_task("[navajo_white1]Running...[/navajo_white1]", total=5)
        for _ in range(5):
            time.sleep(0.5)
            progress.update(task, advance=1)
    if script_path.suffix == '.py':
        subprocess.run([sys.executable, str(script_path)])
    else:
        subprocess.run(["bash", str(script_path)])
    input("\nPress Enter to return...")

# DISPLAY FILE INFO
# -----------------
def show_info(script_file, script_path, wiki):
    disp_name = get_disp_name(script_file)
    raw_file = wiki.get("DIRECTORY_STRUCTURE.SCRIPTS", {}).get(script_file, "\nNo description available.\n")
    raw_file_owner = wiki.get("DIRECTORY_STRUCTURE", {}).get("SCRIPTS", {}).get(script_file, {}).get("OWNER", {})
    raw_file_usage = wiki.get("DIRECTORY_STRUCTURE", {}).get("SCRIPTS", {}).get(script_file, {}).get("USAGE", {})
    raw_file_about = wiki.get("DIRECTORY_STRUCTURE", {}).get("SCRIPTS", {}).get(script_file, {}).get("ABOUT", {})
    raw_file_version = wiki.get("DIRECTORY_STRUCTURE", {}).get("SCRIPTS", {}).get(script_file, {}).get("VERSION", {})
    stat = script_path.stat()
    size_kb = stat.st_size / 1024
    mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
    console.clear(); show_banner()
    console.print(f"[misty_rose1][bold]///[light_slate_grey]MAIN[/light_slate_grey]//[light_slate_grey]{disp_name.upper()}[/light_slate_grey]//C:DOCUMENTATION/>[/bold][light_steel_blue1]cat wiki.json[/light_steel_blue1][bold]_[/bold][/misty_rose1]\n")
    console.print(f"[khaki3]FILE: [/khaki3][bold bright_white]{script_file}[/bold bright_white]\n\n[khaki3]SIZE: [/khaki3][bold medium_spring_green]{size_kb:.2f}[/bold medium_spring_green][dim] KB[/dim]\n[khaki3]LAST MODIFIED: [/khaki3][bold medium_spring_green]{mod_time}[/bold medium_spring_green]")
    console.print(f"\n[khaki3]METADATA: [/khaki3]\n[plum1]• Owner: [/plum1][bold light_cyan]{raw_file_owner}[/bold light_cyan]\n[plum1]• USAGE: [/plum1][bold light_cyan]{raw_file_usage}[/bold light_cyan]\n[plum1]• VERSION: [/plum1][bold spring_green]{raw_file_version}[/bold spring_green]\n\n[khaki3]DESCRIPTION: [/khaki3][light_cyan1]{raw_file_about}[/light_cyan1]")
    input("\nPress Enter to return...")

# MAIN
# ----
if __name__ == "__main__":
    try:
        # main_menu()
        intro_page()
    except KeyboardInterrupt:
        console.print("\n[indian_red1]Goodbye![/indian_red1]")
