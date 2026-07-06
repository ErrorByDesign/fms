# scripts/config/breadcrumbs.py

# -< IMPORTS: LOCAL
import scripts.config.colors as color

# -< IMPORTS: RICH
from rich.console import Console
console = Console()



# -<< STATIC CRUMBS
# --- --- --- --- --- --- --- ---
# BACKUP
c_backup              = f"[{color.crmb}]MAIN[/]//[{color.ACTV}]BACKUP[/]: [{color.info}]Initiating backup...[/]"
c_backup_prefresh     = f"[{color.crmb}]MAIN[/]//[{color.crmb}]UPDATE[/]: [{color.info}]Initiating [{color.ACTV}]prefresh[/] backup...[/]"
c_backup_preset       = f"[{color.crmb}]MAIN[/]//[{color.crmb}]CONFIG[/]//[{color.crmb}]SYS-RESET[/]: [{color.info}]Initiating [{color.ACTV}]preset[/] backup...[/]"
c_backup_preportfolio = f"[{color.crmb}]MAIN[/]//[{color.crmb}]CONFIG[/]//[{color.crmb}]PORTFOLIO[/]: [{color.info}]Initiating [{color.ACTV}]prefolio[/] backup...[/]"
c_backup_prestructure = f"[{color.crmb}]MAIN[/]//[{color.crmb}]CONFIG[/]//[{color.crmb}]STRUCTURE[/]: [{color.info}]Initiating [{color.ACTV}]prestructure[/] backup...[/]"

# INCUBATOR
c_incubator_reborn = f"[{color.crmb}]INCUBATOR[/]//[{color.crmb}]REBORN[/]: [{color.info}]Executing targeted update...[/]"

# MAIN
c_exit        = f"[{color.ACTV}]EXIT[/]//[{color.crmb}]MAIN[/]"
c_main        = f"[{color.ACTV}]MAIN[/]"
c_main_search = f"[{color.crmb}]MAIN[/]//[{color.ACTV}]SEARCH[/]"
c_main_update = f"[{color.crmb}]MAIN[/]//[{color.ACTV}]UPDATE[/]"
c_main_config = f"[{color.crmb}]MAIN[/]//[{color.ACTV}]CONFIG[/]"

# MAIN -> CONFIG
c_main_config_portfolio = f"[{color.crmb}]MAIN[/]//[{color.crmb}]CONFIG[/]//[{color.ACTV}]PORTFOLIO[/]"
c_main_config_structure = f"[{color.crmb}]MAIN[/]//[{color.crmb}]CONFIG[/]//[{color.ACTV}]STRUCTURE[/]"
c_main_config_sys_reset = f"[{color.crmb}]MAIN[/]//[{color.crmb}]CONFIG[/]//[{color.ACTV}]SYS-RESET[/]; [{color.info}]Resetting health metrics...[/]"

# MAIN -> SEARCH
c_main_search_type = f"[{color.crmb}]MAIN[/]//[{color.crmb}]SEARCH[/]//[{color.ACTV}]TYPE[/]"




# =<< DYNAMIC CRUMBS
# === === === === === === === ===
# BACKUP
def c_backup_preborn(stock_type, ticker):
    return f"[{color.crmb}]MAIN[/]//[{color.crmb}]SEARCH[/]//[{color.DONE}][{stock_type}[/]:[{color.DONE}]{ticker}][/]: [{color.info}]Initiating [{color.ACTV}]preborn[/] backup sequence...[/]"

# DASHBOARD
def c_dashboard(user_input):
    return f"[{color.crmb}]DASHBOARD[/]//[{color.ACTV}]{user_input}[/]: [{color.info}]DNA sequence[/]"

# =<< MAIN -> SEARCH
def c_main_script_info(script):
    return f"[{color.crmb}]MAIN[/]//[{color.crmb}]{script.upper()}[/]//[{color.ACTV}]INFO[/]: [{color.info}]Wikipedia[/]"

def c_main_search_type_input(stock_type):
    return f"[{color.crmb}]MAIN[/]//[{color.crmb}]SEARCH[/]//[[{color.DONE}]{stock_type}[/]:[{color.ACTV}]INPUT[/]]"

def c_main_search_type_input_reborn(stock_type, user_input):
    return f"[{color.crmb}]MAIN[/]//[{color.crmb}]SEARCH[/]//[[{color.WARN}]{stock_type}[/]:[{color.WARN}]{user_input}[/]]"

def c_main_search_type_input_verify(stock_type, user_input):
    return f"[{color.crmb}]MAIN[/]//[{color.crmb}]SEARCH[/]//[[{color.DONE}]{stock_type}[/]:[{color.DONE}]{user_input}[/]]//[{color.ACTV}]VERIFY[/]"

def c_main_search_type_input_result(stock_type, user_input):
    return f"[{color.crmb}]MAIN[/]//[{color.crmb}]SEARCH[/]//[[{color.DONE}]{stock_type}[/]:[{color.DONE}]{user_input}[/]]//[{color.ACTV}]RESULTS[/]:"

def c_main_search_type_input_detail(stock_type, user_input):
    return f"[{color.crmb}]MAIN[/]//[{color.crmb}]SEARCH[/]//[[{color.DONE}]{stock_type}[/]:[{color.DONE}]{user_input}[/]]//[{color.ACTV}]DETAILS[/]:"

def c_main_search_type_input_choice(stock_type, clean_input):
    return f"[{color.base}][{color.b6}]TYPE[/]: [{color.b1}]{stock_type}[/] | [{color.b5}]QUERY[/]: [{color.b2}]{clean_input}[/][/]\n"

# =<< MERGER -> INSEMINATE
def merger_inseminate_sequence(stock_type, ticker):
    return f"[{color.base}][{color.crmb}]MAIN[/]//[{color.crmb}]SEARCH[/]//[{color.crmb}]{stock_type}[/]:[{color.crmb}]{ticker}[/]//[{color.ACTV}]Raw DNA sequence[/].[/]\n"



# === === === === === === === ===
# =<< ERROR CRUMBS
def error(msg, stock_type="", user_input=""):
    error_crumb = f"[{color.crmb}]MAIN[/]//[{color.crmb}]SEARCH[/]//[[{color.DONE}]{stock_type}[/]:[{color.DONE}]{user_input}[/]]//[{color.ACTV}]VERIFY[/]//[{color.ERR}]ERROR[/]: [{color.FAIL}]{msg}[/]\n"
    console.print(error_crumb)