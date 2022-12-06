#!/usr/bin/env python3
# coding: utf-8
import genanki
import pysrt
import json
from pathlib import Path
import random
import fire
import subprocess


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


def gen_note(my_model, audioPath, srtPath, srtPath2=None):
    subs = pysrt.open(srtPath)
    subs2 = pysrt.open(srtPath2) if srtPath2 else [None for i in range(len(subs))]
    assert len(subs) == len(subs2), "两个字幕内容数量不一致"
    noteArr = []
    splitAudioArr = []
    for index, row in enumerate(subs):
        row2 = subs2[index]
        startFormat = str(row.start).replace(":", "_").replace(",", "-")
        endFormat = str(row.end).replace(":", "_").replace(",", "-")
        splitAudioName = f"{Path(audioPath).stem} {startFormat} {endFormat}.mp3"
        my_note = genanki.Note(
            model=my_model,
            fields=[
                row.text.strip(),
                row2.text.strip() if row2 else "",
                str(row.start),
                str(row.end),
                str(Path(audioPath).stem),
                f"[sound:{splitAudioName}]",
            ],
        )
        splitAudioArr.append(
            [
                Path(audioPath).parent / "cache" / splitAudioName,
                str(row.start),
                str(row.end),
            ]
        )
        noteArr.append(my_note)
        # if not Path(audio_path).is_file():  # 检测是否存在缺失的音频文件
    return [noteArr, splitAudioArr]


def split_audio(audioPath, splitAudioArr):
    print("start split audio:")
    for [splitAudioPath, start, end] in splitAudioArr:
        Path.mkdir(Path(splitAudioPath).parent, exist_ok=True)
        command = f'ffmpeg -ss {start.replace(",",".")} -to {end.replace(",",".")} -i "{audioPath}" -c copy -y "{splitAudioPath}"'
        subprocess.run(command)
    print("end split audio")


def gen_apkg(audioPath, srtPath, srtPath2=None):
    # 音频文件路径,字幕文件路径,字幕2文件路径,需要绝对路径
    deck_id = random.randrange(1 << 30, 1 << 31)  # 随机唯一id
    deck_name = Path(audioPath).stem
    my_deck = genanki.Deck(deck_id, deck_name)
    my_package = genanki.Package(my_deck)

    my_model = gen_model("audio_model")
    [noteArr, splitAudioArr] = gen_note(my_model, audioPath, srtPath, srtPath2)
    for my_note in noteArr:
        my_deck.add_note(my_note)

    split_audio(audioPath, splitAudioArr)
    for [splitAudioPath, start, end] in splitAudioArr:
        # my_package.media_files.append(str(audioPath))
        my_package.media_files.append(str(splitAudioPath))

    my_package.write_to_file(f"{Path(srtPath)}.apkg")


if __name__ == "__main__":
    fire.Fire({"ga": gen_apkg})
