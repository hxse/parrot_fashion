import subprocess
from pathlib import Path
from tool import check_exists, fix_unicode_bug, get_timeout_log
import os
import fire

langs = [  # 格式为: [[originSuffix, tagetSuffix, -SRC, -D]]
    [".en.srt", "autosub", "en", "zh-cn"],
    [".en-us.srt", "autosub", "en", "zh-cn"],
    [".en-GB.srt", "autosub", "en", "zh-cn"],
    [".en-en.srt", "autosub", "en", "zh-cn"],
    [".en-en-GB.srt", "autosub", "en", "zh-cn"],
    [".txt.srt", "autosub", "en", "zh-cn"],
    [".ja.srt", "autosub", "ja", "zh-cn"],
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
    if type(fileName) != str:
        fileName = fileName.as_posix()
    s = fileName.rsplit(".", 1)
    return s[0] + "." + middle_suffix + "." + s[1]


def run_process(command, code="utf-8", timeout=30):
    os.environ["PYTHONIOENCODING"] = "utf-8"
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=None,
                               shell=True,
                               encoding="utf-8")
    stdout, stderr = process.communicate(timeout=timeout)
    return [stdout, stderr]


def auto_trans_srt(srtPath):
    """
    从英文srt翻译到中文srt,outPath不能带zh-ch, 因为autosub会自动补全zh-cn
    inPath = r"D:\my_repo\parrot fashion\download\BBC Learning English\playlist\6 Minute English - Vocabulary & listening\001 Does wearing a uniform change our behaviour 6 Minute English.autosub.en-us.srt"
    outPath = r"D:\my_repo\parrot fashion\download\BBC Learning English\playlist\6 Minute English - Vocabulary & listening\001 Does wearing a uniform change our behaviour 6 Minute English.autosub.en-us.autosub.srt"
    """
    [code, langArr] = searchLangs(srtPath)
    # outSrtPath = set_middle_suffix(srtPath, f"{langArr[1]}.{langArr[3]}")
    outSrtPath = set_middle_suffix(srtPath, f"{langArr[1]}")

    command = f'autosub -hsp http://127.0.0.1:7890 -i "{srtPath}" -SRC {langArr[2]} -D {langArr[3]} -y -o "{outSrtPath}"'
    stdout, stderr = run_process(command)
    if "All work done." not in str(stdout.strip()):
        raise Exception(f"{stdout} {stderr}")


def autosub_translate_srt(srtPath, overwrite=True, count=7):
    """
    pdm run python .\loop_whisper.py ats 'd:\my_repo\parrot_fashion\download\Kurzgesagt  In a Nutshell\videos\20130822 KsF_hdjWJjo\wsx\20130822 The Solar System -- our home in space KsF_hdjWJjo.mp3.en.srt'
    """
    [code, langArr] = searchLangs(Path(srtPath))
    outSrtPath = set_middle_suffix(srtPath, f"{langArr[1]}.{langArr[3]}")
    path_list = [outSrtPath]

    if not overwrite and check_exists(path_list):
        return path_list

    for i in range(count):
        try:
            auto_trans_srt(srtPath)
            return path_list
        except Exception as e:
            if type(e) == subprocess.TimeoutExpired:
                with open(get_timeout_log(srtPath), 'w') as f:
                    f.write("")
                raise Exception(f"[bold red]翻译超时[/bold red] {srtPath}")
            print(f"[bold red]翻译失败[/bold red] 次数: {i+1}/{count}")
    raise Exception(f"[bold red]翻译失败[/bold red] {srtPath}")


if __name__ == "__main__":
    # pip install git+https://github.com/BingLingGroup/autosub.git@dev ffmpeg-normalize langcodes
    # pdm add git+https://github.com/BingLingGroup/autosub.git@dev ffmpeg-normalize langcodes
    fire.Fire({"ats": auto_trans_srt})
