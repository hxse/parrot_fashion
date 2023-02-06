#!/usr/bin/env python3
# coding: utf-8
import fire
from pathlib import Path
import subprocess
from autosub_tool import fix_unicode_bug, auto_trans_srt
from gen_anki import gen_apkg
from rich import print
import json


def run_check(checkList):
    if len(checkList) == 0:
        return
    statistics = {
        "audioPath": {"success": 0, "failed": 0},
        "srtPath": {"success": 0, "failed": 0},
        "srt2Path": {"success": 0, "failed": 0},
        "ankiPath": {"success": 0, "failed": 0},
        "srtPathHandle": {"success": 0, "failed": 0},
        "srt2PathHandle": {"success": 0, "failed": 0},
        "ankiPathHandle": {"success": 0, "failed": 0},
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


def loop(
    dirPath,
    enable_whisperx=True,
    enable_translate=True,
    enable_anki=True,
    handle="auto",  # auto,handle,current,all
    skip=0,
    check=False,
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
        print(f"run  {index + 1}/{len(pathList)} [bold black]{value.name}[/bold black]")
        result = run(
            value.as_posix(),
            enable_whisperx=enable_whisperx,
            enable_translate=enable_translate,
            enable_anki=enable_anki,
            handle=handle,
            check=check,
        )
        if result != None:
            checkList.append(result)
    run_check(checkList)


def run(
    audioPath,
    enable_whisperx=True,
    enable_translate=True,
    enable_anki=True,
    handle="auto",  # auto,handle,current,all
    check=False,
):
    """
    pdm run python .\loop_whisper.py run "d:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3" 1 1 1 --handle auto
    """
    if check:
        enable_whisperx = False
        enable_translate = False
        enable_anki = False
    audioPath = Path(fix_unicode_bug(audioPath))
    if not audioPath.is_file():
        raise f"audioPath,不是文件 {audioPath}"
    srtPath = Path(run_whisperx(audioPath, enable=True if enable_whisperx else False))
    srt2Path = Path(autosub_translate_srt(srtPath, enable=False))
    srtPathHandle = srtPath.parent / "handle" / srtPath.name
    srt2PathHandle = srt2Path.parent / "handle" / srt2Path.name
    ankiPath = generate_anki_deck(audioPath, srtPath, srt2Path, enable=False)
    ankiPathHandle = generate_anki_deck(
        audioPath, srtPathHandle, srt2PathHandle, enable=False
    )

    def _run(audioPath, srtPath, srt2Path):
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
        boolRich = lambda x: (
            f"[bold green]{x}[/bold green]" if x else f"[bold red]{x}[/bold red]"
        )
        obj = {
            "audioPath": audioPath.is_file(),
            "srtPath": srtPath.is_file(),
            "srt2Path": srt2Path.is_file(),
            "ankiPath": ankiPath.is_file(),
            "srtPathHandle": srtPathHandle.is_file(),
            "srt2PathHandle": srt2PathHandle.is_file(),
            "ankiPathHandle": ankiPathHandle.is_file(),
        }
        text = " ".join([f"{i}: {boolRich(obj[i])}" for i in obj])
        print(text)
        return obj
    if not srtPath.is_file() and not srtPathHandle.is_file():
        print(f"[bold red]检测不到字幕文件[/bold red]")
        return
    if handle == "handle" or handle == "all":
        if srtPathHandle.is_file():
            _run(audioPath, srtPathHandle, srt2PathHandle)
    if handle == "current" or handle == "all":
        if srtPath.is_file():
            _run(audioPath, srtPath, srt2Path)
    if handle == "auto":
        if srtPathHandle.is_file():
            _run(audioPath, srtPathHandle, srt2PathHandle)
        elif srtPath.is_file():
            _run(audioPath, srtPath, srt2Path)


def get_deck_name(info_file):
    with open(info_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        return f"{data['upload_date']} {data['title']} {data['id']}"


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
    deck_name = get_deck_name(info_file)
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
    suffix=[".srt", ".ass", ".word.srt"],
    suffixLang=[".{}.srt", ".{}.ass", ".word.{}.srt"],
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
    return (audioPath.parent / dirName / (audioPath.stem + suffixLang[0])).as_posix()


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
