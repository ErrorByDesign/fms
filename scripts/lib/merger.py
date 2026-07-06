#!/usr/bin/env python3
# --- --- --- --- --- --- --- --- --- --- --- --
# -<< M E R G E R   &   H E A L T H   A U D I T >- -
# --- --- --- --- --

# -< IMPORTS
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# -< IMPORTS: LOCAL
import scripts.config.colors as color
import scripts.config.ui as ui
import scripts.config.utils as util

# -< IMPORTS: RICH
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table
console = Console()

# =<< PATHS
PATH_BACKUP             = "./data/cache/backup-portfolio.json"
PATH_MAPPING            = "./config/CIA/mappings-portfolio.json"
PATH_CONFIG_REPORT      = "./config/CIA/config-report.json"
PATH_REPORT             = "./config/report.json"
PATH_TEMPLATE_REPORT    = "./config/CIA/template-report.json"
PATH_PORTFOLIO          = "./data/portfolio.json"
PATH_NEWBORN            = "./data/cache/latest-newborn.json"
PATH_NEWBORN_CORRUPTED  = "./data/cache/corrupted-newborn.json"
PATH_NEWBORN_MISMATCHED = "./data/cache/mismatched-newborn.json"
PATH_REBORN             = "./data/cache/latest-reborn.json"
PATH_REBORN_CORRUPTED   = "./data/cache/corrupted-reborn.json"
PATH_REBORN_MISMATCHED  = "./data/cache/mismatched-reborn.json"
PATH_REFRESH            = "./data/cache/latest-refresh.json"
PATH_REFRESH_CORRUPTED  = "./data/cache/corrupted-refresh.json"
PATH_REFRESH_MISMATCHED = "./data/cache/mismatched-refresh.json"
PATH_TEMPLATE_PORT      = "./config/CIA/template-portfolio.json"



# -<< COUNT POPULTABLE
# --- --- --- --- --- --- --- ---
def count_populatable_leaves(data, current_path="", count_populatable=False):
    """ F U N C T I O N :
    Detect sections.
    Count poulatable leaves per section.
    """
    total    = 0
    sections = {}
    # COUNT POPULATABLE LEAVES
    if isinstance(data, dict):
        # DETERMINE SECTION AND COUNT LEAVES
        for k, v in data.items():
            # DETERMINE SECTION
            path = f"{current_path}.{k}" if current_path else k
            if '.' not in path:
                section = "ROOT"
            else:
                section = path.split('.')[0]
                if section.startswith("NEWS"):
                    section = "NEWS"
                if not section:
                    section = "ROOT"
            #COUNT POPULATABLE LEAVES
            if isinstance(v, dict):
                sub_total, sub_sections = count_populatable_leaves(v, path, count_populatable)
                total += sub_total
                for sec, cnt in sub_sections.items():
                    sections[sec] = sections.get(sec, 0) + cnt
            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    sub_total, sub_sections = count_populatable_leaves(v[0], f"{path}.[]", count_populatable)
                    total += sub_total
                    for sec, cnt in sub_sections.items():
                        sections[sec] = sections.get(sec, 0) + cnt
                else:
                    if not count_populatable or v != []:
                        total += 1
                        sections[section] = sections.get(section, 0) + 1
            else:
                if count_populatable:
                    if v is None or v == "" or v == []:
                        pass
                    else:
                        total += 1
                        sections[section] = sections.get(section, 0) + 1
                else:
                    total += 1
                    sections[section] = sections.get(section, 0) + 1
    # RETURN PER-SECTION COUNT
    return total, sections

# -<< COUNT POPULATED
# --- --- --- --- --- --- --- ---
def count_populated_leaves(obj):
    """ F U N C T I O N :
    Count populated leaves per section.
    Detect arrays.
    Count populated leaves of index [0] per array.
    """
    cnt = 0
    # COUNT POPULATED SECTION LEAVES
    if isinstance(obj, dict):
        for v in obj.values():
            cnt += count_populated_leaves(v)
    # COUNT POPULATED ARRAY[0] LEAVES
    elif isinstance(obj, list):
        if obj and isinstance(obj[0], dict):
            cnt += count_populated_leaves(obj[0])
    # COUNT ROOT LEAVES
    else:
        if obj is not None and obj != "":
            cnt += 1
    # RETURN TOTAL COUNT
    return cnt



# =<< BRANCH 0. PROCESS RESET
# === === === === === === === ===
def process_reset():
    """ F U L L   S Y S T E M   R E S E T :
    ||| USAGES:
    • If health check reports continous errors.
    • Changes in the structure of fetched data.
    • Changes in the sttucture of FMS tmplates.
    ||| RESULT:
    • Validates mappings against template. 
    • Updates config-report.json and report.json.
    • Displays post-reset metrics.
    """
    ui.show_fms_banner()
    console.print(f"[{color.DONE}]SYSTEM RESET INITIATED[/]\n")

    # FILES: LOAD EXTERNAL DATA
    template_port   = util.load_json(PATH_TEMPLATE_PORT).get("TICKER_SYMBOL", {})
    mappings        = util.load_json(PATH_MAPPING)
    portfolio       = util.load_json(PATH_PORTFOLIO)
    template_report = util.load_json(PATH_TEMPLATE_REPORT)

    # PREPARE DNA SEQUENCES
    private_map = mappings.get("PRIVATE", {})
    public_map  = mappings.get("PUBLIC", {})

    # PERFORM DNA SEQUENCING
    template_total,  template_sections = count_populatable_leaves(template_port, count_populatable=False)
    private_total,   private_sections  = count_populatable_leaves(private_map,   count_populatable=False)
    public_total,    public_sections   = count_populatable_leaves(public_map,    count_populatable=False)
    console.print(f"[{color.base}]• [{color.b1}]Template nodes[/]: [{color.b1}]{template_total}[/]")
    console.print(f"[{color.base}]• [{color.b2}]Private  nodes[/]:  [{color.b2}]{private_total}[/]")
    console.print(f"[{color.base}]• [{color.b3}]Public   nodes[/]:   [{color.b3}]{public_total}[/]")

    # ERROR: DNA TO RNA MUTATION DETECTED
    if template_total != private_total or template_total != public_total:
        util.pause(reason="f", message=f"[{color.info}]Mappings do not match template structure, \n[{color.DONE}]Template[/]: [{color.VAL}]{template_total}[/] \n[{color.ACTV}]Private[/]: [{color.VAL}]{private_total}[/] \n[{color.ACTV}]Public[/]: [{color.VAL}]{public_total}[/] \nManually correct [{color.DOS}]mappings-portfolio.json[/] to match [{color.DOS}]template-portfolio.json[/].[/]")

    # DNA SEQUENCE MATCHED
    console.print(f"[{color.base}][{color.DONE}]All sources match. [{color.PASS}]Template total[/]: [{color.ACTV}]{template_total}[/][/]")

    # FILE: LOAD (config-report.json)
    config_report = util.load_json(PATH_CONFIG_REPORT)
    if not config_report:
        config_report = {"CONFIG": {"MERGER": {"NODES": {}}}}

    # FILE: UPDATE (config-report.json)
    config_report.setdefault("CONFIG", {}).setdefault("MERGER", {}).setdefault("NODES", {})
    config_report["CONFIG"]["MERGER"]["NODES"]["PORTFOLIO"] = {"BRANCHES": template_sections, "TOTAL": template_total}
    config_report["CONFIG"]["MERGER"]["NODES"]["PRIVATE"]   = {"BRANCHES": private_sections,  "TOTAL": private_total}
    config_report["CONFIG"]["MERGER"]["NODES"]["PUBLIC"]    = {"BRANCHES": public_sections,   "TOTAL": public_total}

    # FILE: SAVE (config-report.json)
    util.save_json(PATH_CONFIG_REPORT, config_report)
    console.print(f"[{color.base}][{color.DONE}]Config report updated[/]: [{color.DOS}]{PATH_CONFIG_REPORT}[/][/]")

    # COMPUTE CHROMOSOME COUNTS PER EMBRYO TYPE
    leaf_nodes_plc, _ = count_populatable_leaves(public_map,  count_populatable=True)
    leaf_nodes_pvt, _ = count_populatable_leaves(private_map, count_populatable=True)
    leaf_nodes_ptf    = template_total
    console.print(f"[{color.base}]• [{color.g1}]Populatable leaves (plc)[/]: [{color.ACTV}]{leaf_nodes_plc}[/][/]")
    console.print(f"[{color.base}]• [{color.g2}]Populatable leaves (pvt)[/]: [{color.ACTV}]{leaf_nodes_pvt}[/][/]")

    # PERFORM DNA TO RNA SEQUENCING
    count_plc = sum(1 for d in portfolio.values() if d.get("stockType", "").upper() == "PUBLIC")
    count_pvt = sum(1 for d in portfolio.values() if d.get("stockType", "").upper() == "PRIVATE")
    count_ptf = count_plc + count_pvt

    # MOTHER DNA MISSING
    if leaf_nodes_ptf == 0:
        util.pause(reason="e", message=f"Mother's DNA missing or corrupt, check [{color.DOS}]template-portfolio.json[/]", enter="e")

    # MOTHER DNA SEQUENCING
    score_plc = round((leaf_nodes_plc / leaf_nodes_ptf) * 100, 2)
    score_pvt = round((leaf_nodes_pvt / leaf_nodes_ptf) * 100, 2)
    score_ptf = round(((score_plc * count_plc) + (score_pvt * count_pvt)) / count_ptf, 2) if count_ptf > 0 else 0.0

    # BUILD NEW REPORT
    new_report = {
        "PORTFOLIO": {
            "scorePtf":     score_ptf,
            "scorePlc":     score_plc,
            "scorePvt":     score_pvt,
            "countPtf":     count_ptf,
            "countPlc":     count_plc,
            "countPvt":     count_pvt,
            "leafNodesPtf": leaf_nodes_ptf,
            "leafNodesPlc": leaf_nodes_plc,
            "leafNodesPvt": leaf_nodes_pvt,
            "timestamp":    datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "epoch":        int(datetime.now(timezone.utc).timestamp())
        }
    }
    ticker_blueprint = template_report.get("TICKER_SYMBOL", {"corrupt": None, "score": None, "epoch": None})
    for ticker in portfolio.keys():
        new_report[ticker] = ticker_blueprint.copy()

    # SAVE NEW REPORT
    util.save_json(PATH_REPORT, new_report)
    console.print(f"[{color.DONE}]Report reset and saved to [{color.DOS}]{PATH_REPORT}[/].[/]")

    # NEW RESET HEALTH SUMMARY
    ui.merger_reset_health_summary(leaf_nodes_plc, leaf_nodes_pvt, leaf_nodes_ptf, count_plc, count_pvt, count_ptf, score_plc, score_pvt, score_ptf)
    util.pause(reason="p", message="Baseline health metrics recalculated", enter="e")
    sys.exit(0)

# =<< BRANCH 1. PROCESS BORN (newborn | reborn)
# === === === === === === === ===
def process_born(flag):
    # DETERMINE SOURCE PATH AND LOAD EXTERNAL DATA
    source_path   = PATH_REBORN if flag == "--reborn" else PATH_NEWBORN
    data_payload  = util.load_json(source_path)
    config_report = util.load_json(PATH_CONFIG_REPORT)

    # NO EMBRYO FOUND
    if not data_payload:
        util.pause(reason="e", message=f"[{color.info}]Insemination aborted due to missing DNA sequence. Failed to {'revive reborn' if flag == '--reborn' else 'deliver newborn'} child. No such file at [{color.DOS}]{source_path}[/].[/]")

    # VERIFY TEST-LAB BASELINE EXISTS
    leaf_nodes_ptf = config_report.get("CONFIG", {}).get("MERGER", {}).get("NODES", {}).get("PORTFOLIO", {}).get("TOTAL", 0)
    if leaf_nodes_ptf == 0:
        util.pause(reason="e", message=f"[{color.info}]Invalid structure. Mother's DNA sequence not found in [{color.DOS}]config-report.json[/]. [{color.inst}]Run [{color.VAL}]--reset[/] to initialise health metrics[/].[/]", enter="e")

    # FILES: LOAD EXTERNAL DATA
    report    = util.load_json(PATH_REPORT)
    portfolio = util.load_json(PATH_PORTFOLIO)
    template  = util.load_json(PATH_TEMPLATE_REPORT)
    rep_ptf   = report.get("PORTFOLIO", {})

    # BEGIN FULL HEALTH CHECK
    for ticker, data in data_payload.items():
        stock_type = data.get("stockType", "PUBLIC").upper()
        baseline   = rep_ptf.get("scorePvt" if stock_type == "PRIVATE" else "scorePlc", 0)

        # --- Phase 1: structural integrity check ---
        total, _ = count_populatable_leaves(data, count_populatable=False)
        if total != leaf_nodes_ptf:
            dest = f"{ticker}-corrupted.json"
            if os.path.exists(source_path):
                os.rename(source_path, f"./data/cache/{dest}")
            util.pause(reason="e", message=f"[{color.info}]Insemination aborted due to missing chromosomes in [{color.ACTV}]{ticker}[/]. \n[{color.DONE}]Expected[/]: [{color.PASS}]{leaf_nodes_ptf} chromosomes[/] \n[{color.DONE}]Detected[/]: [{color.FAIL}]{total} chromosomes[/] \nRenamed to [{color.DOS}]{dest}[/].[/]")

        # --- Phase 2: chromosome (population) score check ---
        p     = count_populated_leaves(data)
        score = round((p / leaf_nodes_ptf) * 100, 2)
        if score != baseline:
            dest = f"{ticker}-mismatched.json"
            if os.path.exists(source_path):
                os.rename(source_path, f"./data/cache/{dest}")
            util.pause(reason="e", message=f"[{color.info}]Insemination aborted due to chromosome mismatch for [{color.ACTV}]{ticker}[/]. \n[{color.DONE}]Score[/]: [{color.FAIL}]{score}%[/] ([{color.PASS}]Expected[/]: [{color.VAL}]{baseline}%[/]). \nRenamed to [{color.DOS}]{dest}[/].[/]", enter="e")

        # --- Display health summary ---
        ui.show_fms_banner()
        console.print(f"\n[{color.BNNR1}]DNA HEALTH REPORT[/] — [{color.VAL}]{ticker}[/]\n")
        health_table = Table(show_header=False, box=None)
        health_table.add_row(f"[{color.bnnr1}]Ticker[/]",           f"[{color.VAL}]{ticker}[/]")
        health_table.add_row(f"[{color.bnnr2}]Stock type[/]",       f"[{color.ACTV}]{stock_type}[/]")
        health_table.add_row(f"[{color.bnnr3}]Populated leaves[/]", f"[{color.VAL}]{p}[/]")
        health_table.add_row(f"[{color.bnnr3}]Score[/]",            f"[{color.DONE}]{score}%[/]")
        health_table.add_row(f"[{color.bnnr3}]Baseline[/]",         f"[{color.DONE}]{baseline}%[/]")
        health_table.add_row(f"[{color.bnnr4}]Result[/]",           f"[{color.PASS}]PASS[/]")
        console.print(health_table)

        # --- Interactive insemination menu ---
        
        while True:
            choice = ui.show_menu(
                breadcrumb="",                options=[
                    ("0", "CANCEL",     color.back),
                    ("1", "INSEMINATE", color.opt1),
                    ("2", "VIEW JSON",  color.opt2),
                    ("3", "OPEN FILE",  color.opt3),
                ],
                choice=True
            )            
            if choice == "0":
                return
            elif choice == "1":
                break
            elif choice == "2":
                ui.show_fms_banner()
                crumb.merger_inseminate_sequence(stock_type, ticker)
                console.print(JSON.from_data(data))
                console.print("\n" + "─" * 40)
                util.pause()
            elif choice == "3":
                if os.name == "nt":
                    os.startfile(source_path)
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    os.system(f"{opener} {source_path}")

        # --- Merge into portfolio ---
        portfolio[ticker] = data
        if flag == "--newborn":
            new_entry = template.get("TICKER_SYMBOL", {}).copy()
            new_entry.update({"corrupt": None, "score": None, "epoch": None})
            report[ticker] = new_entry
            rep_ptf["countPtf"] += 1
            if stock_type == "PRIVATE":
                rep_ptf["countPvt"] += 1
            else:
                rep_ptf["countPlc"] += 1

        # Update ticker report entry
        now_epoch = int(datetime.now(timezone.utc).timestamp())
        report[ticker]["corrupt"] = False
        report[ticker]["score"]   = score
        report[ticker]["epoch"]   = now_epoch

        # Recalculate portfolio-level score
        if rep_ptf["countPtf"] > 0:
            rep_ptf["scorePtf"] = round(
                ((rep_ptf["countPlc"] * rep_ptf["scorePlc"]) + (rep_ptf["countPvt"] * rep_ptf["scorePvt"]))
                / rep_ptf["countPtf"], 2
            )

        # Timestamp the report
        now = datetime.now(timezone.utc)
        report["PORTFOLIO"]["timestamp"] = now.isoformat(timespec="seconds").replace("+00:00", "Z")
        report["PORTFOLIO"]["epoch"]     = now_epoch

        util.save_json(PATH_REPORT, report)
        util.save_json(PATH_PORTFOLIO, portfolio)

        console.print(f"\n[{color.info}][{color.DONE}]SUCCESS[/]: [{color.VAL}]{ticker}[/] ([{color.opt2}]{stock_type}[/]) DNA merged into portfolio.[/]")
        util.pause("d")

# =<< BRANCH 2. PROCESS REFRESH
# === === === === === === === ===
def process_refresh():
    # ===== PHASE 0: LOAD AND VALIDATE INPUTS =====
    refresh       = util.load_json(PATH_REFRESH)
    report        = util.load_json(PATH_REPORT)
    config_report = util.load_json(PATH_CONFIG_REPORT)

    # VERIFY PATIENT APPOINTMENT
    if not refresh or not report:
        missing = PATH_REFRESH if not refresh else PATH_REPORT
        util.pause(reason="e", message=f"[{color.info}]Required file [{color.DOS}]{missing}[/] not found. [{color.inst}]Run [{color.DOS}]incubator.py [{color.VAL}]--refresh[/] first[/].[/]")

    # PREPARE DNA SEQUENCE LABORATORY
    rep_ptf        = report.get("PORTFOLIO", {})
    leaf_nodes_ptf = config_report.get("CONFIG", {}).get("MERGER", {}).get("NODES", {}).get("PORTFOLIO", {}).get("TOTAL", 0)
    if leaf_nodes_ptf == 0:
        util.pause(reason="e", message=f"[{color.info}]Mother's DNA missing or corrupt. [{color.inst}]Run [{color.VAL}]--reset[/] to initialise health metrics[/].[/]", enter="e")

    # ===== PHASE 1: STRUCTURAL DNA CHECK (whole-portfolio) =====
    corrupted_tickers = [
        ticker for ticker, data in refresh.items()
        if count_populatable_leaves(data, count_populatable=False)[0] != leaf_nodes_ptf
    ]

    # QUARANTINE MOTHER
    if corrupted_tickers:
        # Quarantine mother
        if os.path.exists(PATH_REFRESH):
            os.rename(PATH_REFRESH, PATH_REFRESH_CORRUPTED)

        # Identify genetically modified embryos
        ui.merger_refresh_dna_mutations(corrupted_tickers, PATH_REFRESH, PATH_REFRESH_CORRUPTED)

        # Update per-embryo health report
        for ticker in corrupted_tickers:
            if ticker in report:
                report[ticker]["corrupt"] = True

        # File health report and abort operation
        util.save_json(PATH_REPORT, report)
        util.pause(reason="e", message=f"[{color.info}][{color.ERR}]Swap aborted[/]. [{color.WARN}]DNA mutation detected[/]. Corrupted patient quarantined at [{color.DOS}]{PATH_REFRESH_CORRUPTED}[/].[/]", enter="e")

    # ===== PHASE 2: CHROMOSOME SCORE CHECK (per-ticker) =====
    scores             = {}
    mismatched_tickers = []

    # PREPARE CHROMOSOME TEST LAB METRICS
    for ticker, data in refresh.items():
        stock_type     = data.get("stockType").upper()
        baseline       = rep_ptf.get("scorePvt" if stock_type == "PRIVATE" else "scorePlc", 0)
        p              = count_populated_leaves(data)
        score          = round((p / leaf_nodes_ptf) * 100, 2)
        scores[ticker] = (p, score)

        # COLATE EMBRYOS WITH MISSING CHROMOSOMES
        if score != baseline:
            mismatched_tickers.append(ticker)

    # ===== PHASE 3: BACKUP AND SWAP =====
    if os.path.exists(PATH_PORTFOLIO):
        os.replace(PATH_PORTFOLIO, PATH_BACKUP)
    os.replace(PATH_REFRESH, PATH_PORTFOLIO)

    # ===== PHASE 4: POST-SWAP HEALTH AUDIT =====
    with open(PATH_PORTFOLIO, 'r') as f:
        portfolio = json.load(f)

    # ANALYZE NEW MOTHER'S' EMBRYO(S)
    count_plc = sum(1 for d in portfolio.values() if d.get("stockType", "").upper() == "PUBLIC")
    count_pvt = sum(1 for d in portfolio.values() if d.get("stockType", "").upper() == "PRIVATE")
    total_score_sum = sum(score for _, score in scores.values())
    calc_score      = round(total_score_sum / len(portfolio), 2) if portfolio else 0

    # SHOW HEALTH BANNER AND SUMMARY
    ui.merger_health_banner()
    ui.merger_refresh_health_summary(rep_ptf, leaf_nodes_ptf, count_plc, count_pvt, calc_score)

    # SHOW MISSING CHROMOSOMES
    if calc_score != rep_ptf.get("scorePtf", 0):
        ui.merger_refresh_missing_chromosomes(mismatched_tickers)

    # PER-EMBRYO SCAN
    now_epoch = int(datetime.now(timezone.utc).timestamp())
    for ticker, data in portfolio.items():
        if ticker not in report:
            report[ticker] = {"corrupt": None, "score": None, "epoch": None}
        
        # DETERMINE TEST SUBJECT AND EMBRYO TYPE
        stock_type = data.get("stockType").upper()
        baseline   = rep_ptf["scorePvt"] if stock_type == "PRIVATE" else rep_ptf["scorePlc"]
        p, score   = scores.get(ticker, (0, 0))
        corrupt    = (score != baseline)

        # UPDATE PER-EMBRYO HEALTH REPORT
        report[ticker]["corrupt"] = corrupt
        report[ticker]["score"]   = score
        report[ticker]["epoch"]   = now_epoch

        # SHOW PER-EMBRYO CHROMOSOME DETAILS
        if corrupt:
            ui.merger_refresh_corrupt_chromosomes(ticker, stock_type, p, rep_ptf, score, baseline)
        else:
            ui.merger_refresh_correct_chromosomes(ticker, stock_type, p, rep_ptf, score, baseline)

    # SIGN OFF UPDATED HEALTH REPORT
    now = datetime.now(timezone.utc)
    report["PORTFOLIO"]["timestamp"] = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    report["PORTFOLIO"]["epoch"]     = now_epoch

    # FILE PATIENT REPORT AND HEADLESS EXIR
    util.save_json(PATH_REPORT, report)
    ui.merger_refresh_final_message(PATH_REPORT)
    sys.exit()



# === === === === === === === ===
# == =<< MAIN >>- --- --- --- ---
if __name__ == "__main__":
    if "--reset" in sys.argv:
        process_reset()
    elif "--refresh" in sys.argv:
        process_refresh()
    elif len(sys.argv) >= 4:
        mode_flag = sys.argv[3].lower()
        process_born(mode_flag)
    else:
        console.print(f"[[{color.ACTV}]USAGE[/]]: python merger.py [--reset | --refresh | TYPE TICKER [--newborn|--reborn]]")
        util.pause(reason="e",message=sys.argv, enter="e")
        sys.exit(1)