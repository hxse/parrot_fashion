#!/usr/bin/env python3
# coding: utf-8
import genanki
import pysrt
import json
from pathlib import Path
import random
import fire
import subprocess
import shutil
from rich.progress import track
import os, subprocess
from tool import check_exists
from template import front, back, css


def run_release_apkg(release_list):
    """
    遍历目录, 然后打包apkg
    这个先不写了, 因为没什么好用的轮子能合并apkg,造轮子就很麻烦了,算了,手动导入anki合并吧
    """
    res = {}
    for i in release_list:
        if not Path(i).is_file():
            raise RuntimeError(f"apkg file not exist: {i}")

        # key = i.name[:4]
        # if key not in res:
        #     res[key] = []
        # res[key] = [*res[key], i]

    import pdb

    pdb.set_trace()


def different_mode(srtPath):
    return ("[handle] " if srtPath.parent.name == "handle" else
            f"[{srtPath.parent.name}] ")


def run_process(command, cwd=None, timeout=None):
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd=cwd,
    )
    stdout, stderr = process.communicate(timeout=timeout)
    return [stdout, stderr]


def gen_model(model_name):
    # model_id = random.randrange(1 << 30, 1 << 31)  # 随机唯一id
    model_id = sum([ord(char) for char in model_name])
    my_model = genanki.Model(
        model_id,
        model_name,
        fields=[
            {
                "name": "sentence"
            },
            {
                "name": "meaning"
            },
            {
                "name": "start"
            },
            {
                "name": "end"
            },
            {
                "name": "sound"
            },
            {
                "name": "audio"
            },
            {
                "name": "audio2"
            },
            {
                "name": "mode"
            },
        ],
        templates=[
            {
                "name": "audio_templates",
                "qfmt":
                # "<h1>[sound:{{audio}}]</h1>",
                front,
                "afmt":
                # "<!-- {{FrontSide}}--><h1>{{audio}}</h1><br><h1>{{furigana:expression}}</h1><br><h2>{{furigana:meaning}}<h2>",
                back,
            },
        ],
        css=css,  # white-space: pre-line
    )
    return my_model


def gen_note(my_model, audioPath, srtPath, srtPath2=None, cacheDir="_cache"):
    subs = pysrt.open(srtPath)
    subs2 = pysrt.open(srtPath2) if srtPath2 else [
        None for i in range(len(subs))
    ]
    assert len(subs) == len(subs2), f"两个字幕内容数量不一致 {len(subs)} {len(subs2)}"
    noteArr = []
    for index, row in enumerate(subs):
        row2 = subs2[index]
        startFormat = str(row.start).replace(":", "_").replace(",", "-")
        endFormat = str(row.end).replace(":", "_").replace(",", "-")

        my_note = genanki.Note(
            model=my_model,
            fields=[
                row.text.strip().replace("\n", "<br>"),
                row2.text.strip().replace("\n", "<br>") if row2 else "",
                str(row.start),
                str(row.end),
                f'[sound:{str(Path(audioPath).name)}]',
                f'<audio id="myaudio" src="{Path(audioPath).name}"></audio>',
                f'<audio id="myaudio" controls src="{Path(audioPath).name}"></audio>',
                different_mode(srtPath),
            ],
        )
        noteArr.append(my_note)
    return noteArr


def split_audio(audioPath, splitAudioArr):
    for [splitAudioPath, start,
         end] in track(splitAudioArr, description="split audio file..."):
        Path.mkdir(Path(splitAudioPath).parent, exist_ok=True)
        command = f'ffmpeg -ss {start.replace(",",".")} -to {end.replace(",",".")} -i "{audioPath.as_posix()}" -y "{splitAudioPath.as_posix()}"'
        # https://stackoverflow.com/questions/18444194/cutting-the-videos-based-on-start-and-end-time-using-ffmpeg
        # 省略 -c copy 会重新编码,会更慢但更精确，但仍然比在 -i 之后指定 -ss 和 -to 更快，因为这种情况意味着必须在处理完整个输入文件之后才进行修剪
        stdout, stderr = run_process(command)


def gen_apkg(audioPath, srtPath, srtPath2=None, deck_name=None):
    # 音频文件路径,字幕文件路径,字幕2文件路径,需要绝对路径
    audioPath, srtPath, srtPath2 = Path(audioPath), Path(srtPath), Path(
        srtPath2)
    outPath = Path(f"{Path(srtPath).as_posix()}.apkg")
    cacheDir = srtPath.parent / "_cache"
    deck_id = random.randrange(1 << 30, 1 << 31)  # 随机唯一id
    deck_name = Path(audioPath).stem if deck_name == None else deck_name
    my_deck = genanki.Deck(deck_id, deck_name)
    my_package = genanki.Package(my_deck)

    my_model = gen_model(deck_name.split(":")[0])
    noteArr = gen_note(my_model,
                       audioPath,
                       srtPath,
                       srtPath2,
                       cacheDir=cacheDir)
    for my_note in noteArr:
        my_deck.add_note(my_note)

    my_package.media_files.append(audioPath.as_posix())

    if len(outPath.as_posix()) > 260:
        print(
            "windows 最大字符限制为260 https://learn.microsoft.com/zh-cn/windows/win32/fileio/maximum-file-path-limitation"
        )

    my_package.write_to_file(outPath)


def get_deck_name(info_file, srtPath):
    try:
        with open(info_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as e:
        return f"{Path(srtPath).parent.parent.parent.parent.name}::{Path(srtPath).parent.parent.parent.name}::{Path(srtPath).parent.parent.parent.name} {Path(srtPath).parent.parent.name} {Path(Path(Path(srtPath).stem).stem).stem}"  # 需要三级目录
    for k in [
            "format", "thumbnails", "automatic_captions", "subtitles",
            "formats"
    ]:
        if k in data:
            del data[k]
    with open(info_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return f"{different_mode(srtPath)}{data['uploader']}::{data['upload_date'][:4]}::{data['upload_date'][4:6]}::{data['upload_date']} {data['title']} {data['id']}"


def generate_anki_deck(audioPath, srtPath, srt2Path=None, overwrite=True):
    """
    pdm run python .\loop_whisper.py gad  'd:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3' 'd:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\wsx\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3.en.srt' 'd:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\wsx\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3.en.srt.autosub.zh-cn.srt'
    handle: handle,current,auto,all
    """
    info_file = audioPath.parent / (audioPath.stem + ".info.json")
    deck_name = get_deck_name(info_file, srtPath)

    outApkgPath = Path(f"{Path(srtPath).as_posix()}.apkg")
    path_list = [outApkgPath]
    if not overwrite and check_exists(path_list):
        return path_list

    gen_apkg(audioPath, srtPath, srt2Path, deck_name=deck_name)
    return path_list


if __name__ == "__main__":
    fire.Fire({"ga": gen_apkg})
