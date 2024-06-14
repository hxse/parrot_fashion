import re
import subprocess
import time
import os
from pathlib import Path
import json

with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)
    if "anki_app" in config:
        anki_app = config["anki_app"]
    else:
        anki_app = Path(os.getenv("APPDATA")).parent / "Local/Programs/Anki/anki.exe"


def import_anki_apkg(import_anki, ankiPath, anki_app=anki_app, sleep=0.6):
    if not ankiPath.is_file():
        print(f"[bold red]检测不到anki文件: {ankiPath}[/bold red]")
        return
    try:
        m = re.search(import_anki, ankiPath.name)
    except TypeError as e:
        print(f"[bold red]检测到正则表达式不合标准: {import_anki}[/bold red]")
        return
    if m:
        command = rf'"{anki_app}" "{ankiPath.as_posix()}"'
        print(command)
        subprocess.run(command)
        time.sleep(sleep)
