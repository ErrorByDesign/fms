# ./scripts/config/introduction.py

# -< IMPORTS
import os

# -< IMPORTS: LOCAL
# import scripts.config.definitions as define
import scripts.config.colors as color
import scripts.config.utils as util

# -< IMPORTS: RICH
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
console = Console()
cw = console.width



# -<< INTRO PAGE
# === === === === === === === ===
def welcome_page():
    # Verify boot up sequence health and system states
    is_headless      = False
    portfolio_exists = os.path.exists("./data/portfolio.json")
    system_ready     = portfolio_exists and os.path.getsize("./data/portfolio.json") > 0
    heartbeat_stable = system_ready

    # Define aplication and developer panel titles and subtitles
    mother_str   = "M  O  T  H  E  R      P  R  O  J  E  C  T"
    fms_str      = "F I N A N C I A L   M O D E L L E I N G   S H E L L"
    fms_str_mini = "FINANCIAL MODELLING SHELL: Lite"

    # Define health and system state titles
    health_str = ":  ::  :::  H E A L T H   S T A B L E  :::  ::  :" if heartbeat_stable else "DIAGNOSTICS REQUIRED"
    online_str = "·  ··  •••  S Y S T E M   O N L I N E  •••  ··  ·" if system_ready else "DATABASE MISSING"

    # Define health and system state patterns
    status_color_health = "blink red" if heartbeat_stable else "blink light_coral"
    status_color_online = "plum3" if system_ready else "bold light_coral"
    status_msg_health = Text(health_str, style=status_color_health, no_wrap=True)
    status_msg_online = Text(online_str, style=status_color_online, no_wrap=True)

    # Define central message
    text    = "|  PRESS ENTER TO ENTER  |"
    pattern = ":"
    sideL   = "|"
    sideR   = "|"
    sides   = 1
    inner   = "|"
    inners  = 1

    # Call scripts/config/UTILS to fit central enter message to console width
    enter = util.fit_to_width(text, pattern, sideL, sideR, sides, inner, inners)

    # Define central message borders
    textLen    = len(text)
    text       = ("|" + ("⁻" * (textLen - 2)) + "|")
    paddingT   = util.fit_to_width(text, pattern, sideL, sideR, sides, inner, inners)
    text       = ("|" + ("_" * (textLen - 2)) + "|")
    paddingB   = util.fit_to_width(text, pattern, sideL, sideR, sides, inner, inners)
    top_bottom = ("|" + ("=" * (cw - 2)) + "|")

    # Print main title panel
    console.print(Panel(
        Align.center(f"[khaki3]{fms_str_mini if cw < 50 else fms_str}[/]"),
        title="[coral_green]xerxes[/]",
        title_align="left",
        padding=(0,0),
        border_style="light_steel_blue1",
        subtitle="MOTHER—PROJECT",
        subtitle_align="right"
    ))

    # Print upper pattern
    console.print(f"[{color.base}]{top_bottom}[/]")
    console.print((("[bold misty_rose1]|[/bold misty_rose1]" + ("[bold medium_orchid3]:[/bold medium_orchid3]" * (cw - 2))) + "[bold misty_rose1]|[/bold misty_rose1]" + "\n") * 2 + (("[bold misty_rose1]|[/bold misty_rose1]" + ("[bold medium_orchid3]:[/bold medium_orchid3]" * (cw - 2))) + "[bold misty_rose1]|[/bold misty_rose1]"))

    # Print upper panel
    console.print(Panel(
        Align.center(f"[{status_color_health}]{status_msg_health}[/]"), 
        title="[bold misty_rose3]XERXES FINANCIAL MODELLING SHELL OS v2.0[/bold misty_rose3]", 
        title_align="center",
        padding=(1, 1),
        border_style="misty_rose1",
        subtitle=f"MODE: {'AUTOMATED' if is_headless else 'DIVINE INTERVENTION'}",
        subtitle_align="right"
    ))

    # Print central enter message and patterns
    console.print((("[bold misty_rose3]|[/]" + ("[bold pale_violet_red1]:[/]" * (cw - 2))) + "[bold misty_rose3]|[/]" + "\n") * 2 + (("[bold misty_rose3]|[/]" + ("[bold pale_violet_red1]:[/]" * (cw - 2))) + "[bold misty_rose3]|[/]"))
    console.print(f"[plum3]{paddingT}[/]")
    console.print(f"[plum1]{enter}[/]")
    console.print(f"[plum3]{paddingB}[/]")
    console.print((("[bold misty_rose3]|[/]" + ("[bold pale_violet_red1]:[/]" * (cw - 2))) + "[bold misty_rose3]|[/]" + "\n") * 2 + (("[bold misty_rose3]|[/]" + ("[bold pale_violet_red1]:[/]" * (cw - 2))) + "[bold misty_rose3]|[/]"))

    # Print lower panel
    console.print(Panel(
        Align.center(status_msg_online), 
        title="[bold misty_rose3]XERXES CORE[/]",
        title_align="center",
        padding=(1, 2),
        border_style="misty_rose1",
        subtitle=f"LOGIC: {'STABLE' if system_ready else 'CRITICAL FAILURE'}",
        subtitle_align="right"
    ))

    # Print bottom border
    console.print((("[bold misty_rose1]|[/]" + ("[bold medium_orchid3]:[/]" * (cw - 2))) + "[bold misty_rose1]|[/]" + "\n") * 2 + (("[bold misty_rose1]|[/]" + ("[bold medium_orchid3]:[/]" * (cw - 2))) + "[bold misty_rose1]|[/]"))
    console.print(f"[{color.base}]{top_bottom}[/]")