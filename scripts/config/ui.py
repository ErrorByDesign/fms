    # ./scripts/config/ui.py
    # --- --- --- --- --- --- --- --- --- --- --- --- --- 
    # F M S   T E R M I N A L   -   U I
    # --- --- --- --- ---

    # -<< IMPORTS
    import sys
    import time

    # -<< IMPORTS: LOCAL
    import config.devops as dev
    import modules.operations as ops
    import scripts.config.globals as glob
    import scripts.config.definitions as define
    import scripts.config.colors as color
    import scripts.config.utils as util

    # -<< IMPORTS: RICH
    from rich import box
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.prompt import IntPrompt, Confirm
    from rich.table import Table
    from rich.text import Text

    # -<< CONSOLE
    console = Console()
    cw = console.width

    # -<< GLOBALS
    padding      = " " * ((cw - define.mhr_len) // 2)
    mhr_dbl_line = util.fit_to_width(define.mhr_dbl, define.mhr_pattern, define.mhr_sideL, define.mhr_sideR, define.mhr_sides, define.mhr_inner, define.mhr_inners)
    mhr_dvd_line = util.fit_to_width(define.mhr_dvd, define.mhr_pattern, define.mhr_sideL, define.mhr_sideR, define.mhr_sides, define.mhr_inner, define.mhr_inners)



    # -<< CLEAN PRINT
    # --- --- --- --- --- --- --- ---
    def clean_print(text: str, row: int = 27):
        """ C L E A N   P R I N T :
        Prints a clean, single-line instruction 
        string strictly at the specified row.
        """
        sys.stdout.write(f"\033[{row};1H\033[K")
        sys.stdout.flush()

        console.print(text, end="")
        sys.stdout.flush()



    # -<< SHOW MENU
    def show_menu(breadcrumb, options, instruction="", rows=10, choice=True, prompt="", row_bg=""):
        print("\033[2J\033[H", end="")
        # Render FMS banner, menu breadcrumb and options
        show_fms_banner(dev.debug)
        console.print(f"\n[{color.BASE}]///{breadcrumb}[/]\n")

        for i, opt in enumerate(options):
            key, label, fg = opt[0], opt[1], opt[2]
            fg = color.exit if key == '0' else fg

            # Per-row bg overrides row_bg; row_bg can be a str or (even, odd) tuple
            if len(opt) >= 4:
                bg = opt[3]
            elif isinstance(row_bg, tuple):
                bg = row_bg[i % 2]          # alternates: even rows → row_bg[0], odd → row_bg[1]
            else:
                bg = row_bg

            fg_on_bg = f"{fg} on {bg}" if bg else fg
            console.print(f"[{color.base}][{fg_on_bg}]{key}.[/] [{fg_on_bg}]{label}[/][/]")

        # Pad remaining rows so the prompt always appears at the same vertical position
        rendered = len(options)
        for _ in range(max(0, rows - rendered)):
            console.print()

        # Determine output and input row positions
        trmx_rows = ops.terminal_size()[0]
        if not trmx_rows:
            inpt_row = 30
        else:
            inpt_row = trmx_rows - 1
        inst_row = inpt_row - 2

        # Show debug (if in developer mode) and page instructions (optional)
        debug = "[DEBUG MODE ENABLED] " if dev.debug == True else ""
        instruct = f"[{color.base}][{color.WARN}]{debug}[/][{color.inst}]{instruction}[/][/]"

        # Call clean print to position instructions row
        clean_print(text=instruct, row=inst_row)

        # Create prompt clas and define style
        class CleanIntPrompt(IntPrompt):
            prompt_suffix = ""
        if prompt == "":
            prompt_style = define.prompt_X
        elif prompt == "F":
            prompt_style = define.prompt_f
        elif prompt == "FMSL":
            prompt_style = define.prompt_FMSL
        elif prompt == "x":
            prompt_style = define.prompt_x
        elif prompt == "X":
            prompt_style = define.prompt_X
        elif prompt == "xrxs":
            prompt_style = define.prompt_xrxs
        elif prompt == "XRXS":
            prompt_style = define.prompt_XRXS
        elif prompt == "xxxx":
            prompt_style = define.prompt_xxxx
        else:
            prompt_style = "X:\\> "

        # Show user input prompt and return choice
        if choice == True:
            sys.stdout.write(f"\033[{inpt_row};1H")
            sys.stdout.flush()
            choice = CleanIntPrompt.ask(f"[{color.DOS}]{prompt_style}[/]", default=0, show_default=False, show_choices=False)
            console.print("")
            return choice



    # -<< FMS BANNER
    # --- --- --- --- --- --- --- ---
    def show_fms_banner(debug=False):
        if debug == False:
            console.clear()
        fms_title    = util.fit_to_width(define.fms_str, define.fms_pttrn_str, define.fms_sideL_str, define.fms_sideR_str, define.fms_sides, define.fms_inner, define.fms_inners)
        fms_subtitle = util.fit_to_width(define.fms_str_sub, define.fms_pttrn_str, define.fms_sideL_str, define.fms_sideR_str, define.fms_sides, define.fms_inner, define.fms_inners)
        fms_line_top = util.fit_to_width(define.fms_top, define.fms_pattern, define.fms_topL, define.fms_topR, define.fms_sides, define.fms_inner, define.fms_inners)
        fms_line_btm = util.fit_to_width(define.fms_btm, define.fms_pattern, define.fms_btmL, define.fms_btmR, define.fms_sides, define.fms_inner, define.fms_inners)
        console.print(f"[{color.bnrd1}]{fms_line_top}[/]")
        console.print(f"[{color.BNNR1}]{fms_title}[/]")
        console.print(f"[{color.bnnr1}]{fms_subtitle}[/]")
        console.print(f"[{color.bnrd1}]{fms_line_btm}[/]")

    # -<< MERGER HEADLESS BANNER
    # --- --- --- --- --- --- --- ---
    def merger_headless_banner():
        ahu_title = util.fit_to_width(define.ahu_str, define.ahu_pattern, define.ahu_sideL, define.ahu_sideR, define.ahu_sides, define.ahu_inner, define.ahu_inners)
        ahu_lines = util.fit_to_width(define.ahu_dot, define.ahu_pattern, define.ahu_sideL, define.ahu_sideR, define.ahu_sides, define.ahu_inner, define.ahu_inners)
        console.print(f"\n[{color.bnrd2}]{ahu_lines}[/]")
        console.print(f"\n[{color.BNNR2}]{ahu_title}[/]")
        console.print(f"\n[{color.bnrd2}]{ahu_lines}[/]\n")

    # -<< MERGER HEALTH BANNER
    # --- --- --- --- --- --- --- ---
    def merger_health_banner():
        mhr_title    = util.fit_to_width(define.mhr_str, define.mhr_pattern, define.mhr_sideL, define.mhr_sideR, define.mhr_sides, define.mhr_inner, define.mhr_inners)
        mhr_dvd_line = util.fit_to_width(define.mhr_dvd, define.mhr_pattern, define.mhr_sideL, define.mhr_sideR, define.mhr_sides, define.mhr_inner, define.mhr_inners)
        console.print(f"\n[{color.BNNR3}]{mhr_title}[/]")
        console.print(f"[{color.bnrd3}]{mhr_dbl_line}[/]")

    # -<< MERGER REFRESH DNA MUTATIONS
    # --- --- --- --- --- --- --- ---
    def merger_refresh_dna_mutations(corrupted_tickers, PATH_REFRESH, PATH_REFRESH_CORRUPTED):
        console.print(f"{padding}[{color.info}][{color.ERR}]ERROR[/]: Structural mismatch detected.\n[{color.FAIL}]Mutated embryo(s)[/]: [{color.FAIL}]{', '.join(corrupted_tickers)}[/].[/]")
        console.print(f"{padding}[{color.info}][{color.FAIL}]Quarantined mother[/]:\n[{color.DOS}]{PATH_REFRESH}[/] to \n[{color.FAIL}]{PATH_REFRESH_CORRUPTED}[/].[/]")

    # -<< MERGER REFRESH CORRECT CHROMOSOMES
    # --- --- --- --- --- --- --- ---
    def merger_refresh_correct_chromosomes(ticker, stock_type, p, rep_ptf, score, baseline):
        console.print(f"\n[{color.bnrd4}]{mhr_dvd_line}[/]")
        console.print(f"{padding}[{color.BNNR4}]TEST SUBJECT[/]"
                      f"\n{padding}[{color.base}][{color.bnnr4}]Embryo[/]:[/] [{color.ACTV}]{ticker}[/]"
                      f"\n{padding}[{color.base}][{color.bnnr4}]Sex[/]:[/] [{color.DONE}]{stock_type.capitalize()}[/]"
                      f"\n{padding}[{color.base}][{color.bnnr4}]Chromosomes[/]: [{color.VAL}]{p}[/] ([{color.DONE}]expected[/]: [{color.PASS}]{rep_ptf['leafNodesPlc' if stock_type == 'PUBLIC' else 'leafNodesPvt']}[/])[/]"
                      f"\n{padding}[{color.base}][{color.bnnr4}]Score[/]: [{color.PASS}]{score}%[/] ([{color.DONE}]expected[/]: [{color.PASS}]{baseline}%[/])[/]"
                      f"\n{padding}[{color.base}][{color.bnnr4}]Result[/]:[/] [{color.PASS}]PASSED[/]")

    # -<< MERGER REFRESH CORRUPT CHROMOSOMES
    # --- --- --- --- --- --- --- ---
    def merger_refresh_corrupt_chromosomes(ticker, stock_type, p, rep_ptf, score, baseline):
        console.print(f"\n[{color.bnrd2}]{mhr_dbl_line}[/]")
        console.print(f"{padding}[{color.BNNR2}]TEST SUBJECT[/]"
                      f"\n{padding}[{color.base}][{color.bnnr2}]Embryo[/]:[/] [{color.WARN}]{ticker}[/]"
                      f"\n{padding}[{color.base}][{color.bnnr2}]Sex[/]:[/] [{color.WARN}]{stock_type.capitalize()}[/]"
                      f"\n{padding}[{color.base}][{color.bnnr2}]Chromosomes[/]: [{color.FAIL}]{p}[/] ([{color.DONE}]expected[/]: [{color.PASS}]{rep_ptf['leafNodesPlc' if stock_type == 'PUBLIC' else 'leafNodesPvt']}[/])[/]"
                      f"\n{padding}[{color.base}][{color.bnnr2}]Score[/]: [{color.FAIL}]{score}%[/] ([{color.DONE}]expected[/]: [{color.PASS}]{baseline}%[/])[/]"
                      f"\n{padding}[{color.base}][{color.bnnr2}]Result[/]:[/] [{color.FAIL}]FAILED[/]")
        console.print(f"[{color.bnrd2}]{mhr_dbl_line}[/]")

    # -<< MERGER REFRESH MISSING CHROMOSOMES
    # --- --- --- --- --- --- --- ---
    def merger_refresh_missing_chromosomes(mismatched_tickers):
        console.print(f"\n{padding}[{color.info}][{color.WARN}]WARNING[/]: Missing chromosomes detected in [{color.FAIL}]{', '.join(mismatched_tickers)}[/].[/]")
        console.print(f"{padding}[{color.info}][{color.WARN}]Check the final health report for more details[/].[/]")
        console.print(f"{padding}[{color.info}][{color.DONE}]Proceeding with swap[/]. Frontend analysis needed.[/]")
        # console.print(f"{padding}[{color.info}]Frontend analysis recommended.[/]")

    # -<< MERGER REFRESH HEALTH SUMMARY
    # --- --- --- --- --- --- --- ---
    def merger_refresh_health_summary(rep_ptf, leaf_nodes_ptf, count_plc, count_pvt, calc_score):
        console.print(f"{padding}[{color.crmb}][{color.p1}]Stock count PTF[/]: [{color.VAL}]{rep_ptf['countPtf']}[/]      ||     [{color.r1}]Leaf nodes PTF[/]: [{color.VAL}]{leaf_nodes_ptf}[/]")
        console.print(f"{padding}[{color.crmb}][{color.p2}]Stock count PLC[/]: [{color.VAL}]{count_plc}[/]      ||     [{color.r2}]Leaf nodes PLC[/]:[/] [{color.VAL}]{rep_ptf['leafNodesPlc']}[/]")
        console.print(f"{padding}[{color.crmb}][{color.p3}]Stock count PVT[/]: [{color.VAL}]{count_pvt}[/]      ||     [{color.r3}]Leaf nodes PVT[/]:[/] [{color.VAL}]{rep_ptf['leafNodesPvt']}[/]")
        console.print(f"{padding}[{color.crmb}][{color.ACTV}]Calculated score[/]:[/] [{color.VAL}]{calc_score}[/]")
        console.print(f"[{color.bnrd3}]{mhr_dbl_line}[/]")

    # -<< MERGER REFRESH FINAL MESSAGE
    # --- --- --- --- --- --- --- ---
    def merger_refresh_final_message(PATH_REPORT):
        msg0 = f"\n{padding}[{color.info}][{color.PASS}]SUCCESS[/]: Macro DNA verified. Portfolio swapped[/]"
        msg1 = f"\n{padding}[{color.info}][{color.DONE}]FINDINGS[/]: Health audit complete. Report signed off[/]"
        msg2 = f"{padding}[{color.DOS}]{PATH_REPORT}[/]"
        msg3 = f"\n{padding}[{color.PASS}][{color.ACTV}]AUTOMATION[/]: Headless update complete.[/]"
        msg4 = f"\n{padding}[{color.DONE}]Pushed files to FMS frontend.[/]\n"
        util.show_task_result(msg0, True)
        util.show_task_result(msg1, True)
        util.show_task_result(msg2, True)
        util.show_task_result(msg3, True)
        util.show_task_result(msg4, True)
        console.print("")

    # -<< MERGER RESET HEALTH SUMMARY
    # --- --- --- --- --- --- --- ---
    def merger_reset_health_summary(leaf_nodes_plc, leaf_nodes_pvt, leaf_nodes_ptf, count_plc, count_pvt, count_ptf, score_plc, score_pvt, score_ptf):
        console.print(f"\n[{color.BNNR3}]=== RESET SUMMARY ===[/]")
        s_table = Table(show_header=False, box=None)
        util.add_row(s_table, f"[{color.base}][{color.y1}]CHROMOSOME COUNT (PLC)[/]:[/]", leaf_nodes_plc, lambda x: f"[{color.VAL}]{x}[/]")
        util.add_row(s_table, f"[{color.base}][{color.y2}]CHROMOSOME COUNT (PVT)[/]:[/]", leaf_nodes_pvt, lambda x: f"[{color.VAL}]{x}[/]")
        util.add_row(s_table, f"[{color.base}][{color.y3}]CHROMOSOME COUNT (PTF)[/]:[/]", leaf_nodes_ptf, lambda x: f"[{color.VAL}]{x}[/]")
        util.add_row(s_table, "", " ")
        util.add_row(s_table, f"[{color.base}][{color.y4}]EMBRYO COUNT (PLC)[/]:[/]",     count_plc,      lambda x: f"[{color.VAL}]{x}[/]")
        util.add_row(s_table, f"[{color.base}][{color.y5}]EMBRYO COUNT (PVT)[/]:[/]",     count_pvt,      lambda x: f"[{color.VAL}]{x}[/]")
        util.add_row(s_table, f"[{color.base}][{color.y6}]EMBRYO COUNT (PTF)[/]:[/]",     count_ptf,      lambda x: f"[{color.VAL}]{x}[/]")
        util.add_row(s_table, "", " ")
        util.add_row(s_table, f"[{color.base}][{color.r1}]HEALTH SCORE (PLC)[/]:[/]",     score_plc,      lambda x: f"[{color.VAL}]{x}%[/]")
        util.add_row(s_table, f"[{color.base}][{color.r2}]HEALTH SCORE (PVT)[/]:[/]",     score_pvt,      lambda x: f"[{color.VAL}]{x}%[/]")
        util.add_row(s_table, f"[{color.base}][{color.r3}]HEALTH SCORE (PTF)[/]:[/]",     score_ptf,      lambda x: f"[{color.VAL}]{x}%[/]")
        console.print(s_table)
        console.print(f"\n[{color.DONE}]Reset completed successfully.[/]\n")

    # -<< WIKI PANEL
    # --- --- --- --- --- --- --- ---
    def wiki_panel(script, wiki):
        key     = "incubator.py" if script == "search" else "updata.sh"
        info    = wiki.get("DIRECTORY_STRUCTURE", {}).get("SCRIPTS", {}).get(key, {})
        owner   = info.get("OWNER",   "Unknown")
        usage   = info.get("USAGE",   "Unknown")
        version = info.get("VERSION", "Unknown")
        about   = info.get("ABOUT",   "\nNo description available.\n")

        t = Table(show_header=True, box=box.ROUNDED, padding=(0, 1))
        t.add_column("PROPERTY", header_style=f"{color.BNNR1}", style=f"{color.bnrd1}")
        t.add_column("DETAILS", header_style=f"{color.BNNR3}", style=f"{color.bnrd3}")
        # util.add_row(t, " ", " ")
        util.add_row(t, f"[{color.info}][{color.p1}]FILE[/]:[/]",           key,     lambda x: f"[{color.DOS}]{x}[/]")
        util.add_row(t, f"[{color.info}][{color.g1}]METADATA[/]:[/]", " ")
        util.add_row(t, f"[{color.info}]• [{color.bnnr1}]OWNER[/]:[/]",     owner,   lambda x: f"[{color.BNNR1}]{x}[/]")
        util.add_row(t, f"[{color.info}]• [{color.bnnr2}]USAGE[/]:[/]",     usage,   lambda x: f"[{color.BNNR2}]{x}[/]")
        util.add_row(t, f"[{color.info}]• [{color.bnnr3}]VERSION[/]:[/]",   version, lambda x: f"[{color.BNNR3}]{x}[/]")
        util.add_row(t, " ", " ")
        util.add_row(t, f"[{color.info}][{color.bnnr4}]DESCRIPTION[/]:[/]", about,   lambda x: f"[{color.info}]{x}[/]")
        # util.add_row(t, " ", " ")
        return Panel(t, title=f"[{color.BNNR4}]WIKIPEDIA[/]", subtitle=f"[{color.bnnr4}]{script.capitalize()}[/]", border_style=f"{color.trmx_dark2}", style=f"on {color.trmx_lite1}")