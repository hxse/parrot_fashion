from pathlib import Path


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


# "whisper-ctranslate2>=0.4.4",
# "torch @ https://download.pytorch.org/whl/cu115/torch-1.11.0%2Bcu115-cp310-cp310-win_amd64.whl",
# "torchaudio @ https://download.pytorch.org/whl/cu115/torchaudio-0.11.0%2Bcu115-cp310-cp310-win_amd64.whl",
# "torchvision @ https://download.pytorch.org/whl/cu115/torchvision-0.12.0%2Bcu115-cp310-cp310-win_amd64.whl",
