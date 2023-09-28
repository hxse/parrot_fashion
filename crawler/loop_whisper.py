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
import re, time
import datetime
from operate_srt import run_log
from gen_anki import run_release_apkg

initial_prompt_default = "Please listen to dialogue and question. Use punctuation symbols to shorten sentences."


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


def import_anki_apkg(import_anki, anki_app, ankiPath, sleep=0.6):
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
    whisper_name="wc2",  # wc2,wsx
    initial_prompt=initial_prompt_default,
    enable_release_apkg=None,
):
    """
    pdm run python .\loop_whisper.py loop "d:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos" 1 1 1 --handle auto
    """
    dirPath = Path(fix_unicode_bug(dirPath))
    log_path = dirPath / "log.txt"
    if not dirPath.is_dir():
        raise f"dirPath,不是文件夹 {dirPath}"

    pathList = [i for i in Path(dirPath).rglob("*.mp3") if i.parent.name != "_cache"]
    checkList = []
    release_list = []

    for index, value in enumerate(pathList):
        if skip > index:
            print(f"skip {index + 1}/{len(pathList)} {value.name}")
            continue
        if key and not re.compile(str(key)).match(value.name):
            continue

        print(
            f"run:  {index + 1}/{len(pathList)} [bold black]{value.name}[/bold black]"
        )
        message = f"run:  {index + 1}/{len(pathList)} {value.name}"
        # run_log(log_path, message, value.name.split(".")[0]) #这一行放run函数里面用,以过滤check和import_anki的情况

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
            whisper_name=whisper_name,
            initial_prompt=initial_prompt,
            log_path=log_path,
            log_message=message,
            enable_release_apkg=enable_release_apkg,
            release_list=release_list,
        )
        if result != None:
            checkList.append(result)
    run_check(checkList, operate_mode=operate_mode)
    if len(release_list) > 0:
        run_release_apkg(release_list)


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
    whisper_name="wc2",  # wc2,wsx
    initial_prompt=initial_prompt_default,
    log_path=None,
    log_message=None,
    enable_release_apkg=None,
    release_list=None,
):
    """
    pdm run python .\loop_whisper.py run "d:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3" 1 1 1 --handle auto
    """

    def isSkip():
        return check or import_anki not in ["", False, 0, None] or enable_release_apkg

    if isSkip():
        enable_whisperx = False
        enable_translate = False
        enable_anki = False
    else:
        run_log(log_path, log_message, Path(audioPath).name.split(".")[0])
    audioPath = Path(fix_unicode_bug(audioPath))
    if not audioPath.is_file():
        raise f"audioPath,不是文件 {audioPath}"
    [srtPath, wordPath] = run_whisperx(
        audioPath,
        enable=True if enable_whisperx else False,
        whisper_name=whisper_name,
        initial_prompt=initial_prompt,
        log_path=log_path,
    )

    srtPath, wordPath = Path(srtPath), Path(wordPath)

    if operate_mode not in ["", False, 0, None]:
        try:
            srtPath = run_operate_srt(
                wordPath,
                operate_mode=None if isSkip() else operate_mode,
                start_offset=start_offset,
                end_offset=end_offset,
                over_start=over_start,
                over_end=over_end,
                log_path=log_path,
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
        if enable_release_apkg:
            release_list.append(ankiPath)
            return
        try:
            autosub_translate_srt(srtPath, enable=True if enable_translate else False)
        except Exception as e:
            print(f"[bold red]跳过[/bold red] {e}")  # sdfsf
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
    try:
        with open(info_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as e:
        return f"{Path(srtPath).parent.parent.parent.parent.name}::{Path(srtPath).parent.parent.parent.name}::{Path(srtPath).parent.parent.name}::{Path(Path(Path(srtPath).stem).stem).stem}"  # 需要三级目录
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


def convert_time(t):
    return str(datetime.timedelta(seconds=t)).replace(".", ",")[:-3]


def run_whisperx(
    audioPath,
    lang="en",
    whisper_name="wc2",  # wc2, wsx
    enable=True,
    initial_prompt=initial_prompt_default,
    log_path=None,
):
    """
    pdm run python .\loop_whisper.py wsx "d:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3"
    --initial_prompt "Hello, welcome to my lecture." 解决没有标点符号 https://github.com/openai/whisper/discussions/194
    initial_prompt = '--initial_prompt "Please, listen to dialogue and question. the example question one: What is the color of this apple? Is it, a red, b green, c yellow? the example question two: What kind of transportation did he take?  Was it, a car, b bike, c bus? A final note, pay attention to the use of punctuation."'
    """
    audioPath = Path(fix_unicode_bug(Path(audioPath)))
    outDir = audioPath.parent / whisper_name
    if whisper_name == "wc2":
        #  --vad_threshold 0.93以上才能过滤背景音乐,
        vad_filter = "--vad_filter True --vad_threshold 0.98"
        model = "--model medium.en" if lang == "en" else "--model medium"
        initial_prompt = f'--initial_prompt "{initial_prompt}"'
        command = f'whisper-ctranslate2 --language {lang} --output_dir "{outDir.as_posix()}" {vad_filter} {model}  --word_timestamps True {initial_prompt} "{audioPath.as_posix()}"'
        srtPath = outDir / f"{audioPath.stem}.{lang}.srt"
        wordSrtPath = outDir / f"{audioPath.stem}.word.{lang}.srt"
        if not enable:
            return [srtPath, wordSrtPath]

        print(command)
        message = f"--language {lang} {vad_filter} {model} {initial_prompt}"
        run_log(log_path, message, audioPath.name.split(".")[0])

        subprocess.run(command)

        # 保证生成文件命名格式一致
        arr = []
        word_arr = []
        n = 1
        with open(outDir / f"{audioPath.stem}.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            for i in data["segments"]:
                arr.append(
                    f"{i['id']}\n{convert_time(i['start'])} --> {convert_time(i['end'])}\n{i['text'].strip()}\n\n"
                )
                for i in i["words"]:
                    word_arr.append(
                        f"{n}\n{convert_time(i['start'])} --> {convert_time(i['end'])}\n{i['word'].strip()}\n\n"
                    )
                    n += 1
        with open(srtPath, "w", encoding="utf-8") as file:
            file.writelines(arr)
        with open(wordSrtPath, "w", encoding="utf-8") as file:
            file.writelines(word_arr)

        suffix = [".json", ".srt", ".tsv", ".txt", ".vtt"]
        for i in suffix:
            if i == ".json":
                oldPath = outDir / f"{audioPath.stem}{i}"
                newPath = outDir / f"{audioPath.stem}.{lang}{i}"
                if oldPath.is_file():
                    newPath.unlink(missing_ok=True)
                    oldPath.rename(newPath)
            else:
                (outDir / f"{audioPath.stem}{i}").unlink(missing_ok=True)
        return [srtPath, wordSrtPath]

    if whisper_name == "wsx":
        command = f'whisperx --language "{lang}" --output_dir "{outDir.as_posix()}" --fp16 False "{audioPath.as_posix()}"'
        old_arr = [
            outDir / f"{audioPath.name}.srt",
            outDir / f"{audioPath.name}.word.srt",
        ]
        new_arr = [
            outDir / f"{audioPath.stem}.{lang}.srt",
            outDir / f"{audioPath.stem}.word.{lang}.srt",
        ]
        if not enable:
            return new_arr

        subprocess.run(command)

        # 保证生成文件命名格式一致
        for oldPath, newPath in zip(old_arr, new_arr):
            if oldPath.is_file():
                newPath.unlink(missing_ok=True)
                oldPath.rename(newPath)
        assPath = outDir / f"{audioPath.name}.ass"
        if assPath.is_file():
            assPath.unlink(missing_ok=True)
        return new_arr
    raise RuntimeError("请选择一个语音引擎,wc2,wsx")


if __name__ == "__main__":
    fire.Fire(
        {
            "wsx": run_whisperx,
            "ats": autosub_translate_srt,
            "gad": generate_anki_deck,
            "run": run,
            "loop": loop,
            "iaa": import_anki_apkg,
        }
    )
