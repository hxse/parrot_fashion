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
import os, subprocess


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
    return (
        "[handle] " if srtPath.parent.name == "handle" else f"[{srtPath.parent.name}] "
    )


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
            {"name": "expression"},
            {"name": "meaning"},
            {"name": "start"},
            {"name": "end"},
            {"name": "audio_name"},
            {"name": "audio"},
            {"name": "mode"},
        ],
        templates=[
            {
                "name": "audio_templates",
                "qfmt": "<h1>{{audio}}</h1>",  # AND THIS
                "afmt": "<!-- {{FrontSide}}--><h1>{{audio}}</h1><br><h1>{{furigana:expression}}</h1><br><h2>{{furigana:meaning}}<h2>",
            },
        ],
        css="h1, h2{text-align: center;}",  # white-space: pre-line
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
                row.text.strip().replace("\n", "<br>"),
                row2.text.strip().replace("\n", "<br>") if row2 else "",
                str(row.start),
                str(row.end),
                str(Path(audioPath).stem),
                f"[sound:{cacheFile.name}]",
                different_mode(srtPath),
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
        command = f'ffmpeg -ss {start.replace(",",".")} -to {end.replace(",",".")} -i "{audioPath.as_posix()}" -y "{splitAudioPath.as_posix()}"'
        # https://stackoverflow.com/questions/18444194/cutting-the-videos-based-on-start-and-end-time-using-ffmpeg
        # 省略 -c copy 会重新编码,会更慢但更精确，但仍然比在 -i 之后指定 -ss 和 -to 更快，因为这种情况意味着必须在处理完整个输入文件之后才进行修剪
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

    my_model = gen_model(deck_name.split(":")[0])
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
