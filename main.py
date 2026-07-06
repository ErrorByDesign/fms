#!/usr/bin/env python3
# === === === === === === === === === === === === ===
# =<< F M S   T E R M I N A L :   M A I N • p y
# === === === === ===

# -< IMPORTS
import os
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# -< IMPORTS: LOCAL
import config.devops as dev
import scripts.config.breadcrumbs as crumb
import scripts.config.colors as color
import scripts.config.globals as glob
import scripts.config.introduction as intro
import scripts.config.input as inp
import scripts.config.ui as ui
import scripts.config.utils as util
import scripts.lib.structure as struct
import scripts.lib.verifier as verify

# -< IMPORTS: RICH
from rich.console import Console
from rich.prompt import IntPrompt, Confirm
console = Console()

# =<< PATHS
PATH_INCUBATOR  = Path("./scripts/incubator.py")
PATH_MERGER     = Path("./scripts/lib/merger.py")
PATH_OPERATIONS = Path("./modules/operations.py")
PATH_PORTFOLIO  = Path("./data/portfolio.json")
PATH_WIKI       = Path("./documentation/wiki.json")

# =<< GLOBALS
def debug_arg():
    return ["--debug"] if dev.debug == True else []



# -<< UTILITIES
# --- --- --- --- ---
def exit_app():
    while True:
        ui.show_menu(
            breadcrumb=crumb.c_exit,
            options=[
                ("Y", "EXIT",   color.exit),
                ("1", "SEARCH", color.mute),
                ("2", "UPDATE", color.mute),
                ("3", "CONFIG", color.mute),
            ],
            choice=False
        )
        if Confirm.ask(f"\n[{color.DOS}] »[/] [{color.back}]Exit program?[/]", default=True, show_default=False):
            console.print(f"\n[{color.DONE}]Goodbye![/]\n")
            sys.exit()
        else:
            console.print("")
            main()

def cover():
    intro.welcome_page()
    input()
    main()

def load_wiki():
    return util.load_json(PATH_WIKI) or {"DIRECTORY_STRUCTURE.SCRIPTS": {}}

def wip_menu():
    console.print(f"\n[{color.WARN}] ⚠ TO BE IMPLEMENTED[/]")
    time.sleep(3)



# -<< PROCESSES: Portfolio
# --- --- --- --- --- --- --- ---
def run_backup_process(origin="", stock_type="", ticker=""):
    # Define origin of backup call
    if origin == "":
        bc = crumb.c_backup
        ops = []
    elif origin in ("--newborn", "--reborn"):
        bc = crumb.c_backup_preborn(stock_type, ticker)
        ops = [
            ("0", "BACK",    color.mute),
            ("1", "EXECUTE", color.mute),
            ("2", "INFO",    color.mute),
        ]
    elif origin == "--refresh":
        bc = crumb.c_backup_prefresh
        ops = [
            ("0", "BACK",    color.mute),
            ("1", "EXECUTE", color.mute),
            ("2", "INFO",    color.mute),            
        ]
    elif origin == "--reset":
        bc = crumb.c_backup_preset
        ops = [
            ("0", "BACK",      color.mute),
            ("1", "PORTFOLIO", color.mute),
            ("2", "STRUCTURE", color.mute),
            ("3", "SYS-RESET", color.mute),
        ]
    elif origin == "--restructure":
        bc = crumb.c_backup_prestructure
        ops = [
            ("0", "BACK",     color.mute),
            ("1", "ADD KEYS", color.mute),
            ("2", "DEL KEYS", color.mute),
            ("3", "MOD KEYS", color.mute),
        ]
    elif origin == "--reportfolio":
        bc = crumb.c_backup_preportfolio
        ops = [
            ("0", "BACK", color.mute),
            ("1", "TCKR", color.mute),
            ("2", "TCKR", color.mute),
        ]
    else:
        bc = crumb.c_backup
        ops = []

    # Determine developer mode state
    dev_msg = f"[{color.info}][{color.WARN}]Developer mode enabled[/]. Skipping backup.[/]\n" if dev.debug == True else "\n "

    # Display temporary diabled menu
    ui.show_menu(breadcrumb=bc, options=ops, instruction = dev_msg, choice = False)
    if dev.debug == True:
        util.wait_spinner()
    else:
        subprocess.run([sys.executable, PATH_OPERATIONS, "--backup"])

def run_newborn_process(ticker, stock_type):
    run_backup_process("--newborn", stock_type, ticker)
    subprocess.run([sys.executable, str(PATH_INCUBATOR), stock_type, ticker, "--newborn"] + debug_arg())

def run_reborn_process(ticker, stock_type):
    run_backup_process("--reborn", stock_type, ticker)
    subprocess.run([sys.executable, str(PATH_INCUBATOR), stock_type, ticker, "--reborn"] + debug_arg())

def run_refresh_process():
    run_backup_process("--refresh")
    subprocess.run([sys.executable, str(PATH_INCUBATOR), "--refresh"] + debug_arg())

def run_reset_process():
    run_backup_process("--reset")
    subprocess.run([sys.executable, str(PATH_MERGER), "--reset"] + debug_arg())

# -<< PROCESSES: Structure
# --- --- --- --- --- --- --- ---
def run_addkeys_process():
    run_backup_process("--restructure")
    struct.structure_add_menu()

def run_delkeys_process():
    run_backup_process("--restructure")
    wip_menu()

def run_modkeys_process():
    run_backup_process("--restructure")
    wip_menu()



# =<< MENU: MAIN -> CONFIG -> PORTFOLIO -> TICKER
# === === === === === === === === === === === ===
def main_config_portfolio_ticker():
    wip_menu()

# =<< MENU: MAIN -> CONFIG -> PORTFOLIO
# === === === === === === === === ===
def main_config_portfolio():
    while True:
        choice = ui.show_menu(
            breadcrumb=crumb.c_main_config_portfolio,
            options=[
                ("0", "BACK", color.back),
                ("1", "TCKR", color.opt1),
                ("2", "TCKR", color.opt2),
            ],
            choice=True,
            prompt="X"
        )
        if choice == 0:
            return
        elif choice in (1, 2):
            main_config_portfolio_ticker()

# =<< MENU: MAIN -> CONFIG -> STRUCTURE
# === === === === === === === === ===
def main_config_structure():
    while True:
        choice = ui.show_menu(
            breadcrumb=crumb.c_main_config_structure,
            options=[
                ("0", "BACK",     color.back),
                ("1", "ADD KEYS", color.opt3),
                ("2", "DEL KEYS", color.opt6),
                ("3", "MOD KEYS", color.opt4),
            ],
            choice=True,
            prompt="X"
        )
        if choice == 0:
            return
        elif choice == 1:
            run_addkeys_process()
        elif choice == 2:
            run_delkeys_process()
        elif choice == 3:
            run_modkeys_process()

# =<< MENU: MAIN -> CONFIG
# === === === === === ===
def main_config():
    while True:
        choice = ui.show_menu(
            breadcrumb=crumb.c_main_config,
            options=[
                ("0", "BACK",      color.back),
                ("1", "PORTFOLIO", color.opt4),
                ("2", "STRUCTURE", color.opt5),
                ("3", "SYS-RESET", color.opt6),
            ],
            prompt="x"
        )
        if choice == 0:
            return
        elif choice == 1:
            main_config_portfolio()
        elif choice == 2:
            main_config_structure()
        elif choice == 3:
            run_reset_process()

# =<< MENU: MAIN
# === === === ===
def main():
    wiki = load_wiki()
    while True:
        choice = ui.show_menu(
            breadcrumb=crumb.c_main,
            options=[
                ("0", "EXIT",   color.exit),
                ("1", "SEARCH", color.opt1),
                ("2", "UPDATE", color.opt2),
                ("3", "CONFIG", color.opt3),
            ],
            instruction="",
            choice=True,
            prompt="f"
        )
        if choice == 0:
            exit_app()
        elif choice in (1, 2):
            script = "search" if choice == 1 else "update"
            main_script(script, wiki)
        elif choice == 3:
            main_config()

# =<< MENU: MAIN -> SCRIPT
# === === === === === ===
def main_script(script, wiki):
    while True:
        choice = ui.show_menu(
            breadcrumb=crumb.c_main_search if script == "search" else crumb.c_main_update,
            options=[
                ("0", "BACK",    color.back),
                ("1", "EXECUTE", color.opt1),
                ("2", "INFO",    color.opt2),
            ],
            choice=True,
            prompt="f"
        )
        if choice == 0:
            return
        elif choice == 1:
            if script == "search":
                main_search_type()
            else:
                run_refresh_process()
        elif choice == 2:
            main_script_info(script, wiki)

# =<< MENU: MAIN -> SCRIPT -> INFO
# === === === === === === === ===
def main_script_info(script, wiki):
    while True:
        choice = ui.show_menu(
            breadcrumb=crumb.c_main_script_info(script),
            options=[
                ("0", "BACK",    color.back),
                ("1", "EXECUTE", color.opt1),
                ("2", "INFO",    color.mute),
            ],
            choice=True,
            prompt="fms"
        )
        console.print(ui.wiki_panel(script, wiki))
        # choice = IntPrompt.ask(f"\n[{color.DOS}] ›[/]", default=0, show_default=False, show_choices=False)
        console.print("")
        if choice == 0:
            return
        elif choice == 1:
            if script == "search":
                main_search_type()
            else:
                run_refresh_process()
            return

# =<< MENU: MAIN -> SEARCH -> TYPE
# === === === === === === === ===
def main_search_type():
    # --- Step 1: choose stock type ---
    while True:
        choice = ui.show_menu(
            breadcrumb=crumb.c_main_search_type,
            options=[
                ("0", "BACK",    color.back),
                ("1", "PRIVATE", color.opt1),
                ("2", "PUBLIC",  color.opt2),
            ],
            choice=True,
            prompt="x"
        )
        if choice == 0:
            return
        elif choice in (1, 2):
            break

    glob.stock_type = "PRIVATE" if choice == 1 else "PUBLIC"
    color_prv    = color.ACTV if glob.stock_type == "PRIVATE" else color.mute
    color_plc    = color.ACTV if glob.stock_type == "PUBLIC"  else color.mute

    # --- Step 2: get ticker/company input ---
    ui.show_menu(
        breadcrumb=crumb.c_main_search_type_input(glob.stock_type),
        options=[
            ("0", "BACK",    color.back),
            ("1", f"[{color_prv}]PRIVATE[/]", color.mute),
            ("2", f"[{color_plc}]PUBLIC[/]",  color.mute),
        ],
        choice=False
    )
    user_input = inp.input_field(caller="search", stock_type=glob.stock_type)
    if user_input == "0" or not user_input:
        return
    glob.user_input = user_input

    # --- Step 3: check if already in portfolio ---
    portfolio = util.load_json(PATH_PORTFOLIO)
    if user_input in portfolio:
        choice = ui.show_menu(
            breadcrumb=crumb.c_main_search_type_input_reborn(glob.stock_type, user_input),
            options=[
                ("0", "BACK",          color.back),
                ("1", "SINGLE UPDATE", color.r1),
                ("2", "TOTAL REFRESH", color.r2),
            ],
            choice=True,
            prompt="x"
        )
        if choice == 1:
            run_reborn_process(user_input, glob.stock_type)
        elif choice == 2:
            run_refresh_process()
        return

    # --- Step 4: verify and add new stock ---
    verified_ticker = verify.verify_stock(user_input, glob.stock_type)
    if not verified_ticker:
        return
    run_newborn_process(verified_ticker, glob.stock_type)



# === === === === === === === ===
# == =<< MAIN >>- --- --- --- ---
if __name__ == "__main__":
    dev.debug = "--debug" in sys.argv
    try:
        if dev.debug == True:
            main()
        else:
            cover()
    except KeyboardInterrupt:
        console.print(f"\n[{color.info}][{color.WARN}]KEYBOARD INTERRUPT[/]: Goodbye![/]\n")