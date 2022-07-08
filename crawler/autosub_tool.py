#!/usr/bin/env python3
# coding: utf-8
import subprocess
import fire
from pathlib import Path


def set_middle_suffix(fileName, middle_suffix):
    s = fileName.rsplit(".", 1)
    return s[0] + "." + middle_suffix + "." + s[1]


def gen_srt(inPath, outPath):
    """
    识别生成英文srt
    inPath = r"D:\my_repo\parrot fashion\download\BBC Learning English\playlist\6 Minute English - Vocabulary & listening\001 Does wearing a uniform change our behaviour 6 Minute English.mp3"
    outPath =r"D:\my_repo\parrot fashion\download\BBC Learning English\playlist\6 Minute English - Vocabulary & listening\001 Does wearing a uniform change our behaviour 6 Minute English.autosub.srt"
    """
    inPath = Path(inPath).as_posix()
    outPath = Path(outPath).as_posix()
    command = f'autosub -hp http://127.0.0.1:7890  -hsp http://127.0.0.1:7890 -i "{inPath}" -S en-us -o "{outPath}"'
    subprocess.run(command)
    return set_middle_suffix(outPath, "en-us")


def trans_srt(inPath, outPath, langArr):
    """
    从英文srt翻译到中文srt
    inPath = r"D:\my_repo\parrot fashion\download\BBC Learning English\playlist\6 Minute English - Vocabulary & listening\001 Does wearing a uniform change our behaviour 6 Minute English.autosub.en-us.srt"
    outPath = r"D:\my_repo\parrot fashion\download\BBC Learning English\playlist\6 Minute English - Vocabulary & listening\001 Does wearing a uniform change our behaviour 6 Minute English.autosub.en-us.autosub.srt"
    """
    inPath = Path(inPath).as_posix()
    outPath = Path(outPath).as_posix()
    command = f'autosub -hsp http://127.0.0.1:7890 -i "{inPath}" -SRC {langArr[2]} -D {langArr[3]} -o "{outPath}"'
    subprocess.run(command)
    return set_middle_suffix(outPath, "zh-cn")


def gen_trans(fileName, fileDir):
    """
    先识别生成英文srt,再从英文srt翻译到中文srt,函数gen_srt和trans_srt的组合
    name = "001 Does wearing a uniform change our behaviour 6 Minute English.mp3"
    fileDir = r"D:\my_repo\parrot fashion\download\BBC Learning English\playlist\6 Minute English - Vocabulary & listening"
    """
    name = fileName.rsplit(".", 1)[0]
    inPath = fileDir + "\\" + fileName
    outPath = fileDir + "\\" + name + ".srt"
    outPath = set_middle_suffix(outPath, "autosub")
    gen_srt(inPath, outPath)

    inPath = fileDir + "\\" + name + ".autosub.en-us.srt"
    outPath = set_middle_suffix(inPath, "autosub")
    trans_srt(inPath, outPath)


if __name__ == "__main__":
    # pip install git+https://github.com/BingLingGroup/autosub.git@dev ffmpeg-normalize langcodes
    # pdm add git+https://github.com/BingLingGroup/autosub.git@dev ffmpeg-normalize langcodes
    fire.Fire({"gt": gen_trans, "gs": gen_srt, "ts": trans_srt})
