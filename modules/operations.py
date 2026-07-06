        # -<< IMPORTS
        import os
        import re                                 
        import shutil
        import sys
        import time
        import zipfile
        from datetime import datetime
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

        # -<< IMPORTS: LOCAL
        import scripts.config.colors as color
        import scripts.config.utils as util

        # -<< IMPORTS: RICH
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
        console = Console()

        # =<< PATHS
        DIR_ROOT   = Path(__file__).parent.parent.absolute()
        DIR_BACKUP = DIR_ROOT / "backup"



        # -<< PROTECTED FILES
        # --- --- --- --- --- --- --- ---
        def protected_files():
            # COLLECT THE "SAFE" FILESs
            safe_files = []
            for item in DIR_BACKUP.iterdir():
                if item.is_file() and item.suffix != ".zip":
                    # Check if it is a protected backup file (contains 'bck' or 'backup')
                    if "bak" in item.name or "bck" in item.name or "backup" in item.name:
                        # Get modification time
                        m_time = datetime.fromtimestamp(item.stat().st_mtime)
                        # Append to the safe list
                        safe_files.append({
                            "name": item.name,
                            "path": item,
                            "modified": m_time
                        })

            # SORT THE LIST (oldest to newest)
            safe_files.sort(key=lambda x: x["modified"]) 

            # RETURN SORTED LIST
            return safe_files

        # -<< BACKUP PROCESS
        # --- --- --- --- --- --- --- ---
        def backup_project():
            # PREPARE FRAMEWORK
            timestamp   = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            folder_name = f"{DIR_ROOT.name}_{timestamp}"
            temp_dir    = DIR_BACKUP / folder_name
            zip_file    = DIR_BACKUP / f"{folder_name}.zip"

            # LIST BACKUP ITEMS
            items_to_backup = [".git", ".github", "config", "css", "data", "documentation", "fonts", "modules", ".gitignore", "scripts", "index.html", "main.py", "script.js", "style.css"]

            # BEGIN BACKUP PROCESS
            try:
                DIR_BACKUP.mkdir(exist_ok=True)

                console.print(f"🔄 [{color.ACTV}]Executing 4-Step Protocol[/]")
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console, transient=False) as progress:
                    task = progress.add_task(f"🔄 [{color.crmb}]Preparing...[/]", total=4)
                    time.sleep(3)

                    # --- STEP 1: STAGING ---
                    progress.update(task, description=f"⌛ [{color.base}][{color.ACTV}]STEP 1[/]: Staging [{color.DOS}]{folder_name}[/][/]")

                    temp_dir.mkdir(parents=True, exist_ok=True)

                    for item in items_to_backup:
                        src = DIR_ROOT / item
                        if src.exists():
                            dst = temp_dir / item
                            if src.is_dir():
                                shutil.copytree(src, dst, dirs_exist_ok=True)
                            else:
                                shutil.copy2(src, dst)

                    progress.update(task, advance=1)
                    console.print(f"✅ [{color.base}][{color.DONE}]STAGED[/]: [{color.DOS}]{temp_dir.name}[/][/]")

                    # --- STEP 2: ARCHIVING ---
                    progress.update(task, description=f"💾 [{color.base}][{color.ACTV}]STEP 2[/]: Creating [{color.DOS}]{zip_file.name}[/][/]")

                    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for root, _, files in os.walk(temp_dir):
                            for file in files:
                                fp = Path(root) / file
                                zf.write(fp, arcname=fp.relative_to(temp_dir))

                    progress.update(task, advance=1)
                    console.print(f"📦 [{color.DONE}]Archive Created[/]")

                    # --- STEP 3: RETENTION POLICY ---
                    progress.update(task, description=f" [{color.base}][{color.ACTV}]STEP 3[/]: Executing retention policy[/]")

                    today_str = timestamp.split('T')[0]     # e.g. "2026-06-30"
                    zip_files = [p for p in DIR_BACKUP.iterdir() if p.is_file() and p.suffix == ".zip"]

                    backups_by_date = {}

                    for p in zip_files:
                        # Expected pattern: <ProjectName>_YYYY-MM-DDTHH-MM-SS.zip
                        m = re.search(r'_(\d{4}-\d{2}-\d{2})T(\d{2}-\d{2}-\d{2})\.zip$', p.name)
                        # skip files that don't match the naming convention
                        if not m:
                            continue
                        # "YYYY-MM-DD"
                        date_part = m.group(1)
                        # "HH-MM-SS"
                        time_part = m.group(2)
                        dt = datetime.strptime(f"{date_part}T{time_part}", "%Y-%m-%dT%H-%M-%S")
                        backups_by_date.setdefault(date_part, []).append((p, dt))

                    for date_key, entries in backups_by_date.items():
                        # Keep all backups created today
                        if date_key == today_str:
                            continue
                        # Sort entries by datetime descending (newest first)
                        entries.sort(key=lambda x: x[1], reverse=True)
                        # Preserve the newest; delete the rest
                        for p, _ in entries[1:]:
                            p.unlink()
                            console.print(f"✅ [{color.base}][{color.ACTV}]DELETE[/]: Old backup [{color.DOS}]{p.name}[/] deleted[/]")

                    progress.update(task, advance=1)
                    console.print(f"📦 [{color.DONE}]Purged all backups from previous date groups keeping the latest per group[/]")

                    # --- STEP 4: CLEAN BACKUP DIRECTORY ---
                    progress.update(task, description=f"🧹 [{color.base}][{color.ACTV}]STEP 4[/]: Cleaning backup directory[/]")

                    for item in DIR_BACKUP.iterdir():
                        # Delete folders inside the backup directory
                        if item.is_dir():
                            shutil.rmtree(item)
                            console.print(f"✅ [{color.base}][{color.ACTV}]DELETE[/]: Folder [{color.DOS}]{item.name}[/] deleted[/]")
                            time.sleep(1)
                        # Delete all files inside the backup directory excluding ones with a .zip extension and files with 'bck' or 'backup' as part of the filename
                        elif item.is_file() and item.suffix != ".zip" and ("bck" not in item.name and "backup" not in item.name):
                            item.unlink()
                            console.print(f"✅ [{color.base}][{color.ACTV}]DELETE[/]: File [{color.DOS}]{item.name}[/] deleted[/]")
                            time.sleep(1)

                    progress.update(task, description="")
                    progress.update(task, advance=1)

                # Fetch and print the list of protected files that were not purged
                safe_files = protected_files()
                if safe_files:
                    console.print(f"\n[{color.base}][{color.info}]Found [{color.VAL}]{len(safe_files)}[/] protected backup files ([{color.crmb}]oldest to newest[/])[/]:[/]")
                    console.print(f"[{color.BASE}][{color.ACTV}]{'Modified Date':<25}[/] | [{color.DOS}]{'Filename'}[/][/]")
                    line = "-" * 50
                    console.print(f"[{color.bnrd4}]{line}[/]")

                    for file in safe_files:
                        date_str = file["modified"].strftime("%Y-%m-%dT%H-%M-%S")
                        console.print(f"[{color.BASE}][{color.ACTV}]{date_str}[/] | [{color.DOS}]{file['name']}[/][/]")

                console.print(f"✅ [{color.DONE}]BACKUP COMPLETE[/]")

                return True

            # HANDLE BACKUP ERRORS
            except Exception as e:
                msg = f"[{color.info}]Critical failure occured during project backup process. \n[{color.inst}]Check the backup directory in root at [{color.DOS}]{DIR_BACKUP}[/] for further analysis[/].[/]" if e == "" else e
                util.pause(reason="e", message=msg, enter="e")
                console.print("")
                sys.exit(1)

        # -<< GET TERMINAL SIZE
        # --- --- --- --- --- --- --- ---
        def terminal_size():
            size = os.get_terminal_size()
            return size.lines, size.columns
            # print(f"Rows: {size.lines}, Columns: {size.columns}")

        # -<< GET TERMINAL COLOR
        # --- --- --- --- --- --- --- ---
        def terminal_color():
            path = Path.home() / ".termux" / "colors.properties"
            for line in path.read_text().splitlines():
                line = line.strip()
                if line.startswith("background="):
                    return line.split("=", 1)[1].strip()
            raise ValueError("background not found")



        # --- --- --- --- --- --- --- ---
        # =<< MODULE GATE >>- --- --- ---
        if __name__ == "__main__":
            if "--backup" in sys.argv:                     # added missing colon
                backup_project()
            elif "--terminal" in sys.argv:
                terminal_size()
                terminal_color()
            else:
                sys.exit(0)