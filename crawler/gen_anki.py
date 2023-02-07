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

import os
from rich.progress import track


def run_process(command, encoding="utf-8", timeout=None):
    os.environ["PYTHONIOENCODING"] = encoding
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        encoding=encoding,
    )
    stdout, stderr = process.communicate(timeout=timeout)
    return [stdout, stderr]


def gen_model(deck_name):
    model_id = random.randrange(1 << 30, 1 << 31)  # 随机唯一id
    my_model = genanki.Model(
        model_id,
        deck_name,
        fields=[
            {"name": "expression"},
            {"name": "meaning"},
            {"name": "start"},
            {"name": "end"},
            {"name": "audio_name"},
            {"name": "audio"},
        ],
        templates=[
            {
                "name": "audio_templates",
                "qfmt": "<h1>{{audio}}</h1>",  # AND THIS
                "afmt": "<!-- {{FrontSide}}--><h1>{{audio}}</h1><br><h1>{{expression}}</h1><br><h2>{{meaning}}<h2>",
            },
        ],
        css="h1, h2{text-align: center;}",
    )
    return my_model


def gen_note(my_model, audioPath, srtPath, srtPath2=None, cacheDir="_cache"):
    subs = pysrt.open(srtPath)
    subs2 = pysrt.open(srtPath2) if srtPath2 else [None for i in range(len(subs))]
    assert len(subs) == len(subs2), f"两个字幕内容数量不一致 {len(subs)} {len(subs2)}"
    noteArr = []
    splitAudioArr = []
    for index, row in enumerate(subs):
        row2 = subs2[index]
        startFormat = str(row.start).replace(":", "_").replace(",", "-")
        endFormat = str(row.end).replace(":", "_").replace(",", "-")
        splitAudioName = f"{Path(audioPath).stem} {startFormat} {endFormat}.mp3"
        cacheFile = cacheDir / " ".join(splitAudioName.rsplit(" ", 3)[1:])

        if len(cacheFile.as_posix()) > 260:
            print(
                "windows 最大字符限制为260 https://learn.microsoft.com/zh-cn/windows/win32/fileio/maximum-file-path-limitation"
            )

        my_note = genanki.Note(
            model=my_model,
            fields=[
                row.text.strip(),
                row2.text.strip() if row2 else "",
                str(row.start),
                str(row.end),
                str(Path(audioPath).stem),
                f"[sound:{cacheFile.name}]",
            ],
        )
        splitAudioArr.append(  # windows路径不应该大于260
            [
                cacheFile,
                str(row.start),
                str(row.end),
            ]
        )
        noteArr.append(my_note)
        # if not Path(audio_path).is_file():  # 检测是否存在缺失的音频文件
    return [noteArr, splitAudioArr]


def split_audio(audioPath, splitAudioArr):
    for [splitAudioPath, start, end] in track(
        splitAudioArr, description="split audio file..."
    ):
        Path.mkdir(Path(splitAudioPath).parent, exist_ok=True)
        command = f'ffmpeg  -i "{audioPath.as_posix()}" -acodec copy -ss {start.replace(",",".")} -to {end.replace(",",".")}  -y "{splitAudioPath.as_posix()}"'  # 把-i放后面会导致切割出来的文件变很大
        stdout, stderr = run_process(command)


def gen_apkg(audioPath, srtPath, srtPath2=None, enable=True, deck_name=None):
    # 音频文件路径,字幕文件路径,字幕2文件路径,需要绝对路径
    audioPath, srtPath, srtPath2 = Path(audioPath), Path(srtPath), Path(srtPath2)
    outPath = Path(f"{Path(srtPath).as_posix()}.apkg")
    if not enable:
        return Path(outPath)
    cacheDir = srtPath.parent / "_cache"
    deck_id = random.randrange(1 << 30, 1 << 31)  # 随机唯一id
    deck_name = Path(audioPath).stem if deck_name == None else deck_name
    my_deck = genanki.Deck(deck_id, deck_name)
    my_package = genanki.Package(my_deck)

    my_model = gen_model("audio_model")
    [noteArr, splitAudioArr] = gen_note(
        my_model, audioPath, srtPath, srtPath2, cacheDir=cacheDir
    )
    for my_note in noteArr:
        my_deck.add_note(my_note)

    split_audio(audioPath, splitAudioArr)
    for [splitAudioPath, start, end] in splitAudioArr:
        # my_package.media_files.append(str(audioPath))
        my_package.media_files.append(str(splitAudioPath))

    if len(outPath.as_posix()) > 260:
        print(
            "windows 最大字符限制为260 https://learn.microsoft.com/zh-cn/windows/win32/fileio/maximum-file-path-limitation"
        )

    my_package.write_to_file(outPath)
    shutil.rmtree(cacheDir)


if __name__ == "__main__":
    fire.Fire({"ga": gen_apkg})
