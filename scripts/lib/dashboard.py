# scripts/config/dashboard.py
# -- --- --- --- --- --- --- --- --- --- --- --- --
# =<< F M S   T E R M I N A L :  D A S H B O A R D
# --- --- --- --- ---

# -< IMPORTS
import sys
import termios
import textwrap
import tty

# -< IMPORTS: LOCAL MODULES
import scripts.config.breadcrumbs as crumb
import scripts.config.colors as color
import scripts.config.ui as ui
import scripts.config.utils as util

# -< IMPORTS: RICH
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
console = Console()



# -<< PANEL RENDERERS
# --- --- --- --- --- --- --- ---
def render_company_panel(data, stock_type):
    comp = data.get("COMPANY", {})
    website = comp.get("website")

    t = Table(show_header=True, box=box.ROUNDED, padding=(0, 1))
    t.add_column("OVERVIEW", header_style=f"{color.BNNR1}", style=f"{color.bnnr1}")
    t.add_column("DETAILS",  header_style=f"{color.BNNR3}",  style=f"{color.bnnr3}")
    
    util.add_row(t, " ", " ")
    util.add_row(t, f"Name[{color.base}][/]:[/]",     comp.get("name"))     # lambda x: f"[{color.bnnr1}]{x}[/]")
    util.add_row(t, f"Name[{color.base}]x[/]:[/]",    comp.get("exchange")) # lambda x: f"[{color.bnnr1}]{x}[/]")
    util.add_row(t, f"Industry[{color.base}][/]:[/]", comp.get("industry")) # lambda x: f"[{color.bnnr2}]{x}[/]")
    util.add_row(t, f"Sector[{color.base}][/]:[/]",   comp.get("sector"))   # lambda x: f"[{color.bnnr3}]{x}[/]")
    util.add_row(t, f"Country[{color.base}][/]:[/]",  comp.get("country"))  # lambda x: f"[{color.bnnr4}]{x}[/]")
    if website:
        website_cell = f"[link={website}]{website}[/link]"
    else:
        website_cell = "N/A"
    util.add_row(t, f"Website[{color.base}][/]:[/]", website_cell), lambda x: f"[{color.link}]{x}[/]")
    util.add_row(t, f"Year[{color.base}][/]:[/]",    comp.get("year"))  # lambda x: f"[{color.bnnr6}]{x}[/]")
    if stock_type == "PRIVATE":
        facts = comp.get("facts", [])
        if facts:
            fact = facts[0]
            util.add_row(t, f"Key Facts[{color.base}][/]:[/]", util.truncate(fact, 180), lambda x: f"[{color.info}]{x}[/]")
    util.add_row(t, " ", " ")
    util.add_row(t, f"Description[{color.base}][/]:[/]", util.truncate(comp.get("pseudoDescription", ""), 180), lambda x: f"[{color.info}]{x}[/]")
    util.add_row(t, " ", " ")
    return Panel(t, title=f"[{color.BNNR1}]COMPANY[/]", border_style=f"{color.bnrd1}", style=f"on {color.bnnr1x}")

def render_finance_panel(data, stock_type):
    fin = data.get("FINANCE", {})
    t = Table(show_header=True, box=box.ROUNDED, padding=(0, 1))
    t.add_column("FINANCIALS")
    t.add_column("DETAILS")
    util.add_row(t, " ", " ")
    util.add_row(t, f"[{color.base}][{color.bnnr2}]Market Price[/]:[/]", data.get("price"), lambda x: f"[{color.bnnr2x}]${float(x):,.2f}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr2}]Percentage Change[/]:[/]", fin.get("change"), lambda x: f"[{color.g2}]{x}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr2}]Market Cap[/]:[/]", fin.get("marketCap"), lambda x: f"[{color.g3}]${int(x):,}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr2}]52 Week Low[/]:[/]", fin.get("weekLow"), lambda x: f"[{color.g4}]${float(x):,.2f}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr2}]52 Week High[/]:[/]", fin.get("weekHigh"), lambda x: f"[{color.g5}]${float(x):,.2f}[/]")
    if stock_type == "PUBLIC":
        util.add_row(t, f"[{color.base}][{color.bnnr2}]Target Price[/]:[/]", fin.get("yearTarget"), lambda x: f"[{color.g6}]${float(x):,.2f}[/]")
    util.add_row(t, " ", " ")
    return Panel(t, title=f"[{color.BNNR2}]FINANCE[/]", border_style=f"{color.bnrd2}")

def render_funding_panel(data):
    fund = data.get("FUNDING", {})
    t = Table(show_header=False, box=None, padding=(0, 1))
    util.add_row(t, " ", " ")
    util.add_row(t, f"[{color.base}][{color.bnnr3}]Lead Investor[/]:[/]", fund.get("leadInvestor"), lambda x: f"[{color.bnnr3x}]{x}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr3}]Latest Share Class[/]:[/]", fund.get("latestShareClass"), lambda x: f"[{color.g1}]{x}[/]")
    util.add_row(t, " ", " ")
    util.add_row(t, f"[{color.base}][{color.bnnr3}]Total Funding Rounds[/]:[/]", fund.get("totalFundingRounds"), lambda x: f"[{color.g2}]{x}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr3}]Latest Funding Date[/]:[/]", fund.get("latestFundingDate"), lambda x: f"[{color.g3}]{x}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr3}]Latest Amount Raised[/]:[/]", fund.get("latestAmountRaised"), lambda x: f"[{color.g4}]{x}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr3}]Total Funding Raised[/]:[/]", fund.get("fundingToDate"), lambda x: f"[{color.g5}]{x}[/]")
    util.add_row(t, " ", " ")
    return Panel(t, title=f"[{color.BNNR3}]FUNDING[/]", border_style=f"{color.bnrd3}")

def render_ratings_panel(data):
    rat = data.get("RATINGS", {})
    t = Table(show_header=False, box=None, padding=(0, 1))
    util.add_row(t, " ", " ")
    util.add_row(t, f"[{color.base}][{color.bnnr3}]Recommendation[/]:[/]", rat.get("recommendationKey"), lambda x: f"[{color.bnnr3x}]{x}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr3}]Rec Score[/]:[/]", rat.get("recommendationMean"), lambda x: f"[{color.g3}]{x}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr3}]Total Analysts[/]:[/]", rat.get("analystCount"), lambda x: f"[{color.g4}]{x}[/]")
    util.add_row(t, " ", " ")
    util.add_row(t, f"[{color.base}][bright_cyan]Strong Buy[/]:[/]", rat.get("strongBuy"), lambda x: f"[{color.g1}]{x}[/]")
    util.add_row(t, f"[{color.base}][cyan1]Buy[/]:[/]", rat.get("buy"), lambda x: f"[{color.g2}]{x}[/]")
    util.add_row(t, f"[{color.base}][bright_sky_blue]Hold[/]:[/]", rat.get("hold"), lambda x: f"[{color.p6}]{x}[/]")
    util.add_row(t, f"[{color.base}][light_salmon3]Sell[/]:[/]", rat.get("sell"), lambda x: f"[{color.r2}]{x}[/]")
    util.add_row(t, f"[{color.base}][dark_orange3]Strong Sell[/]:[/]", rat.get("strongSell"), lambda x: f"[{color.r1}]{x}[/]")
    util.add_row(t, " ", " ")
    return Panel(t, title=f"[{color.BNNR3}]RATINGS[/]", border_style=f"{color.bnrd3}")

def render_news_panel(data):
    news = data.get("NEWS", [])
    if not news:
        return Panel("No news available.", title=f"[{color.BNNR4}]NEWS[/]", border_style=f"{color.bnrd4}")
    latest = news[0]
    news_url = latest.get("url", "")
    is_premium = latest.get("premium") == True
    is_freemium = latest.get("freemium") == True
    t = Table(show_header=False, box=None, padding=(0, 1))
    util.add_row(t, " ", " ")
    if is_premium or is_freemium:
        access_type = "Premium article (subscription required)" if is_premium else "Premium article (available for free)"
        util.add_row(t, f"[{color.base}][{color.bnnr4}]Access[/]:[/]", access_type, lambda x: f"[{color.r1 if is_premium else color.y1}]{x}[/]")
        util.add_row(t, " ", " ")
    util.add_row(t, f"[{color.base}][{color.bnnr4}]Source[/]:[/]", latest.get("source"), lambda x: f"[{color.bnnr4x}]{x}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr4}]Title[/]:[/]", latest.get("title"), lambda x: f"[{color.y1}]{x}[/]")
    util.add_row(t, f"[{color.base}][{color.bnnr4}]Category[/]:[/]", latest.get("category"), lambda x: f"[{color.y2}]{x}[/]")
    util.add_row(t, " ", " ")
    if news_url:
        link_cell = f"[link={news_url}]{news_url}[/link]"
    else:
        link_cell = "N/A"
    util.add_row(t, f"[{color.base}][{color.bnnr4}]Link[/]:[/]", link_cell)
    if not is_premium:
        news_image_url = latest.get("urlImage", "")
        if news_image_url:
            image_cell = f"[link={news_image_url}]{news_image_url}[/link]"
        else:
            image_cell = "N/A"
        util.add_row(t, f"[{color.base}][{color.bnnr4}]Image url[/]:[/]", image_cell)
        util.add_row(t, " ", " ")
    util.add_row(t, f"[{color.base}][{color.bnnr4}]Summary[/]:[/]", util.truncate(latest.get("summary", ""), 150), lambda x: f"[{color.info}]{x}[/]")
    util.add_row(t, " ", " ")
    return Panel(t, title=f"[{color.BNNR4}]NEWS[/]", border_style=f"{color.bnrd4}")



# =<< DASHBOARD
# === === === === === === === ===
def show_human_details(ticker, data, stock_type="PUBLIC"):
    expanded = "company"
    while True:
        ui.show_fms_banner()
        console.print(crumb.c_dashboard)

        # Company panel
        if expanded == "company":
            console.print(render_company_panel(data, stock_type))
        else:
            console.print(Panel("[dim]Press C to expand[/]", title=f"[{color.BNNR1}]COMPANY[/]", border_style=f"{color.bnrd1}"))

        # Finance panel
        if expanded == "finance":
            console.print(render_finance_panel(data, stock_type))
        else:
            console.print(Panel("[dim]Press F to expand[/]", title=f"[{color.BNNR2}]FINANCE[/]", border_style=f"{color.bnrd2}"))

        # Ratings (public) or Funding (private)
        if stock_type == "PUBLIC":
            if expanded == "ratings":
                console.print(render_ratings_panel(data))
            else:
                console.print(Panel("[dim]Press R to expand[/]", title=f"[{color.BNNR3}]RATINGS[/]", border_style=f"{color.bnrd3}"))
        else:
            if expanded == "funding":
                console.print(render_funding_panel(data))
            else:
                console.print(Panel("[dim]Press R to expand[/]", title=f"[{color.BNNR3}]FUNDING[/]", border_style=f"{color.bnrd3}"))

        # News panel
        if expanded == "news":
            console.print(render_news_panel(data))
        else:
            console.print(Panel("[dim]Press N to expand[/]", title=f"[{color.BNNR4}]NEWS[/]", border_style=f"{color.bnrd4}"))

        # Footer: single-key toggles and numeric choices
        key_label = "Ratings" if stock_type == "PUBLIC" else "Funding"
        console.print(f"\n[dim]C: Company  F: Finance  R: {key_label}  N: News[/dim]")
        console.print(f"[{color.exit}]0[/]. [{color.back}]CANCEL[/]")
        console.print(f"1. [{color.opt1}]ACCEPT[/]")

        ch = getch()
        if ch == 'c':
            expanded = "company"
        elif ch == 'f':
            expanded = "finance"
        elif ch == 'r':
            expanded = "ratings" if stock_type == "PUBLIC" else "funding"
        elif ch == 'n':
            expanded = "news"
        elif ch == '0' or ch == '1':
            # Consume the newline (Enter) that follows the digit
            sys.stdin.read(1)  # consumes '\n'
            return ch == '1'
        # else: ignore other keys and redraw