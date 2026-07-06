# ./scripts/config/utils.py
# -- --- --- --- --- --- --- --- --- --- --- --- -- 
# -< F M S   T E R M I N A L :   U T I L I T I E S
# -- --- --- --- --

# -< IMPORTS
import colorsys
import json
import os
import re
import sys
import textwrap
import time

# -< IMPORTS: LOCAL
import scripts.config.colors as color

# -< IMPORTS: RICH
from rich.console import Console
console = Console()
cw = console.width



# --- --- --- --- ---
# COLORS AND STYLES
# --- --- --- --- ---
# -< COLOR: COMPLIMENTARY
def comp_color(hex_color):
    """Approximate complementary color by rotating hue in HSV."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255

    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + 0.25) % 1.0  # 180° hue shift
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    return f"#{round(r*255):02X}{round(g*255):02X}{round(b*255):02X}"

# -< COLOR: TEXT
def text_color(hex_color):
    """Simple RGB invert for text / accent."""
    hex_color = hex_color.lstrip("#")
    r = 255 - int(hex_color[0:2], 16)
    g = 255 - int(hex_color[2:4], 16)
    b = 255 - int(hex_color[4:6], 16)

    return f"#{r:02X}{g:02X}{b:02X}"

# -< COLOR: TINT
def tint_color(hex_color, factor):
    """Lighten/darken by scaling RGB channels."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = max(0, min(255, round(r * factor)))
    g = max(0, min(255, round(g * factor)))
    b = max(0, min(255, round(b * factor)))

    return f"#{r:02X}{g:02X}{b:02X}"



# --- --- --- --- ---
# EXTERNAL STORAGE
# --- --- --- --- ---
# -< JSON: LOAD
def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as file: return json.load(file)

# -< JSON: SAVE
def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as file: json.dump(data, file, indent=4)



# --- --- --- --- ---
# DATA AND FORMATTING
# --- --- --- --- ---
# -< CAMEL CASE
def camel_case(key: str) -> str:
    parts = re.split(r"[ _\-]+", key.strip())
    if not parts:
        return ""
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])

# -< FIT TO WIDTH
def fit_to_width(text, pattern, pattern_sideL="", pattern_sideR="", width_sides=0, pattern_inner="", width_inner=0):
    total_gap   = cw - len(text)
    total_width = width_sides + width_inner
    left_count  = (total_gap // 2) - total_width
    pL = pattern * max(0, left_count)
    pR = pattern * max(0, (total_gap - (left_count + total_width)) - total_width)
    return pattern_sideL + pL + pattern_inner + text + pattern_inner + pR + pattern_sideR

# -< NEWLINE
def newline(text):
    if not text: return ""
    clean = re.sub(r'\s+', ' ', str(text)).strip()
    return re.sub(r'\. (?=[A-Z])', '.\n\n', clean)

# -< TRUNCATE
def truncate(text, length=140):
    if not text: return ""
    width = cw if length > cw * 0.75 else length
    return textwrap.shorten(str(text), width, placeholder="...")

# -< IS VALID
def is_valid(val):
    if val is None:
        return False
    if isinstance(val, str) and val == "":
        return False
    # Handle numpy arrays and other collections
    try:
        if hasattr(val, '__len__') and len(val) == 0:
            return False
    except TypeError:
        pass
    return True



# --- --- --- --- ---
# SCRIP FLOW
# --- --- --- --- ---
# -< PAUSE
def pause(reason="", message="", enter=""):
    # Define action on Enter key press
    if enter == "e" or (enter == "" and reason == "e"):
        nxt = "exit program"
    else:
        nxt = "continue" if enter == "" else enter

    # Define pause reason and message
    if reason == "bug" or reason == "b":
        msg = f"Debugging required, [{color.inst}]restart the program with a '[{color.crmb}]--debug[/]' flag to enter developer mode" if message == "" else message
        console.input(f"\n[{color.info}][{color.DOS}]DEBUG[/]: {msg}. Press Enter to {nxt}...[/]")
        sys.exit(1)
    elif reason == "done" or reason == "d":
        msg = "Task complete." if message == "" else message
        console.input(f"\n[{color.info}][{color.DONE}]DONE[/]: {msg}. Press Enter to {nxt}...[/]")
    elif reason == "err" or reason == "e":
        msg = "Fatal error occured" if message == "" else message
        console.input(f"\n[{color.info}][{color.ERR}]ERROR[/]: {msg}. Press Enter to {nxt}...[/]")
    elif reason == "fail" or reason == "f":
        msg = "Task completed unsuccessfully" if message == "" else message
        console.input(f"\n[{color.info}][{color.FAIL}]FAILURE[/]: {msg}. Press Enter to {nxt}...[/]")
    elif reason == "pass" or reason == "p":
        msg = "Task completed successfully" if message == "" else message
        console.input(f"\n[{color.info}][{color.PASS}]SUCCESS[/]: {msg}. Press Enter to {nxt}...[/]")
    elif reason == "warn" or reason == "w":
        msg = "Task completed with warning(s), excersise caution" if message == "" else message
        console.input(f"\n[{color.info}][{color.WARN}]WARNING[/]: {msg}. Press Enter to {nxt}...[/]")
    else:
        msg = "Script paused" if message == "" and reason == "" else message
        console.input(f"\n[{color.info}][{color.DOS}]GENERAL[/]: {msg}. Press Enter to {nxt}...[/]")

# -< TASK RESULT
def show_task_result(msg="pass", passed=True, padding="", exit=False, end="", auto=True, sleep=1, solution=""):
    negative = f"[{color.FAIL}]Task failed[/]" if msg == "fail" or (msg == "" and not passed) else msg
    positive = f"[{color.PASS}]Task completed successfully[/]" if msg == "pass" or (msg == "" and passed) else msg
    result   = positive if passed else negative
    advice   = f" {solution}." if solution else ""
    if end in ("e", "x", "exit") or (end == "" and exit and not auto):
        ending = "exit"
    elif end in ("c", "cont", "continue") or (end == "" and not exit and not auto):
        ending = "continue"
    else:
        ending = end
    suffix = "" if auto else f" Press Enter to {ending}..."
    console.print(f"{padding}[{color.info}]{result}.[{color.ACTV}]{advice}[/]{suffix}[/]", end="")
    if auto:
        time.sleep(sleep)
    else:
        console.input("")

# -< WAIT SPINNER
def wait_spinner(message="", wait=3):
    # Define waiting message
    msg = "Processing..." if message == "" else message
    # The message will appear with a spinning dot/ellipsis
    with console.status(f"[{color.DONE}]{msg}[/]") as status:
        time.sleep(wait)



# --- --- --- --- ---
# TABLES AND PANELS
# --- --- --- --- ---
# -<< TABLES: ADD ROW
def add_row(table, label, value, fmt=None):
    if is_valid(value):
        display_val = fmt(value) if fmt else str(value)
        table.add_row(label, display_val)