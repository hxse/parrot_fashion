from pathlib import Path
import subprocess


def check_punctuation(text, punctuation='.!?'):
    for i in text:
        if i in punctuation:
            return True
    return False


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
        return inPath.as_posix().replace("Kurzgesagt  In a Nutshell",
                                         "Kurzgesagt – In a Nutshell")
    if "6 Minute English" in inPath.as_posix():
        return inPath.as_posix().replace("/ 6 Minute English",
                                         "/⏲️ 6 Minute English")
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


def run_process(command, cwd=None, timeout=None):
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd=cwd,
    )
    stdout, stderr = process.communicate(timeout=timeout)
    return [stdout, stderr]


def split_audio(audioPath, splitAudioArr):
    for [splitAudioPath, start,
         end] in track(splitAudioArr, description="split audio file..."):
        Path.mkdir(Path(splitAudioPath).parent, exist_ok=True)
        command = f'ffmpeg -ss {start.replace(",",".")} -to {end.replace(",",".")} -i "{audioPath.as_posix()}" -y "{splitAudioPath.as_posix()}"'
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


# "whisper-ctranslate2>=0.4.4",
# "torch @ https://download.pytorch.org/whl/cu115/torch-1.11.0%2Bcu115-cp310-cp310-win_amd64.whl",
# "torchaudio @ https://download.pytorch.org/whl/cu115/torchaudio-0.11.0%2Bcu115-cp310-cp310-win_amd64.whl",
# "torchvision @ https://download.pytorch.org/whl/cu115/torchvision-0.12.0%2Bcu115-cp310-cp310-win_amd64.whl",
