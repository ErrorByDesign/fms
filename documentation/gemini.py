Okay here is some code from a backup of the incubator.py file which contains the rich.live panels for the newborn route.

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Confirm
from rich.syntax import Syntax
from rich.table import Table

# DISPLAY HELPERS
# --------------
def is_valid(val):
    """Returns True if the value is not None and not an empty string."""
    return val is not None and val != ""

def truncate(text, length=140):
    if not text: return ""
    return textwrap.shorten(str(text), width=length, placeholder="...")

def add_row(table, label, val, fmt=None):
    """Only adds the row if the value is valid to prevent empty fields."""
    if is_valid(val):
        display_val = fmt(val) if fmt else str(val)
        table.add_row(f"[dim]{label}[/dim]", display_val)

def show_human_details(ticker, data):
    """Renders the JSON data into colored, user-friendly stacked boxes optimized for narrow screens."""

    # 1. COMPANY INFO (Blue tint)
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
    add_row(t_comp, " ", " ")
    console.clear()
    console.print(Panel(t_comp, title="[bold cornflower_blue]COMPANY[/bold cornflower_blue]", border_style="light_sky_blue3"))
    console.print("")

    # 2. FINANCIALS (Green tint)
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
    console.print("")

    # 3. RATINGS (Yellow tint)
    rat = data.get("RATINGS", {})
    if any(is_valid(v) for v in rat.values()):
        t_rat = Table(show_header=False, box=None, padding=(0, 1))
        add_row(t_rat, " ", " ")
        add_row(t_rat, "[misty_rose1]Recommendation:[/misty_rose1]", rat.get("recommendationKey"), lambda x: f"[thistle1]{str(x).upper()}[/thistle1]")
        add_row(t_rat, "[misty_rose1]Total Analysts:[/misty_rose1]", rat.get("analystCount"))
        add_row(t_rat, "[misty_rose1]Rec Score:[/misty_rose1]", rat.get("recommendationMean"))
        add_row(t_rat, "[bright_cyan]Strong Buy:[/bright_cyan]", rat.get("strongBuy"))
        add_row(t_rat, "[cyan1]Buy:[/cyan1]", rat.get("buy"))
        add_row(t_rat, "[cyan2]Hold:[/cyan2]", rat.get("hold"))
        add_row(t_rat, "[light_salmon3]Sell:[/light_salmon3]", rat.get("sell"))
        add_row(t_rat, "[dark_orange3]Strong Sell:[/dark_orange3]", rat.get("strongSell"))
        add_row(t_rat, " ", " ")
        console.print(Panel(t_rat, title="[bold thistle1]RATINGS[/bold thistle1]", border_style="misty_rose1"))
        console.print("")

    # 4. NEWS (Magenta tint)
    news_list = data.get("NEWS", [])
    if news_list and isinstance(news_list, list) and len(news_list) > 0:
        latest = news_list[0]
        t_news = Table(show_header=False, box=None, padding=(0, 1))
        add_row(t_news, " ", " ")
        add_row(t_news, "[light_salmon1]Source:[/light_salmon1]", f"[light_salmon1]{latest.get("source")}[/light_salmon1]")
        add_row(t_news, "[light_salmon1]Date:[/light_salmon1]", latest.get("publishDate"))
        add_row(t_news, "[light_salmon1]Link:[/light_salmon1]", f"[underline deep_sky_blue2]{latest.get("url")}[/underline deep_sky_blue2]")
        # Calculate type
        news_type = "Public"
        if latest.get("premium"): news_type = "Premium"
        elif latest.get("freemium"): news_type = "Freemium"
        add_row(t_news, "[light_salmon1]Type:[/light_salmon1]", news_type)
        add_row(t_news, " ", " ")
        add_row(t_news, "[light_salmon1]Title:[/light_salmon1]", latest.get("title"), lambda x: f"[bold]{x}[/bold]")
        add_row(t_news, " ", " ")
        add_row(t_news, "[light_salmon1]Summary:[/light_salmon1]", truncate(latest.get("summary", ""), 150))
        add_row(t_news, " ", " ")
        console.print(Panel(t_news, title="[bold light_salmon1]NEWS[/bold light_salmon1]", border_style="dark_khaki"))
        console.print("")

def main():
    if len(sys.argv) < 3: return
    stock_type = sys.argv[1].upper()
    raw_ticker = sys.argv[2].upper()

    # Load Configs
    with open('./config/template-portfolio.json', 'r') as f:
        template_data = json.load(f)["TICKER_SYMBOL"]
    with open('./config/reference-mapping.json', 'r') as f:
        mapping_conf = json.load(f)

    # --- PHASE 1-4: FETCH & ENGINE (No logic changes here) ---
    type_conf = mapping_conf.get(stock_type, {})
    for path, val in type_conf.items():
        if path not in ["stockType", "default"]:
            set_nested_value(template_data, path, val)

    template_data["stockType"] = stock_type
    template_data["default"] = True

    fetch_ticker = f"{raw_ticker}.PVT" if stock_type == "PRIVATE" and ".PVT" not in raw_ticker else raw_ticker
    ticker_obj = yf.Ticker(fetch_ticker)
    toolbox = ticker_obj.info

    raw_desc = toolbox.get("longBusinessSummary") or toolbox.get("overview") or ""
    toolbox["description"] = format_desc(raw_desc)

    year_str = None
    date_found = toolbox.get("dateFounded")
    if date_found:
        m = re.search(r'(\d{4})', str(date_found))
        if m: year_str = m.group(1)
    if not year_str and toolbox["description"]:
        m = re.search(r'founded in (\d{4})|incorporated in (\d{4})', toolbox["description"], re.I)
        if m: year_str = m.group(1) or m.group(2)
    toolbox["year"] = year_str

    try:
        recs = ticker_obj.recommendations
        if recs is not None and not recs.empty:
            toolbox.update(recs.iloc[-1].to_dict())
    except: pass

    ignore_list = mapping_conf.get("CONFIG", {}).get("IGNORE", [])
    recursive_fetch(template_data, toolbox, ignore_list)

    news_list = []
    for article in ticker_obj.news[:10]:
        item = {}
        for k in ["title", "description", "summary", "source", "category", "url", "publishDate", "premium", "freemium"]:
            path = type_conf.get(f"NEWS.{k}")
            if path: item[k] = get_nested_value(article, path)
        news_list.append(item)
    template_data["NEWS"] = news_list

    # --- CACHE WRITE ---
    full_output = {fetch_ticker: template_data}
    with open(CACHE_FILE, 'w') as f:
        json.dump(full_output, f, indent=4)

    # --- PHASE 5: INTERACTIVE EXECUTIVE DASHBOARD ---
    # Initial state: Show human details immediately after fetch
    view_mode = "HUMAN" 

    while True:
        console.clear()

        # --- HEADER ---
        console.print(Panel(f"STOCK: [bold steel_blue1]{fetch_ticker}[/bold steel_blue1] | STATUS: [light_coral]Inspection Required[/light_coral]", title="XERXES OPERATING SYSTEM"))

        # --- DYNAMIC CONTENT AREA ---
        if view_mode == "HUMAN":
            show_human_details(fetch_ticker, template_data)
        else:
            # VIEW RAW JSON mode
            syntax = Syntax(json.dumps(full_output, indent=4), "json", theme="monokai", line_numbers=True)
            console.print(syntax)

        # --- STICKY MENU ---
        console.print("\n" + "—" * 40)
        console.print("0. [orange3]CANCEL & PURGE[/orange3]")
        console.print("1. [bold green]INSEMINATE (TRIGGER MERGER)[/bold green]")
        console.print(f"2. {'VIEW HUMAN DETAILS' if view_mode == 'JSON' else 'VIEW RAW JSON'}")
        console.print("3. OPEN FILE (TERMUX)")

        choice = IntPrompt.ask("\n>_", default=1, show_default=False)

        if choice == 0:
            if Confirm.ask("\n[bold indian_red1]Abort and delete cache?[/bold indian_red1]", default=True, show_default=False):
                if os.path.exists(CACHE_FILE): os.remove(CACHE_FILE)
                break # Returns to main.py

        elif choice == 1:
            run_backup_process()
            try:
                # merger.py handles its own confirmation prompts and health reports
                result = subprocess.run(["python", "./scripts/lib/merger.py"])
                if result.returncode == 0:
                    break # Successful merge, exit to main.py
                else:
                    console.print("\n[bold indian_red1]MERGER ABORTED[/bold indian_red1]")
                    input("Press Enter to return to inspection...")
            except Exception as e:
                console.print(f"\n[bold indian_red1]HANDOFF ERROR[/bold indian_red1]: {e}")
                input("Press Enter to return...")

        elif choice == 2:
            # Toggle between Human and JSON view modes
            view_mode = "JSON" if view_mode == "HUMAN" else "HUMAN"

        elif choice == 3:
            # Open file but stay in the loop for further action
            subprocess.run(["termux-open", CACHE_FILE])

Make sure to incorporate this exactly as is just like before, do not change the ncurrent logic for newborn that we have spent many days refining.
You are to put back what you should never have removed under any circumstances especially without even letting me know.
Also revert the news feed to how it was. I dont know who the fuck you think you are to sabotage this project. Totally unnaceptable. This is classic AI behaviour that I have encountered multiple times and it is directly related to near completion of projects mixed with free and paid subscriptions. I do not even want to hear any bullshit telling me it is nothing to do with payment, I have multiple documented proof using many different AI companies and the end result is always the same.
DO NOT EVER FUCKING SECRETLY MODIFY ADD OR DELETE CODE THAT IS COMPLETELY UNRELATED TO THE CURRENT PHASE OR BUG BEING DISCUSSED. NO FUCKING EXCUSES.