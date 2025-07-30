#!/usr/bin/env python3
# coding: utf-8
import subprocess
import fire
from pathlib import Path


langs = [  # 格式为: [[originSuffix, tagetSuffix, -SRC, -D]]
    [".en.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    [".en-us.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    [".en-GB.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    [".en-en.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    [".en-en-GB.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    [".txt.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    [".ja.srt", ".autosub.zh-ch.srt", "ja", "zh-cn"],
]
langs2 = [[i[0] + ".txt.srt", *i[1:]] for i in langs]
langs3 = [[".handle" + i[0], *i[1:]] for i in langs]
langs = [*langs, *langs2, *langs3]


def searchLangs(path: Path, langs=langs):
    for i in langs:
        if path.as_posix().endswith(i[0]):
            return [True, i]
    return [False, None]


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
    command = f'autosub -hp http://127.0.0.1:7890  -hsp http://127.0.0.1:7890 -i "{inPath}" -S en-us -y -o "{outPath}"'
    subprocess.run(command)
    return set_middle_suffix(outPath, "en-us")


def fix_unicode_bug(inPath):
    inPath = Path(inPath)
    if "Kurzgesagt  In a Nutshell" in inPath.as_posix():
        return inPath.as_posix().replace(
            "Kurzgesagt  In a Nutshell", "Kurzgesagt – In a Nutshell"
        )
    return inPath.as_posix()


import os


def run_process(command, code="utf-8", timeout=None):
    os.environ["PYTHONIOENCODING"] = "utf-8"
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=None, shell=True, encoding="utf-8"
    )
    stdout, stderr = process.communicate(timeout=timeout)
    return [stdout, stderr]


def trans_srt(inPath, outPath, langArr, enable=True):
    """
    从英文srt翻译到中文srt,outPath不能带zh-ch, 因为autosub会自动补全zh-cn
    inPath = r"D:\my_repo\parrot fashion\download\BBC Learning English\playlist\6 Minute English - Vocabulary & listening\001 Does wearing a uniform change our behaviour 6 Minute English.autosub.en-us.srt"
    outPath = r"D:\my_repo\parrot fashion\download\BBC Learning English\playlist\6 Minute English - Vocabulary & listening\001 Does wearing a uniform change our behaviour 6 Minute English.autosub.en-us.autosub.srt"
    """
    inPath = Path(fix_unicode_bug(inPath))
    inPath = Path(inPath).as_posix()
    outPath = Path(outPath).as_posix()
    command = f'autosub -hsp http://127.0.0.1:7890 -i "{inPath}" -SRC {langArr[2]} -D {langArr[3]} -y -o "{outPath}"'
    if enable:
        stdout, stderr = run_process(command)
        if "All work done." not in str(stdout.strip()):
            raise Exception(f"{stdout} {stderr}")
    return Path(set_middle_suffix(outPath, "zh-cn")).as_posix()


def auto_trans_srt(inPath, enable=True):
    inPath = Path(Path(inPath).as_posix())
    [code, langArr] = searchLangs((inPath))
    if code == False:
        # print("跳过: ", i)
        return
    outPath = inPath.parent / (inPath.name + ".autosub" + inPath.suffix)
    return trans_srt(inPath, outPath, langArr, enable=enable)


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
    fire.Fire({"gt": gen_trans, "gs": gen_srt, "ts": trans_srt, "ats": auto_trans_srt})
