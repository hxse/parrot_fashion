#!/usr/bin/env python3
# coding: utf-8

import fire
from pathlib import Path
import subprocess


def findSuffix(array, suffix, mode="end"):
    for i in array:
        if mode == "end":
            if i.name.endswith(suffix):
                return i
        else:
            if i.name.startswith(suffix):
                return i
    return None


def kurzgesagt(dirPath, mediSuffix, suffixArr):
    videoDir = [*Path(dirPath).glob("*")]
    for d in videoDir:
        files = [*d.glob("*")]

        ignoreFile = findSuffix(
            files, "忽略", mode="start"
        )  # 如果文件夹有个开头是"忽略"的, 那么忽略, 建议手动处理
        if ignoreFile:
            print("忽略", ignoreFile)
            continue

        apkgFile = findSuffix(files, ".apkg")
        if apkgFile:
            print("跳过", "已存在apkg文件", apkgFile)
            continue
        mp3File = findSuffix(files, mediSuffix)
        srtFile = None
        for suffix in suffixArr:
            srtFile = findSuffix(files, suffix)
            if srtFile:
                break
        if mp3File and srtFile:
            command = f"powershell . D:\my_repo\my_cmd\my_init.ps1;"
            command = command + f"ycs '{srtFile}';"
            command = (
                command
                + f"yga '{mp3File}' '{srtFile}.txt.srt' '{srtFile}.txt.srt.autosub.zh-cn.srt'"
            )
            subprocess.run(command)
        else:
            print("没找到文件", "mp3File:", mp3File, "srtFile:", srtFile)


if __name__ == "__main__":
    fire.Fire({"ku": kurzgesagt})
