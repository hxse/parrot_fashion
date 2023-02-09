#!/usr/bin/env python3
# coding: utf-8
import pysrt
from pathlib import Path
from rich import print


def fix_autosub_bug(file):
    # 一个莫名其妙的bug,`winning.`这个字符会导致翻译出错,不知道为什么
    # https://github.com/BingLingGroup/autosub/issues/198
    for i in file:
        if "the terrorists are winning." in i.text:
            i.text = i.text.replace(
                "the terrorists are winning.", "the terrorists are winning;"
            )


def condition(i, operate_mode=None):
    if operate_mode == "en":
        c1 = any([i.text.endswith(s) for s in ",.?!;"])
        return any([c1])
    if operate_mode == "en_no_comma":
        c1 = any([i.text.endswith(s) for s in ".?!;"])
        return any([c1])
    raise Exception(f"can not match operate_mode {operate_mode}")


def merge_text(text, word, operate_mode=None):
    if operate_mode == "en":
        return text + " " + word
    if operate_mode == "en_no_comma":
        return text + " " + word
    raise Exception(f"can not match operate_mode {operate_mode}")


def offset_time(start, end, start_offset=0, end_offset=0):
    _start, _end = start + int(start_offset), end + int(end_offset)
    return [
        start.from_string("0:0:0,0") if _start.ordinal < 0 else _start,
        end.from_string("0:0:0,0") if _end.ordinal < 0 else _end,
    ]


def merge_subtitle(subs, operate_mode=None, start_offset=0, end_offset=0):
    n = 1
    data = []
    for index, i in enumerate(subs):
        if index == 0:
            obj = {"index": n, "start": i.start, "end": i.end, "text": ""}
        obj["end"] = i.end
        obj["text"] = merge_text(obj["text"], i.text, operate_mode=operate_mode)
        if index == len(subs) - 1:
            data.append(obj)
        elif condition(i, operate_mode=operate_mode):
            data.append(obj)
            n += 1
            obj = {
                "index": n,
                "start": subs[index + 1].start,
                "end": subs[index + 1].end,
                "text": "",
            }
    for i in data:
        i["start"], i["end"] = offset_time(
            i["start"], i["end"], start_offset=start_offset, end_offset=end_offset
        )
    return data


def gen_operate_srt(wordPath, operate_mode=None, start_offset=0, end_offset=0):
    subs = pysrt.open(wordPath, encoding="utf-8")
    file = pysrt.SubRipFile()
    if wordPath.name.endswith("en.srt"):
        data = merge_subtitle(
            subs, operate_mode, start_offset=start_offset, end_offset=end_offset
        )
        for obj in data:
            file.append(
                pysrt.SubRipItem(
                    obj["index"],
                    start=obj["start"],
                    end=obj["end"],
                    text=obj["text"],
                )
            )
    fix_autosub_bug(file)
    return file


def run_operate_srt(
    wordPath, name_key="operate", operate_mode=None, start_offset=0, end_offset=0
):
    seg = Path(wordPath).name.split(".")
    seg[-3] = name_key
    outPath = Path(wordPath).parent / ".".join(seg)
    if operate_mode not in ["", False, 0, None]:
        assert Path(wordPath).is_file(), f"not check wordPath {wordPath.name}"
        file = gen_operate_srt(
            wordPath,
            operate_mode=operate_mode,
            start_offset=start_offset,
            end_offset=end_offset,
        )
        file.save(outPath)
        print(f"[bold green]create wordPath done {wordPath.name}[/bold green]")
    return outPath
