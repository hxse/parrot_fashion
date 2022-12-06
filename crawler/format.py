#!/usr/bin/env python3
# coding: utf-8
from ast import main
from logging import root
import pysrt
import subprocess
import fire
from pathlib import Path


def srt2txt(path):
    subs = pysrt.open(path)
    music1 = lambda text: text.startswith("[") and text.endswith("]")
    music2 = lambda text: text.startswith("(") and text.endswith(")")
    arr = []
    for i in subs:
        row = i.text.strip()
        if music1(row) or music2(row):
            row = "." + row + "."
        arr.append(row)
    text = " ".join(arr)

    text = text.replace("\\h", " ").replace("\n", " ")
    text = text.replace(".", ".\n").replace("?", "?\n").replace("!", "!\n")
    text = "\n".join([i.strip() for i in text.split("\n")])
    text = " ".join(filter(lambda x: x, text.split(" ")))
    text = "\n".join(filter(lambda x: x != ".", text.split("\n")))
    return text


def txt2srt(audioPath, txtPath, txtSrtPath):
    opt = "|task_adjust_boundary_algorithm=percent|task_adjust_boundary_percent_value=50"  # https://github.com/readbeyond/aeneas/issues/211
    # opt = ""
    command = f'C:\Python37-32\python.exe -m aeneas.tools.execute_task  "{audioPath}" "{txtPath}"   "task_language=eng|os_task_file_format=srt|is_text_type=plain{opt}" "{txtSrtPath}"'
    subprocess.run(command)
    return


def srt2txt2srt(i):
    i = Path(i)
    audioPath = i.parent / (
        i.name.rsplit(" ", 1)[0]  # fix if name have '.'
        + " "
        + i.name.rsplit(" ", 1)[1].split(".")[0]
        + ".mp3"
    )
    txtPath = i.parent / (i.name + ".txt")
    txtSrtPath = i.parent / (i.name + ".txt" + ".srt")
    text = srt2txt(i)
    with open(txtPath, "w", encoding="utf-8") as f:
        f.write(text)
    txt2srt(audioPath, txtPath, txtSrtPath)


def loop(rootPath):
    for i in Path(rootPath).rglob("*.en*.srt"):
        if ".txt" in i.name or i.name.endswith("zh-ch.srt"):
            continue
        srt2txt2srt(i)


if __name__ == "__main__":
    fire.Fire({"lp": loop, "sts": srt2txt2srt})

    # 测试
    # audioPath=r'D:\my_repo\parrot_fashion\download\BBC Learning English\6 Minute English - Vocabulary & listening PLcetZ6gSk96-FECmH9l7Vlx5VDigvgZpt\20221006 Are artistic brains different - 6 Minute English Oq2bnLC_DXU.mp3'
    # txtPath=r'D:\my_repo\parrot_fashion\download\BBC Learning English\6 Minute English - Vocabulary & listening PLcetZ6gSk96-FECmH9l7Vlx5VDigvgZpt\20221006 Are artistic brains different - 6 Minute English Oq2bnLC_DXU.en-GB.txt'
    # outPath=r'D:\my_repo\parrot_fashion\download\BBC Learning English\6 Minute English - Vocabulary & listening PLcetZ6gSk96-FECmH9l7Vlx5VDigvgZpt\20221006 Are artistic brains different - 6 Minute English Oq2bnLC_DXU.en-GB.txt.srt'
    # originSrtPath=r'D:\my_repo\parrot_fashion\download\BBC Learning English\6 Minute English - Vocabulary & listening PLcetZ6gSk96-FECmH9l7Vlx5VDigvgZpt\20221006 Are artistic brains different - 6 Minute English Oq2bnLC_DXU.en-GB.srt'
    # text=srt2txt(originSrtPath)
    # with open (txtPath,'w',encoding='utf8') as f:
    #     f.write(text)
    # txt2srt(audioPath,txtPath,outPath)
