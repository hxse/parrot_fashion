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


def fix_name(dirPath):
    arr = [
        [
            "Kurzgesagt 鈥?In a Nutshell",
            "Kurzgesagt – In a Nutshell",
        ],  # windows11 编码会有点问题
    ]
    for i in arr:
        if i[0] in dirPath:
            return dirPath.replace(i[0], i[1])
    return dirPath


def kurzgesagt(dirPath, mediSuffix, suffixArr, setPath=None):
    dirPath = fix_name(dirPath)
    videoDir = [*Path(dirPath).glob("*")]
    for d in videoDir:
        if setPath and d.name != Path(setPath).name:
            continue

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
            # import pdb

            # pdb.set_trace()
            mp3File = Path(mp3File.as_posix().replace("’", "’’"))
            srtFile = Path(srtFile.as_posix().replace("’", "’’"))

            if (
                ".handle." in srtFile.name
            ):  # 给文件后缀加个.handle.就会默认直接翻译后生成apkg,不用走aeneas了
                srtFile1 = f"{srtFile}"
                srtFile2 = f"{srtFile}.autosub.zh-cn.srt"
                command = command + f"yats '{srtFile}';"
            else:
                srtFile1 = f"{srtFile}.txt.srt"
                srtFile2 = f"{srtFile}.txt.srt.autosub.zh-cn.srt"

                command = command + f"ysts '{srtFile}';"

                command = command + f"yats '{srtFile}.txt.srt';"
                # command = command + f"ycs '{srtFile}';" #ycs = ysts + yats
            command = command + f"yga '{mp3File}' '{srtFile1}' '{srtFile2}'"
            subprocess.run(command)
        else:
            print("没找到文件", "mp3File:", mp3File, "srtFile:", srtFile)


if __name__ == "__main__":
    fire.Fire({"ku": kurzgesagt})
