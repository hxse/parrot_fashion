import grequests  # must sure first import
from pathlib import Path
import subprocess
import os
import json
import sys
import winreg
from pysrt import SubRipTime


def check_file(out_file):
    return Path(out_file).is_file() and os.stat(out_file).st_size > 0


def time2string(data_list):
    return [{**i, "start": str(i["start"]), "end": str(i["end"])} for i in data_list]


def string2time(data_list):
    return [
        {
            **i,
            "start": SubRipTime.from_string(i["start"]),
            "end": SubRipTime.from_string(i["end"]),
        }
        for i in data_list
    ]


def mergeCache(cacheOutSrtPath, data_list, mode):
    """
    mode: init, merge, clean
    """

    if mode == "load":
        if not Path(cacheOutSrtPath).is_file():
            return data_list
        with open(cacheOutSrtPath, "r", encoding="utf-8") as file:
            data = json.load(file)
            if len(data) == 0:
                return data_list
            return string2time(data)

    if mode == "dump":
        data_list = time2string(data_list)
        with open(cacheOutSrtPath, "w", encoding="utf-8") as file:
            json.dump(data_list, file, ensure_ascii=False, indent=4)

    if mode == "clean":
        Path(cacheOutSrtPath).unlink(missing_ok=True)


def get_handle(
    audioPath,
    whisper_mode="wc2",  # wc2, wsx
    lang="en",
):
    outDir = audioPath.parent / whisper_mode
    handlePath = outDir / f"{audioPath.stem}.handle.{lang}.srt"
    return [handlePath]


def get_timeout_log(srtPath):
    return srtPath.parent / "timeout.log"


def check_punctuation(text, punctuation=".!?"):
    for i in text:
        if i in punctuation:
            return True
    return False


def check_word(text, arr=["Mr.", "Mrs.", "Miss.", "Ms."]):
    if text in arr:
        return False
    return True


def rename_file(oldFile, newFile):
    if newFile.is_file():
        newFile.unlink(missing_ok=True)
    oldFile.rename(newFile)


def check_exists(path_list):
    for i in path_list:
        if not Path(i).exists():
            return False
    return True


def fix_unicode_bug(inPath):
    inPath = Path(inPath)
    if "Kurzgesagt  In a Nutshell" in inPath.as_posix():
        return inPath.as_posix().replace(
            "Kurzgesagt  In a Nutshell", "Kurzgesagt – In a Nutshell"
        )
    if "6 Minute English" in inPath.as_posix():
        return inPath.as_posix().replace("/ 6 Minute English", "/⏲️ 6 Minute English")
    return inPath.as_posix()


def getPathList(dirPath, suffixArr=[".ogg", ".mp3"]):
    _ = [i for i in Path(dirPath).rglob("*") if i.parent.name != "_cache"]
    keyArr = set()
    pathList = []
    for s in suffixArr:
        for i in _:
            k = i.parent / i.stem
            if k not in keyArr:
                if i.suffix == s:
                    keyArr.add(k)
                    pathList.append(i)
    pathList.sort()
    return pathList


def run_process(command, code="utf-8", cwd=None, timeout=None):
    os.environ["PYTHONIOENCODING"] = "utf-8"
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd=cwd,
        encoding="utf-8",
    )
    stdout, stderr = process.communicate(timeout=timeout)
    return [stdout, stderr]


def split_audio(audioPath, splitAudioArr):
    for [splitAudioPath, start, end] in track(
        splitAudioArr, description="split audio file..."
    ):
        Path.mkdir(Path(splitAudioPath).parent, exist_ok=True)
        command = f'ffmpeg -ss {start.replace(",", ".")} -to {end.replace(",", ".")} -i "{audioPath.as_posix()}" -y "{splitAudioPath.as_posix()}"'
        # https://stackoverflow.com/questions/18444194/cutting-the-videos-based-on-start-and-end-time-using-ffmpeg
        # 省略 -c copy 会重新编码,会更慢但更精确，但仍然比在 -i 之后指定 -ss 和 -to 更快，因为这种情况意味着必须在处理完整个输入文件之后才进行修剪
        stdout, stderr = run_process(command)


def mp32ogg(audioPath, srtPath):
    if audioPath.suffix == ".mp3":
        oggPath = audioPath.parent / (audioPath.stem + ".ogg")
        if not oggPath.exists():
            command = f'ffmpeg -i "{audioPath.as_posix()}" -y "{oggPath.as_posix()}"'
            print(command)
            stdout, stderr = run_process(command)
        return oggPath

    return audioPath


def create_word_srt(res):
    data = ""
    n = 0
    for i in res:
        if len(i[0]) > 0:
            n += 1
            data = data + str(n) + "\n"
            data = data + f"{i[1][0]} --> {i[2][-1]}\n"
            data = data + " ".join(i[0]) + "\n"
            data = data + "\n"
    return data


def create_srt(res):
    data = ""
    n = 0
    for i in res:
        if len(i[0]) > 0:
            n += 1
            data = data + f"{n}\n"
            data = data + f"{i[1]} --> {i[2]}\n"
            data = data + f"{i[0]}\n"
            data = data + "\n"
    return data


def searchLangs(path: Path, langs):
    for i in langs:
        if path.as_posix().endswith(i[0]):
            return [True, i]
    return [False, None]


def check_long_paths_enabled():
    """
    检测Windows是否启用长路径支持（不需要管理员权限）

    Returns:
        bool: 返回是否启用了长路径支持
    """
    # 如果不是Windows系统，直接返回True
    if sys.platform != "win32":
        return True

    try:
        # 检查注册表中的长路径设置
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
            0,
            winreg.KEY_READ,
        )
        try:
            value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
            long_paths_enabled = bool(value)
        except WindowsError:
            # 如果注册表项不存在，默认为禁用
            long_paths_enabled = False
        finally:
            winreg.CloseKey(key)

        return long_paths_enabled

    except Exception as e:
        print(f"检查长路径支持时出错: {e}")
        return False


def enable_long_paths():
    """
    尝试启用Windows长路径支持（需要管理员权限）

    Returns:
        bool: 返回是否成功启用长路径支持
    """
    # 如果不是Windows系统，直接返回True
    if sys.platform != "win32":
        return True

    try:
        # 检查是否已经有管理员权限
        import ctypes

        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("警告: 需要管理员权限来启用长路径支持")
            return False

        # 修改注册表启用长路径
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
            0,
            winreg.KEY_WRITE,
        )
        winreg.SetValueEx(key, "LongPathsEnabled", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)

        print("已成功启用Windows长路径支持")
        return True

    except Exception as e:
        print(f"启用长路径支持失败: {e}")
        return False


def check_and_enable_long_paths():
    """
    检测Windows是否启用长路径支持，如果未启用则提供启用指导

    Returns:
        bool: 返回是否启用了长路径支持
    """
    # 检查长路径是否已启用
    if check_long_paths_enabled():
        print("Windows长路径支持已启用")
        return True

    print("Windows长路径支持未启用")

    # 尝试启用长路径支持
    if enable_long_paths():
        return True

    # 如果自动启用失败，提供手动启用指导
    print("请手动启用长路径支持:")
    print("方法1: 以管理员身份运行此脚本")
    print("方法2: 手动修改注册表")
    print("1. 以管理员身份打开注册表编辑器")
    print(
        "2. 导航到 HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\FileSystem"
    )
    print("3. 将 LongPathsEnabled 的值设置为 1")
    print("4. 重启计算机使更改生效")

    return False


# "whisper-ctranslate2>=0.4.4",
# "torch @ https://download.pytorch.org/whl/cu115/torch-1.11.0%2Bcu115-cp310-cp310-win_amd64.whl",
# "torchaudio @ https://download.pytorch.org/whl/cu115/torchaudio-0.11.0%2Bcu115-cp310-cp310-win_amd64.whl",
# "torchvision @ https://download.pytorch.org/whl/cu115/torchvision-0.12.0%2Bcu115-cp310-cp310-win_amd64.whl",
