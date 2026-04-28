#!/usr/bin/env python3
# -----------------------------------------
# X E R X E S   S T O C K   V E R I F I E R
#------------
import random
import time
import sys
import yfinance as yf
from pathlib import Path
from rich.console import Console
from rich.prompt import IntPrompt, Prompt, Confirm
from rich.table import Table

from modules.paginator import paginate

sys.path.append(str(Path("./modules").resolve()))

console = Console()

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

# VERIFY
# ------
def verify_stock(query, stock_type):
    """
    Search yFinance for a company/ticker and return a confirmed symbol.
    """
    # 1. SANITIZE
    # Handle casing and whitespace gracefully
    clean_query = query.strip()
    if not clean_query:
        return None

    console.clear()
    show_banner()
    console.print(f"[misty_rose1][bold]///[light_slate_grey]MAIN[/light_slate_grey]//[light_slate_grey]SEARCH[/light_slate_grey]//[light_slate_grey]TYPE[/light_slate_grey]:[navajo_white1]{stock_type}[/navajo_white1]//[light_slate_grey]{"TICKER" if stock_type == "PUBLIC" else "COMPANY"}[/light_slate_grey]:[navajo_white1]{clean_query}[/navajo_white1]//C:>[/bold][light_steel_blue1]pkg search [bold honeydew2]{clean_query}[/bold honeydew2]...[/light_steel_blue1][bold]_[/bold][/misty_rose1]\n")

    # 2. FETCH RESULTS
    try:
        # yFinance search is case-insensitive, so we don't need to force upper/lower here
        search = yf.Search(clean_query, max_results=20)
        results = search.quotes
    except Exception as e:
        console.clear()
        show_banner()
        console.print(f"[misty_rose1][bold]///[light_slate_grey]MAIN[/light_slate_grey]//[light_slate_grey]SEARCH[/light_slate_grey]//[light_slate_grey]TYPE[/light_slate_grey]:[navajo_white1]{stock_type}[/navajo_white1]//[light_slate_grey]{"TICKER" if stock_type == "PUBLIC" else "COMPANY"}[/light_slate_grey]:[navajo_white1]{clean_query}[/navajo_white1]//C:>[/bold][bold indian_red1]Search Error:[/bold indian_red1][bold honeydew2]{e}[/bold honeydew2][/light_coral][bold]_[/bold][/misty_rose1]\n")
        time.sleep(5)
        return None

    if not results:
        console.clear()
        show_banner()
        console.print(f"[misty_rose1][bold]///[light_slate_grey]MAIN[/light_slate_grey]//[light_slate_grey]SEARCH[/light_slate_grey]//[light_slate_grey]TYPE[/light_slate_grey]:[navajo_white1]{stock_type}[/navajo_white1]//[light_slate_grey]{"TICKER" if stock_type == "PUBLIC" else "COMPANY"}[/light_slate_grey]:[navajo_white1]{clean_query}[/navajo_white1]//C:>[/bold][light_coral]Failed to fetch [bold honeydew2]{clean_query}[/bold honeydew2][/light_coral]: No such ticker or company[bold]_[/bold][/misty_rose1]\n")
        time.sleep(5)
        return None

    # 3. PAGINATION LOOP
    current_page = 0
    page_size = 8 # Optimized for mobile (OriginOS/Termux)
    
    while True:
        items, has_more, exit_pos = paginate(results, page=current_page, page_size=page_size)
        
        console.clear()
        show_banner()
        console.print(f"[misty_rose1][bold]///[light_slate_grey]MAIN[/light_slate_grey]//[light_slate_grey]SEARCH[/light_slate_grey]//[light_slate_grey]TYPE[/light_slate_grey]:[navajo_white1]{stock_type}[/navajo_white1]//[light_slate_grey]{"TICKER" if stock_type == "PUBLIC" else "COMPANY"}[/light_slate_grey]:[navajo_white1]{clean_query}[/navajo_white1]//C:>[/bold][light_steel_blue1]ls | grep '[bold honeydew2]{clean_query}[/bold honeydew2]'[/light_steel_blue1]\\..*\\..*[bold]_[/bold][/misty_rose1]\n")
        console.print(f"[dim]TYPE: [bold light_coral]{stock_type}[/bold light_coral] | QUERY: [bold steel_blue1]{clean_query.upper()}[/bold steel_blue1][/dim]\n")

        # UI Table
        table = Table(box=None, show_header=True, header_style="bold yellow")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Symbol", style="bold white")
        table.add_column("Name", style="spring_green1")
        table.add_column("Exch", style="dim")
        
        table.add_row("0", "CANCEL", "", "")
        
        for i, item in enumerate(items, 1):
            symbol = item.get("symbol", "N/A")
            name = item.get("shortname", item.get("longname", "Unknown"))
            exch = item.get("exchDisp", item.get("exchange", "???"))
            table.add_row(str(i), symbol, name, exch)

        console.print(table)
        
        # Build choices using your Paginator's exit_pos
        choices = [0] + list(range(1, len(items) + 1))
        if has_more:
            console.print(f"[bold yellow]{exit_pos}. NEXT PAGE[/bold yellow]")
            choices.append(exit_pos)
            
        # Convert choices to strings for the Prompt to handle them correctly
        str_choices = [str(c) for c in choices]
        
        raw_choice = Prompt.ask("\n>_ ", choices=str_choices, show_choices=False, default=0, show_default=False)
        
        # Now we know it's a valid string choice, convert back to int
        choice = int(raw_choice)

        if choice == 0:
            return None
        elif choice == exit_pos and has_more:
            current_page += 1
            continue
        elif 1 <= choice <= len(items):
            selected = items[choice - 1]
            return _confirm_selection(selected, stock_type, clean_query)

# CONFIRM
# -------
def _confirm_selection(item, stock_type, clean_query):
    """
    Internal helper for final confirmation as per requirements.
    """
    symbol = item.get("symbol", "N/A")
    name   = item.get("shortname", item.get("longName", "Unknown"))
    exch   = item.get("exchDisp", item.get("fullExchangeName", "???"))
    
    console.print(f"[misty_rose1][bold]///[light_slate_grey]MAIN[/light_slate_grey]//[light_slate_grey]SEARCH[/light_slate_grey]//[light_slate_grey]TYPE[/light_slate_grey]:[navajo_white1]{stock_type}[/navajo_white1]//[light_slate_grey]{"TICKER" if stock_type == "PUBLIC" else "COMPANY"}[/light_slate_grey]:[navajo_white1]{clean_query}[/navajo_white1]//C:>[/bold][light_steel_blue1]Confirm Selection:[/light_steel_blue1][/misty_rose1]\n")
    console.print(f"[plum1]• Company: [/plum1][bold cyan]{name}[/bold cyan]")
    console.print(f"[plum1]• Ticker:  [/plum1][bold steel_blue1]{symbol.upper()}[/bold steel_blue1]")
    console.print(f"[plum1]• Exchange: [/plum1][dim]{exch}[/dim]")
    
    # Final verification gate
    is_correct = Confirm.ask("\nIs this correct?", default=True)
    
    # Ensure the ticker is upper-cased before returning to main/incubator
    return symbol.upper() if is_correct else None

# MODULE GATE
if __name__ == "__main__":
    # Test block
    res = verify_stock("Space", "PUBLIC")
    if res:
        print(f"\n[SUCCESS] Verified Ticker: {res}")
