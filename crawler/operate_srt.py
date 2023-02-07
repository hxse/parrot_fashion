#!/usr/bin/env python3
# coding: utf-8
import pysrt
from pathlib import Path
from rich import print


def condition(i, operate_mode=None):
    if operate_mode == "en":
        c1 = any([i.text.endswith(s) for s in ",.?!"])
        c2 = any([i.text.endswith(s) for s in ",.?!"])
        return any([c1, c2])
    raise Exception(f"can not match operate_mode {operate_mode}")


def merge_text(text, word, operate_mode=None):
    if operate_mode == "en":
        return text + " " + word
    raise Exception(f"can not match operate_mode {operate_mode}")


def merge_subtitle(subs, operate_mode=None):
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
    return data


def gen_operate_srt(wordPath, operate_mode=None):
    subs = pysrt.open(wordPath, encoding="utf-8")
    file = pysrt.SubRipFile()
    if wordPath.name.endswith("en.srt"):
        data = merge_subtitle(subs, operate_mode)
        for obj in data:
            file.append(
                pysrt.SubRipItem(
                    obj["index"],
                    start=obj["start"],
                    end=obj["end"],
                    text=obj["text"],
                )
            )
    return file


def run_operate_srt(wordPath, name_key="operate", operate_mode=None):
    seg = Path(wordPath).name.split(".")
    seg[-3] = name_key
    outPath = Path(wordPath).parent / ".".join(seg)
    if operate_mode not in ["", False, 0, None]:
        assert Path(wordPath).is_file(), f"not check wordPath {wordPath.name}"
        file = gen_operate_srt(wordPath, operate_mode=operate_mode)
        file.save(outPath)
        print(f"[bold green]create wordPath done {wordPath.name}[/bold green]")
    return outPath
