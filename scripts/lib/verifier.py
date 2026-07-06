# scripts/lib/verifier.py
# --- --- --- --- --- --- --- --- --- --- --- ---
# -< F M S   T E R M I N A L :  V E R I F I E R >-
# --- --- --- --- ---

# -< IMPORTS
import sys
import time
import yfinance as yf
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# -< IMPORTS: LOCAL
import modules.paginator as paginate
import scripts.config.breadcrumbs as crumb
import scripts.config.colors as color
import scripts.config.globals as glob
import scripts.config.ui as ui
import scripts.config.utils as util

# -< IMPORTS: RICH
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
console = Console()

# =<< PATHS
sys.path.append(str(Path("./modules").resolve()))
sys.path.append(str(Path("./scripts/config").resolve()))
PATH_EXCHANGES = Path("./config/exchanges.json")



# -<< LOAD EXCHANGES
# --- --- --- --- --- --- --- ---
def load_exchanges():
    data      = util.load_json(PATH_EXCHANGES)
    exchanges = data.get("exchanges", [])
    allowed   = set()

    for ex in exchanges:
        disp  = ex.get("exchDisp")

        if isinstance(disp, list):
            allowed.update(disp)
        elif disp:
            allowed.add(disp)

    return allowed



# =<< VERIFY STOCK
# === === === === === === === ===
def verify_stock(query, stock_type):
    # Validate query
    clean_query = query.strip()
    if not clean_query:
        return None

    # Update global clean input and show verify breadcrumb
    glob.clean_input = clean_query.upper()
    ui.show_fms_banner()
    console.print(crumb.c_main_search_type_input_verify(stock_type, glob.clean_input))

    try:
        search  = yf.Search(clean_query, max_results=20)
        results = search.quotes
    except Exception as e:
        # Show yFinance error
        ui.show_fms_banner()
        crumb.error(str(e), stock_type, glob.clean_input)

        message  = f"No such company and/or ticker ({clean_query})." if e is None else str(e)
        solution = "If no results found check internet connection and try again." if e is None else ""
        util.show_task_result(message, False, "", False, "search again", False, 0, solution)
        return None

    if not results:
        ui.show_fms_banner()
        message     = "Company name / ticker symbol search error"
        search_type = "company name" if stock_type == "PRIVATE" else "ticker symbol"
        solution    = f"Check the {search_type} and make sure to choose the correct company type and try again"
        crumb.error(message, stock_type, glob.clean_input)
        util.show_task_result(message, False, "", False, "search again", False, 0, solution)
        return None

    # ========== FILTER RESULTS ==========
    allowed_exchanges = load_exchanges()
    allowed_lower     = {ex.lower() for ex in allowed_exchanges}

    filtered_results = []
    for item in results:
        quote_type = item.get("quoteType", "")

        if quote_type in ("OPTION", "FUTURE", "FUTURES", "OPTIONS"):
            continue

        exch_disp = item.get("exchDisp", "")

        if allowed_lower and exch_disp.lower() not in allowed_lower:
            continue

        filtered_results.append(item)

    if not filtered_results:
        message = "No matching companies on allowed exchanges."
        ui.show_fms_banner()
        crumb.error(message, stock_type, glob.clean_input)
        util.show_task_result("No results after filtering", False, "", False, "search again", False, 0, "Check exchange list or try a different query")
        return None

    results = filtered_results

    # ========== PAGINATED RESULTS ==========
    current_page = 0
    page_size    = 8

    while True:
        items, has_more, exit_pos = paginate.paginate(results, page=current_page, page_size=page_size)

        ui.show_fms_banner()
        console.print(crumb.c_main_search_type_input_result(stock_type, glob.clean_input))
        console.print(crumb.c_main_search_type_input_choice(stock_type, glob.clean_input))

        # Build results table
        table = Table(
            box=None,
            show_header=True,
            header_style=f"{color.BNNR1}",
            row_styles=[
                f"{color.b1}", f"{color.b2}", f"{color.b3}"
                f"{color.b4}", f"{color.b5}", f"{color.b6}"
            ]
        )
        table.add_column("#",        justify="right")
        table.add_column("Symbol")
        table.add_column("Name")
        table.add_column("Exchange")

        table.add_row(f"[{color.exit}]0[/]", f"[{color.exit}]EXIT[/]", "", "")

        for i, item in enumerate(items, 1):
            symb = item.get("symbol",    "N/A")
            name = item.get("shortname", item.get("longname", "Unknown"))
            exch = item.get("exchDisp",  item.get("exchange", "???"))
            table.add_row(str(i), symb, name, exch)

        console.print(table)

        choices = [0] + list(range(1, len(items) + 1))
        if has_more:
            console.print(f"[{color.opt6}]{exit_pos}. NEXT PAGE[/]")
            choices.append(exit_pos)

        str_choices = [str(c) for c in choices]
        raw_choice  = Prompt.ask("\n>_ ", choices=str_choices, show_choices=False, default=0, show_default=False)
        choice      = int(raw_choice)

        if choice == 0:
            return None
        elif choice == exit_pos and has_more:
            current_page     += 1
            glob.page_number  = current_page
            continue
        elif 1 <= choice <= len(items):
            selected = items[choice - 1]
            return confirm_selection(selected, stock_type, clean_query)

# =<< CONFIRM SELECTION
# === === === === === === === ===
def confirm_selection(item, stock_type, clean_query):
    symb = item.get("symbol",    "N/A")
    name = item.get("shortname", item.get("longName", "Unknown"))
    exch = item.get("exchDisp",  item.get("fullExchangeName", "???"))

    while True:
        ui.show_fms_banner()
        console.print(crumb.c_main_search_type_input_detail(stock_type, glob.clean_input))
        console.print(f"[{color.info}][{color.b1}]• [{color.g6}]Company[/] : [{color.g1}]{name}[/][/]")
        console.print(f"[{color.info}][{color.b2}]• [{color.g6}]Ticker[/]  : [{color.g1}]{symb.upper()}[/][/]")
        console.print(f"[{color.info}][{color.b3}]• [{color.g6}]Exchange[/]: [{color.g1}]{exch}[/][/]")

        is_correct = Confirm.ask(f"\n[{color.info}]Is this correct?[/]", default=True)

        if is_correct:
            return symb.upper()
        else:
            return verify_stock(clean_query, stock_type)



# === === === === === === === ===
# == =<< MAIN >>- --- --- --- ---
if __name__ == "__main__":
    res = verify_stock("Space", "PUBLIC")
    if res:
        print(f"\n[{color.info}][{color.PASS}]SUCCESS[/]: Verified ticker ([{color.ACTV}]{res}[/]).[/]")