    #!/usr/bin/env python3
    # --- --- --- --- --- --- --- --- --- --- --- --
    # -<< S T R U C T U R E   &   T E M P L A T E S
    # --- --- --- --- --

    # -< IMPORTS
    import json
    import random
    import re
    import subprocess
    import sys
    import time
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

    # -< IMPORTS: LOCAL
    import scripts.config.colors as color
    import scripts.config.input as inp
    import scripts.config.ui as ui
    import scripts.config.utils as util

    # -< IMPORTS: RICH
    from rich.console import Console
    from rich.prompt import IntPrompt, Confirm
    console = Console()

    # =<< PATHS
    PATH_BACKUP    = "./data/cache/backup-portfolio.json"
    PATH_INCUBATOR = "./scripts/incubator.py"
    PATH_MAPPING   = "./config/CIA/mappings-portfolio.json"
    PATH_PORTFOLIO = "./data/portfolio.json"
    PATH_REPORT    = "./config/report.json"
    PATH_TEMPLATE  = "./config/CIA/template-portfolio.json"



    # -< UTILITIES
    # -- --- --- --- --- --- --- ---
    def backup_portfolio_file():
        import shutil
        from pathlib import Path

        dst = Path(PATH_BACKUP)
        src = Path(PATH_PORTFOLIO)

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        console.print(f"[{color.DONE}]✔ Portfolio backup created.[/]")
        time.sleep(1)

    def insert_root_key(ticker, key, value):
        new = {}

        for k, v in ticker.items():
            # first branch encountered
            if isinstance(v, dict) or isinstance(v, list):
                new[key] = value
                new[k] = v
                # copy rest
                for kk in list(ticker.keys())[list(ticker.keys()).index(k)+1:]:
                    new[kk] = ticker[kk]
                return new

            new[k] = v

        # fallback (no branches found)
        new[key] = value
        return new

    def update_all_tickers(location, camelKey, default_value):
        path = Path(PATH_PORTFOLIO)

        with open(path, "r") as f:
            portfolio = json.load(f)

        for ticker, data in portfolio.items():

            if location == "ROOT":
                if camelKey not in data:
                    new = {}
                    inserted = False

                    for k, v in data.items():
                        if not inserted and isinstance(v, (dict, list)):
                            new[camelKey] = default_value
                            inserted = True
                        new[k] = v

                    if not inserted:
                        new[camelKey] = default_value

                    portfolio[ticker] = new

            else:
                if location in data and isinstance(data[location], dict):
                    if camelKey not in data[location]:
                        data[location][camelKey] = default_value

        with open(path, "w") as f:
            json.dump(portfolio, f, indent=4)

        console.print(f"[{color.DONE}]✔ Portfolio updated.[/]")

    def confirm_details(location, camelKey, default_value, type_choice, scope_choice, data_source, sourceKey):
        ui.show_fms_banner()
        # MENU
        console.print(f"[{color.base}]///[{color.DOS}]C:[{color.crmb}]\\SAVE[/][{color.ACTV}]\\{location.upper()}[/]>([{color.ACTV}]{camelKey}[/]: [{color.info}]{default_value}[/]) >> [{color.VAL}]template-portfolio.json --{scope_choice.lower()}[/][/]\n")
        # DETAILS
        console.print(f"[{color.info}]LOCATION[/]: [{color.info}]{location}[/]")
        console.print(f"[dim]KEY[/]: [{color.info}]{camelKey}[/]")
        console.print(f"[dim]TYPE[/]: [{color.info}]{type_choice}[/]")
        console.print(f"[dim]SCOPE[/]: [{color.info}]{scope_choice}[/]")
        console.print(f"[dim]SOURCE[/]: [{color.info}]{data_source}[/]")
        sourceKey_name = "" if data_source == "INTERNAL" else f"[dim]SOURCE KEY[/]: [{color.info}]{sourceKey}[/]"
        console.print(sourceKey_name)
        # INPUT
        return Confirm.ask("\nProceed?", default=True)



    # -<< STRUCTURE: ADD KEY FLOW
    # --- --- --- --- --- --- --- ---
    def structure_add_key_flow(location):
        # -------------------
        # ENTER KEY NAME
        # -------------------
        caller      = "config"
        config_type = "structure"
        input_page  = "add"

        # MENU
        ui.show_menu(
            breadcrumb=f"[{color.DOS}]C:[{color.crmb}]\\STRUCT[/][{color.ACTV}]\\ADD[/]>ECHO ([{color.inst}]Key name[/]_[/]: [{color.WARN}]null[/]) >> [{color.ACTV}]t-p.json[/]",
            options=[
                ("0", "BACK",   color.back),
            ],
            instruction="Enter key name",
            choice=False
        )
        # INPUT FIELD
        key_name = inp.input_field(caller, config_type, input_page)
        # BACK
        if not key_name or key_name == "0":
            return

        # -------------------
        # CHOOSE VALUE TYPE
        # -------------------
        camelKey   = util.camel_case(key_name)
        value_type = ui.show_menu(
            breadcrumb=f"[{color.DOS}]C:[{color.crmb}]\\STRUCT\\ADD[/][{color.ACTV}]\\TYPE[/]>ECHO ('[{color.VAL}]{camelKey}[/]': [{color.inst}]Key type[/]_[/]) >> [/][{color.ACTV}]t-p.json[/]",
            options=[
                ("0", "BACK",   color.back),
                ("1", "BOOL",   color.g1),
                ("2", "FLOAT",  color.g2),
                ("3", "STRING", color.g3),
            ],
            instruction="Choose value type",
            choice=True
        )
        # BACK
        if value_type == 0 or not value_type:
            return
        # VALUE TYPES
        if value_type == 1:
            type_choice   = "BOOLEAN"
            default_value = None
        elif value_type == 2:
            type_choice   = "FLOAT"
            default_value = None
        elif value_type == 3:
            type_choice   = "STRING"
            default_value = ""
        else:
            return

        # -------------------
        # DEFINE KEY SCOPE
        # -------------------
        s_choice = ui.show_menu(
            breadcrumb=f"[{color.DOS}]C:[{color.crmb}]\\STRUCTURE\\ADD\\{location.upper()}[/]>ECHO ('[{color.VAL}]{camelKey}[/]': [{color.inst}]{'string' if value_type == 3 else default_value}[/]) >> [{color.ACTV}]t-p.json[/] [{color.VAL}]--scope[/][{color.DOS}]_[/]",
            options=[
                ("0", "BACK",    color.back),
                ("1", "GLOBAL",  color.opt1),
                ("2", "PRIVATE", color.opt2),
                ("3", "PUBLIC",  color.opt3),
            ],
            instruction="Choose key scope",
            choice=True
        )
        # BACK
        if s_choice == 0 or not s_choice:
            return
        # SCOPES
        if s_choice == 1:
            scope_choice = "GLOBAL"
        elif s_choice == 2:
            scope_choice = "PRIVATE"
        elif s_choice == 3:
            scope_choice = "PUBLIC"
        else:
            return

        # -------------------
        # DEFINE DATA SOURCE
        # -------------------
        d_choice = ui.show_menu(
            breadcrumb=f"[{color.DOS}]C:[{color.crmb}]\\MAPPING\\ADD[/][{color.ACTV}]\\{scope_choice.upper()}[/]>EDIT ('[{color.VAL}]{camelKey}[/]': [{color.inst}]Data source[/]_[/]) >> [{color.ACTV}]reference-mapping.json[/]",
            options=[
                ("0", "BACK",     color.back),
                ("1", "INTERNAL", color.opt1),
                ("2", "EXTERNAL", color.opt2),
            ],
            instruction="Choose data source",
            choice=True
        )
        # BACK
        if d_choice == 0 or not d_choice:
            return
        # DATA
        elif d_choice == 1:
            data_source = "INTERNAL"
            sourceKey = None
            if not confirm_details(location, camelKey, default_value, type_choice, scope_choice, data_source, sourceKey):
                return
        elif d_choice == 2:
            data_source = "EXTERNAL"
        else:
            return

        # -------------------
        # SOURCE KEY NAME
        # -------------------
        if data_source == "EXTERNAL":
            ui.show_menu(
                breadcrumb=f"[{color.DOS}]C:[{color.crmb}]\\MAPPING\\ADD\\{scope_choice.upper()}\\[{color.ACTV}]EXTERNAL[/]>EDIT ('[{color.VAL}]{camelKey}[/]': [{color.inst}]Source key[/]_[/]) >> [{color.ACTV}]reference-mapping.json[/]",
                options=[
                    ("0", "BACK", color.back),
                ],
                instruction="Enter source key name",
                choice=False
            )
            # INPUT: Source Key Name
            sourceKey = inp.input_field(caller="config", config_type="mapping", input_page="add", placeholder="Enter source key name")
            # BACK
            if not sourceKey or sourceKey == "0":
                return
            else:
                if not confirm_details(location, camelKey, default_value, type_choice, scope_choice, data_source, sourceKey):
                    return

        # -------------------
        # SAVE TEMPLATE KEY
        # -------------------
        template = util.load_json(PATH_TEMPLATE)
        ticker = template["TICKER_SYMBOL"]
        # FIND SAVE LOCATION
        if location == "ROOT":
            ticker = insert_root_key(ticker, camelKey, default_value)
            template["TICKER_SYMBOL"] = ticker
        else:
            ticker[location][camelKey] = default_value
        # SAVE JSON
        util.save_json(PATH_TEMPLATE, template)
        # FEEDBACK
        console.print(f"\n[{color.DONE}]✔ KTemplate key added successfully.[/]")

        # -------------------
        # SAVE MAPPING KEYS
        # -------------------
        reference = util.load_json(PATH_MAPPING)

        pub = reference["PUBLIC"]
        pvt = reference["PRIVATE"]

        if data_source == "EXTERNAL":
            value = sourceKey
        else:
            value = default_value

        def ignore_default():
            if type_choice == "STRING":
                return ""
            return None

        if scope_choice == "GLOBAL":
            pub[camelKey] = value
            pvt[camelKey] = value

        elif scope_choice == "PUBLIC":
            pub[camelKey] = value
            pvt[camelKey] = ignore_default()

        elif scope_choice == "PRIVATE":
            pvt[camelKey] = value
            pub[camelKey] = ignore_default()

        util.save_json(PATH_MAPPING, reference)

        console.print(f"\n[{color.DONE}]✔ KMapping key added successfully.[/]")

        # -------------------
        # BACKUP PORTFOLIO
        # -------------------
        backup_portfolio_file()

        # -------------------
        # ADD KEY TO PORTFOLIO
        # -------------------
        update_all_tickers(location, camelKey, default_value)
        # -------------------
        # RECALCULATE
        # -------------------
        recalculate_baselines(scope_choice)

        # -------------------
        # REFRESH PORTFOLIO 
        # -------------------
        console.print(f"\n[{color.DONE}]✔ Baselines updated.[/]")
        console.print("[bold yellow]⚠ Structure changed — full refresh required[/bold yellow]\n")
        if Confirm.ask("Run full portfolio refresh now?", default=True):
            run_refresh()

    # -<< STRUCTURE: ADD MENU
    # --- --- --- --- --- --- --- ---
    def structure_add_menu():
        while True:
            branches = get_branches()
            ui.show_fms_banner()
            # MENU
            console.print(f"[{color.base}]///[{color.DOS}]C:[{color.crmb}]\\STRUCTURE[/][{color.ACTV}]\\ADD[/]>CD [{color.VAL}]location[/][/][{color.DOS}]_[/][/{color.base}]\n")
            # OPTIONS
            console.print(f"0. [{color.back}]BACK[/]")
            for i, b in enumerate(branches, 1):
                console.print(f"{i}. [{color.opt1}]{b}[/]")
            # INPUT
            choice = IntPrompt.ask("\n>_ ", default=0, show_default=False)
            # BACK
            if choice == 0:
                return
            # BRANCHES
            if 1 <= choice <= len(branches):
                location = branches[choice - 1]
                structure_add_key_flow(location)

    # END OF REFACTOR
    # === === === === === === === === R E F A C T O R



    # -<< GET BRANCH
    # --- --- --- --- --- --- --- ---
    def get_branches():
        template = util.load_json(PATH_TEMPLATE)
        ticker   = template["TICKER_SYMBOL"]
        branches = ["ROOT"]

        for k, v in ticker.items():
            if isinstance(v, dict) or isinstance(v, list):
                branches.append(k)

        return branches

    # -<< RUN REFRESH
    # --- --- --- --- --- --- --- ---
    def run_refresh():
        console.print(f"\n[{color.info}]Running full portfolio refresh...[/]\n")

        try:
            subprocess.run(["python", PATH_INCUBATOR, "--refresh"], check=True)
            console.print(f"\n[{color.DONE}]✔ Refresh complete.[/]\n")

        except subprocess.CalledProcessError:
            console.print(f"[{color.ERR}]✘ Refresh failed.[/]\n")

    # -<< RECALCULATIE BASELINE
    # --- --- --- --- --- --- --- ---
    def recalculate_baselines(scope):
        report = util.load_json(PATH_REPORT)
        p      = report["PORTFOLIO"]

        # increment totals
        p["leafNodesPtf"] += 1

        if scope == "GLOBAL":
            p["leafNodesPlc"] += 1
            p["leafNodesPvt"] += 1
        elif scope == "PUBLIC":
            p["leafNodesPlc"] += 1
        elif scope == "PRIVATE":
            p["leafNodesPvt"] += 1

        # recalculate scores
        p["scorePlc"] = round((p["leafNodesPlc"] / p["leafNodesPtf"]) * 100, 2)
        p["scorePvt"] = round((p["leafNodesPvt"] / p["leafNodesPtf"]) * 100, 2)
        p["scorePtf"] = round(((p["scorePlc"] * p["countPlc"]) + (p["scorePvt"] * p["countPvt"])) / p["countPtf"], 2)

        for ticker, data in report.items():
            if ticker == "PORTFOLIO":
                continue
            if ticker.endswith(".PVT"):
                data["score"] = p["scorePvt"]
            else:
                data["score"] = p["scorePlc"]

        util.save_json(PATH_REPORT, report)