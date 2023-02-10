#!/usr/bin/env python3
# coding: utf-8
import fire
from pathlib import Path
import subprocess
from autosub_tool import fix_unicode_bug, auto_trans_srt
from gen_anki import gen_apkg, different_mode
from rich import print
import json
from operate_srt import run_operate_srt


def print_check(
    audioPath,
    srtPath,
    srt2Path,
    ankiPath,
    srtPathHandle,
    srt2PathHandle,
    ankiPathHandle,
    operate_mode,
):
    boolRich = lambda x: (
        f"[bold green]{x}[/bold green]" if x else f"[bold red]{x}[/bold red]"
    )
    if operate_mode not in ["", False, 0, None]:
        obj = {
            "audio": audioPath.is_file(),
            "o-srt": srtPath.is_file(),
            "o-srt2": srt2Path.is_file(),
            "o-anki": ankiPath.is_file(),
            "o-srtHandle": srtPathHandle.is_file(),
            "o-srt2Handle": srt2PathHandle.is_file(),
            "o-ankiHandle": ankiPathHandle.is_file(),
        }
    else:
        obj = {
            "audio": audioPath.is_file(),
            "srt": srtPath.is_file(),
            "srt2": srt2Path.is_file(),
            "anki": ankiPath.is_file(),
            "srtHandle": srtPathHandle.is_file(),
            "srt2Handle": srt2PathHandle.is_file(),
            "ankiHandle": ankiPathHandle.is_file(),
        }
    text = " ".join([f"{i}: {boolRich(obj[i])}" for i in obj])
    print(text)
    return obj


def run_check(checkList, operate_mode):
    if len(checkList) == 0:
        return
    if operate_mode not in ["", False, 0, None]:
        statistics = {
            "audio": {"success": 0, "failed": 0},
            "o-srt": {"success": 0, "failed": 0},
            "o-srt2": {"success": 0, "failed": 0},
            "o-anki": {"success": 0, "failed": 0},
            "o-srtHandle": {"success": 0, "failed": 0},
            "o-srt2Handle": {"success": 0, "failed": 0},
            "o-ankiHandle": {"success": 0, "failed": 0},
        }
    else:
        statistics = {
            "audio": {"success": 0, "failed": 0},
            "srt": {"success": 0, "failed": 0},
            "srt2": {"success": 0, "failed": 0},
            "anki": {"success": 0, "failed": 0},
            "srtHandle": {"success": 0, "failed": 0},
            "srt2Handle": {"success": 0, "failed": 0},
            "ankiHandle": {"success": 0, "failed": 0},
        }
    for l in checkList:
        for i in l:
            if l[i]:
                statistics[i]["success"] += 1
            else:
                statistics[i]["failed"] += 1
    result = [
        f"{i}: {statistics[i]['success']}/{statistics[i]['success']+statistics[i]['failed']}"
        for i in statistics
    ]
    print(" ".join(result))


def import_anki_apkg(import_anki, anki_app, ankiPath, sleep=0.5):
    import re, time

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


def loop(
    dirPath,
    enable_whisperx=True,
    enable_translate=True,
    enable_anki=True,
    handle="auto",  # auto,handle,current,all
    skip=0,
    check=False,
    operate_mode=None,
    import_anki=None,
    anki_app=None,
    start_offset=0,
    end_offset=0,
    over_start=1,
    over_end=1,
    key=None,
):
    """
    pdm run python .\loop_whisper.py loop "d:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos" 1 1 1 --handle auto
    """
    dirPath = Path(fix_unicode_bug(dirPath))
    if not dirPath.is_dir():
        raise f"dirPath,不是文件夹 {dirPath}"
    pathList = [i for i in Path(dirPath).rglob("*.mp3") if i.parent.name != "_cache"]
    checkList = []
    for index, value in enumerate(pathList):
        if skip > index:
            print(f"skip {index + 1}/{len(pathList)} {value.name}")
            continue
        if key and key not in value.name:
            continue
        print(f"run  {index + 1}/{len(pathList)} [bold black]{value.name}[/bold black]")
        result = run(
            value.as_posix(),
            enable_whisperx=enable_whisperx,
            enable_translate=enable_translate,
            enable_anki=enable_anki,
            handle=handle,
            check=check,
            operate_mode=operate_mode,
            import_anki=import_anki,
            anki_app=anki_app,
            start_offset=start_offset,
            end_offset=end_offset,
            over_start=over_start,
            over_end=over_end,
        )
        if result != None:
            checkList.append(result)
    run_check(checkList, operate_mode=operate_mode)


def join_handle(srtPath, number):
    return (
        srtPath.parent
        / "handle"
        / (
            ".".join(
                [
                    *srtPath.name.split(".")[:number],
                    "handle",
                    *srtPath.name.split(".")[number:],
                ]
            )
        )
    )


def run(
    audioPath,
    enable_whisperx=True,
    enable_translate=True,
    enable_anki=True,
    handle="auto",  # auto,handle,current,all
    check=False,
    operate_mode=None,
    import_anki=None,
    anki_app=None,
    start_offset=0,
    end_offset=0,
    over_start=1,
    over_end=1,
):
    """
    pdm run python .\loop_whisper.py run "d:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3" 1 1 1 --handle auto
    """
    if check or import_anki not in ["", False, 0, None]:
        enable_whisperx = False
        enable_translate = False
        enable_anki = False
    audioPath = Path(fix_unicode_bug(audioPath))
    if not audioPath.is_file():
        raise f"audioPath,不是文件 {audioPath}"
    [srtPath, wordPath, assPath] = run_whisperx(
        audioPath, enable=True if enable_whisperx else False
    )
    srtPath, wordPath, assPath = Path(srtPath), Path(wordPath), Path(assPath)

    if operate_mode not in ["", False, 0, None]:
        try:
            srtPath = run_operate_srt(
                wordPath,
                operate_mode=None
                if check or import_anki not in ["", False, 0, None]
                else operate_mode,
                start_offset=start_offset,
                end_offset=end_offset,
                over_start=over_start,
                over_end=over_end,
            )
        except (AssertionError, Exception) as e:
            print(f"[bold red]{e}[/bold red] ")
            return

    srt2Path = Path(autosub_translate_srt(srtPath, enable=False))
    srtPathHandle = join_handle(srtPath, -2)
    srt2PathHandle = join_handle(srt2Path, -5)
    ankiPath = generate_anki_deck(audioPath, srtPath, srt2Path, enable=False)
    ankiPathHandle = generate_anki_deck(
        audioPath, srtPathHandle, srt2PathHandle, enable=False
    )

    def _run(audioPath, srtPath, srt2Path, ankiPath):
        if import_anki not in ["", False, 0, None]:
            import_anki_apkg(import_anki, anki_app, ankiPath)
            return
        try:
            autosub_translate_srt(srtPath, enable=True if enable_translate else False)
        except Exception as e:
            print(f"[bold red]跳过[/bold red] {e}")
            return
        generate_anki_deck(
            audioPath,
            srtPath,
            srt2Path if srt2Path.is_file() else None,
            enable=True if enable_anki else False,
        )

    if check:
        obj = print_check(
            audioPath,
            srtPath,
            srt2Path,
            ankiPath,
            srtPathHandle,
            srt2PathHandle,
            ankiPathHandle,
            operate_mode=operate_mode,
        )
        return obj
    if not srtPath.is_file() and not srtPathHandle.is_file():
        print(f"[bold red]检测不到字幕文件[/bold red]")
        return
    if handle == "handle" or handle == "all":
        if srtPathHandle.is_file():
            _run(audioPath, srtPathHandle, srt2PathHandle, ankiPathHandle)
    if handle == "current" or handle == "all":
        if srtPath.is_file():
            _run(audioPath, srtPath, srt2Path, ankiPath)
    if handle == "auto":
        if srtPathHandle.is_file():
            _run(audioPath, srtPathHandle, srt2PathHandle, ankiPathHandle)
        elif srtPath.is_file():
            _run(audioPath, srtPath, srt2Path, ankiPath)


def get_deck_name(info_file, srtPath):
    with open(info_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    for k in ["format", "thumbnails", "automatic_captions", "subtitles", "formats"]:
        if k in data:
            del data[k]
    with open(info_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return f"{different_mode(srtPath)}{data['uploader']}::{data['upload_date'][:4]}::{data['upload_date'][4:6]}::{data['upload_date']} {data['title']} {data['id']}"


def generate_anki_deck(
    audioPath, srtPath, srt2Path=None, enable=True  # handle,current,auto,all
):
    """
    pdm run python .\loop_whisper.py gad  'd:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3' 'd:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\wsx\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3.en.srt' 'd:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\wsx\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3.en.srt.autosub.zh-cn.srt'
    handle: handle,current,auto,all
    """
    audioPath = Path(fix_unicode_bug(Path(audioPath)))
    srtPath = Path(fix_unicode_bug(Path(srtPath)))
    srt2Path = Path(fix_unicode_bug(Path(srt2Path)))
    info_file = audioPath.parent / (audioPath.stem + ".info.json")
    deck_name = get_deck_name(info_file, srtPath)
    return gen_apkg(audioPath, srtPath, srt2Path, enable=enable, deck_name=deck_name)


def autosub_translate_srt(
    srtPath, mode=True, enable=True, count=5
):  # handle,current,auto,all
    """
    pdm run python .\loop_whisper.py ats 'd:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\wsx\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3.en.srt'
    handle: # handle,current,auto,all
    """
    srtPath = Path(fix_unicode_bug(Path(srtPath)))
    for i in range(count):
        try:
            return auto_trans_srt(srtPath, enable=enable)
        except Exception as e:
            print(f"[bold red]翻译失败[/bold red] 次数: {i+1}/{count}")
    raise Exception(f"[bold red]翻译失败[/bold red] {srtPath}")


def run_whisperx(
    audioPath,
    lang="en",
    suffix=[".srt", ".word.srt", ".ass"],
    suffixLang=[".{}.srt", ".word.{}.srt", ".{}.ass"],
    dirName="wsx",
    enable=True,
):
    """
    pdm run python .\loop_whisper.py wsx "d:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3"
    """
    audioPath = Path(fix_unicode_bug(Path(audioPath)))
    outDir = audioPath.parent / dirName
    suffix = [audioPath.suffix + i for i in suffix]
    suffixLang = [audioPath.suffix + i.format(lang) for i in suffixLang]
    command = f'whisperx --language "{lang}" --output_dir "{outDir.as_posix()}" --fp16 False "{audioPath.as_posix()}"'
    if enable:
        subprocess.run(command)

    for i, i2 in zip(suffix, suffixLang):
        oldPath = audioPath.parent / dirName / (audioPath.stem + i)
        newPath = audioPath.parent / dirName / (audioPath.stem + i2)
        if oldPath.is_file():
            newPath.unlink(missing_ok=True)
            oldPath.rename(newPath)
    return [
        (audioPath.parent / dirName / (audioPath.stem + i)).as_posix()
        for i in suffixLang
    ]


if __name__ == "__main__":
    fire.Fire(
        {
            "wsx": run_whisperx,
            "ats": autosub_translate_srt,
            "gad": generate_anki_deck,
            "run": run,
            "loop": loop,
        }
    )
