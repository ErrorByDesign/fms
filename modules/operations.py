#!/usr/bin/env python3
# -----------------------------------------------
# X E R X E S   O P E R A T I O N S   M O D U L E
#------------
import os
import shutil
import time
import zipfile
from datetime import datetime
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console

console = Console()

# BACKUP PROCESS
# --------------
def backup_project():
    # 0. SET PATHS
    root_dir = Path(__file__).parent.parent.absolute()
    backup_base = root_dir / "backup"
    # EXACT PATH PROVIDED: ./data/cache
    cache_dir = root_dir / "data" / "cache"
    
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    folder_name = f"{root_dir.name}_{timestamp}"
    
    temp_folder = backup_base / folder_name
    zip_file = backup_base / f"{folder_name}.zip"
    
    items_to_backup = ["config", "data", "documentation", "modules", "scripts", "index.html", "script.js", "style.css", "main.py"]

    try:
        backup_base.mkdir(exist_ok=True)
        
        console.print("\n[bold dark_olive_green]INITIATING BACKUP SEQUENCE...[/bold dark_olive_green]\n")

        # THE RICH LIVE ENVIRONMENT (transient=False keeps it on screen)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
            transient=False 
        ) as progress:
            
            task = progress.add_task("[cyan]Executing 4-Step Protocol...", total=4)

            # --- STEP 1: STAGING ---
            progress.update(task, description=f"[yellow]Step 1: Staging [bold khaki3]{folder_name}[/bold khaki3]...[/yellow]")
            temp_folder.mkdir(parents=True, exist_ok=True)
            for item in items_to_backup:
                src = root_dir / item
                if src.exists():
                    dst = temp_folder / item
                    if src.is_dir():
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
            progress.update(task, advance=1)
            console.print(f"[light_coral]✔[/light_coral] [bold]Staged[/bold]: [bold steel_blue1]{temp_folder.name}[/bold steel_blue1]")
            time.sleep(1)
 
            # --- STEP 2: ARCHIVING ---
            progress.update(task, description=f"[light_coral][bold]Step 2[/bold]: Creating [bold steel_blue1]{zip_file.name}[/bold steel_blue1]...[/light_coral]")
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(temp_folder):
                    for file in files:
                        fp = Path(root) / file
                        zf.write(fp, arcname=fp.relative_to(temp_folder))
            progress.update(task, advance=1)
            console.print(f"[light_coral]✔[/light_coral][navajo_white1] Archive Created.[/navajo_white1]")
            time.sleep(1)

            # --- STEP 3: CLEAN BACKUP DIR ---
            progress.update(task, description="[navajo_white1][bold]Step 3[/bold]: Cleaning backup directory...[/navajo_white1]")
            for item in backup_base.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                    console.print(f"[indian_red1]×[/indian_red1][navajo_white1] Deleted folder: [/navajo_white1][bold khaki3]{item.name}[/bold khaki3]")
                    time.sleep(1)
                elif item.is_file() and item.suffix != ".zip":
                    item.unlink()
                    console.print(f"[bold indian_red1]×[/bold indian_red1][navajo_white1] Deleted file: [/navajo_white1][bold khaki3]{item.name}[/bold khaki3]")
                    time.sleep(1)
            progress.update(task, advance=1)

            # --- STEP 4: WIPE CACHE ---
            progress.update(task, description=f"[magenta]Step 4: Wiping [bold khaki3]{cache_dir}[/bold khaki3]...[/magenta]")
            # if cache_dir.exists():
            #     for item in cache_dir.iterdir():
            #         if item.is_file() or item.is_symlink():
            #             item.unlink()
            #             console.print(f"[bold indian_red1]×[/bold indian_red1][navajo_white1] Nuked cache file: [/navajo_white1][bold khaki3]{item.name}[/bold khaki3]")
            #             time.sleep(1)
            #         elif item.is_dir():
            #             shutil.rmtree(item)
            #             console.print(f"[bold indian_red1]×[/bold indian_red1][navajo_white1] Nuked cache folder: [/navajo_white1][bold khaki3]{item.name}[/bold khaki3]")
            #             time.sleep(1)
            # else:
            #     console.print(f"[bold yellow]![/bold yellow][/navajo_white1] Cache not found at: [/navajo_white1][bold khaki3]{cache_dir}[/bold khaki3]")
            console.print("SKIPPING CACHE FOLDER.")
            progress.update(task, advance=1)

        return True

    except Exception as e:
        console.print(f"\n[bold red]CRITICAL FAILURE:[/bold red] {e}")
        time.sleep(3)
        return False

# MODULE GATE
# -----------
if __name__ == "__main__":
    if backup_project():
        console.print("\n[bold light_cyan1]BACKUP COMPLETE.[/bold light_cyan1]")
        time.sleep(1)
    else:
        console.print("\n[bold light_coral]BACKUP FAILED.[/bold light_coral]")
        time.sleep(3)
