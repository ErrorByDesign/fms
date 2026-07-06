# Script for various useful random pieces of code

# -<< IMPORTS
import os
from pathlib import Path

# =<< PATHS
PATH_TERMUX_COLORS = Path.home() / ".termux" / "colors.properties"



# -<< Get visible terminal size
def terminal_size():
    size = os.get_terminal_size()
    return size.lines, size.columns
    print(f"Rows: {size.lines}, Columns: {size.columns}")

# -<< Get termux background color
def termux_bgcolor():
    p = PATH_TERMUX_COLORS
    for line in p.read_text().splitlines():
        line = line.strip()
        if line.startswith("background="):
            return line.split("=", 1)[1].strip()
    raise ValueError("background not found")

# -<< 