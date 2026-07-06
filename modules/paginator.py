#!/usr/bin/env python3
# === === === === === === === === === === === === ===
# M O D U L E   D Y N A M I C   M E N U
# === === === === ===



# PAGINATE
# --- --- --- --- --- --- --- ---
def paginate(items, page=0, page_size=7):

    total_items = len(items)

    start = page * page_size
    end = start + page_size

    page_items = items[start:end]

    has_more = end < total_items

    if has_more:
        exit_position = 9
    else:
        exit_position = len(page_items) + 1

    return page_items, has_more, exit_position



# === === === === === === === ===
# =<< MODULE GATE >>- --- --- ---
if __name__ == "__main__":
    # Internal test for manual Termux execution
    import os
    
    # Setup paths relative to root (assuming you run from FMSLite/)
    cache   = "./data/cache/latest-portfolio.json"
    master  = "./data/portfolio.json"
    mapping = "./config/CIA/mappings-portfolio.json"
    
    print(f"Testing Merge Logic...")
    if merge_cache_to_master(cache, master, mapping):
        print("Done! Check stock-data.json for updates.")
    else:
        print("Merge failed. Check if files exist and mapping is correct.")