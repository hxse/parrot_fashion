import re
import subprocess
import time
import os
from pathlib import Path
import json
from rich import print


def get_config_anki_path():
    """从配置文件获取 Anki 路径"""
    try:
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)
            if "anki_app" in config:
                path = Path(config["anki_app"])
                if path.exists():
                    return path
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None


def get_default_anki_path1():
    """获取默认 Anki 路径1 (APPDATA)"""
    appdata = os.getenv("APPDATA")
    if appdata:
        path = Path(appdata).parent / "Local/Programs/Anki/anki.exe"
        if path.exists():
            return path
    return None


def get_default_anki_path2():
    """获取默认 Anki 路径2 (scoop)"""
    path = Path("C:/Users/qmlib/scoop/apps/anki/current/anki.exe")
    if path.exists():
        return path
    return None


# 获取 Anki 应用程序路径
config_path = get_config_anki_path()
default_path1 = get_default_anki_path1()
default_path2 = get_default_anki_path2()

if config_path:
    anki_app = config_path
    print(f"[bold green]使用配置文件中的 Anki 路径: {anki_app}[/bold green]")
elif default_path1:
    anki_app = default_path1
    print(f"[bold green]使用默认路径1: {anki_app}[/bold green]")
elif default_path2:
    anki_app = default_path2
    print(f"[bold green]使用默认路径2: {anki_app}[/bold green]")
else:
    print("[bold red]无法找到 Anki 应用程序，请手动配置路径[/bold red]")
    anki_app = None


def import_anki_apkg(import_anki, ankiPath, anki_app=anki_app, sleep=0.6):
    if anki_app is None:
        print("[bold red]Anki 应用程序路径未设置，无法导入文件[/bold red]")
        return

    # 处理可能的路径长度限制问题
    if not ankiPath.is_file():
        # 尝试使用长路径前缀
        long_path = Path("\\\\?\\" + str(ankiPath))
        if long_path.is_file():
            ankiPath = long_path
        else:
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
