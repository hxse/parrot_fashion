#!/usr/bin/env python3
# coding: utf-8
import pysrt
from pathlib import Path
from rich import print


def run_log(log_path, message, name, init=False):
    if not log_path:
        return
    from datetime import datetime

    now = datetime.now()
    current_time = now.strftime("%Y/%m/%d %H:%M:%S")
    message = f"\nruntime: {current_time} | name: {name} | {message}\n"
    if init:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(message)
            return

    # with open(log_path, "r", encoding="utf-8") as f:
    #     data = f.readlines()

    # if message not in data:
    #     data.append(message)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(message)


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


def offset_time(
    start,
    end,
    start_offset=0,
    end_offset=0,
):
    _start, _end = start + int(start_offset), end + int(end_offset)
    return [
        start.from_string("0:0:0,0") if _start.ordinal < 0 else _start,
        end.from_string("0:0:0,0") if _end.ordinal < 0 else _end,
    ]


def set_over_offset(
    last_sub_obj,
    current_sub_obj,
    next_sub_obj,
    start_offset=0,
    end_offset=0,
    over_start=1,
    over_end=1,
):
    cur_start = current_sub_obj["start"]
    cur_end = current_sub_obj["end"]
    last_end = (
        cur_start.from_string("0:0:0,0")
        if last_sub_obj == None
        else last_sub_obj["end"]
    )
    next_start = (
        cur_start.from_string("0:0:0,0")
        if next_sub_obj == None
        else next_sub_obj["start"]
    )

    _min = lambda a, b: a if a.ordinal < b.ordinal else b
    _max = lambda a, b: a if a.ordinal > b.ordinal else b
    if over_start or start_offset == 0:
        start = cur_start + start_offset
    else:
        temp_start = cur_start + start_offset
        if cur_start.ordinal > last_end.ordinal:
            start = _max(last_end, temp_start)
        else:
            start = temp_start

    if over_end or end_offset == 0:
        end = cur_end + end_offset
    else:
        temp_end = cur_end + end_offset
        if cur_end.ordinal < next_start.ordinal:
            end = _min(next_start, temp_end)
        else:
            end = temp_end
    # print(f"last_end: {last_end} start: {start}")
    # print(f"next_start: {next_start} end: {end}")
    return start, end


def merge_subtitle(
    subs,
    operate_mode=None,
    start_offset=0,
    end_offset=0,
    over_start=1,
    over_end=1,
):
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
    new_data = []
    for index, i in enumerate(data):
        start, end = set_over_offset(
            last_sub_obj=None if index == 0 else data[index - 1],
            current_sub_obj=i,
            next_sub_obj=None if index == len(data) - 1 else data[index + 1],
            start_offset=start_offset,
            end_offset=end_offset,
            over_start=over_start,
            over_end=over_end,
        )
        new_data.append({"start": start, "end": end})
    for k, v in enumerate(data):
        v["start"] = new_data[k]["start"]
        v["end"] = new_data[k]["end"]
    return data


def pre_processing(
    subs,
    wordPath,
    operate_mode,
    start_offset,
    end_offset,
    over_start,
    over_end,
    log_path=None,
):
    # 预处理文本, 比如把 A. B. C. 替换成 A, B, C,
    if operate_mode == "en":
        pass
    if operate_mode == "en_no_comma":
        for i in subs:
            if len(i.text) == 2 and i.text.endswith("."):
                i.text = i.text.replace(".", ",")


def after_processing(
    subs_data,
    wordPath,
    operate_mode,
    start_offset,
    end_offset,
    over_start,
    over_end,
    log_path=None,
):
    # 后处理文本
    if operate_mode == "en":
        pass
    if operate_mode == "en_no_comma":
        n = 1
        new_data = []
        for i in subs_data:
            if i["end"].ordinal - i["start"].ordinal < 20:  # 小于20ms的被丢弃
                message = f'warning: time too short and throw away | {i["start"]} --> {i["end"]} | duration:{i["end"].ordinal - i["start"].ordinal}ms | text: { i["text"]}'
                print(f"[bold yellow]{message}[/bold yellow]")
                run_log(log_path, message, wordPath.name.split(".")[0])
                continue
            i["index"] = n
            new_data.append(i)
            n += 1
    return new_data


def gen_operate_srt(
    wordPath,
    operate_mode=None,
    start_offset=0,
    end_offset=0,
    over_start=1,
    over_end=1,
    log_path=None,
):
    subs = pysrt.open(wordPath, encoding="utf-8")
    file = pysrt.SubRipFile()
    pre_processing(
        subs,
        wordPath,
        operate_mode=operate_mode,
        start_offset=start_offset,
        end_offset=end_offset,
        over_start=over_start,
        over_end=over_end,
        log_path=log_path,
    )
    if wordPath.name.endswith("en.srt"):
        data = merge_subtitle(
            subs,
            operate_mode,
            start_offset=start_offset,
            end_offset=end_offset,
            over_start=over_start,
            over_end=over_end,
        )
        data = after_processing(
            data,
            wordPath,
            operate_mode=operate_mode,
            start_offset=start_offset,
            end_offset=end_offset,
            over_start=over_start,
            over_end=over_end,
            log_path=log_path,
        )
        for obj in data:
            file.append(
                pysrt.SubRipItem(
                    obj["index"],
                    start=obj["start"],
                    end=obj["end"],
                    text=obj["text"].strip(),
                )
            )
    fix_autosub_bug(file)
    return file


def run_operate_srt(
    wordPath,
    name_key="operate",
    operate_mode=None,
    start_offset=0,
    end_offset=0,
    over_start=1,
    over_end=1,
    log_path=None,
):
    start_offset = start_offset if start_offset <= 0 else -start_offset
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
            over_start=over_start,
            over_end=over_end,
            log_path=log_path,
        )
        file.save(outPath)
        print(f"[bold green]create wordPath done {wordPath.name}[/bold green]")
    return outPath
