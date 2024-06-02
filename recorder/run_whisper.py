import subprocess
import json
import datetime
from tool import check_exists, rename_file


def convert_time(t):
    return str(datetime.timedelta(seconds=t)).replace(".", ",")[:-3]


def run_whisper(
        audioPath,
        whisper_mode="wc2",  # wc2, wsx
        lang="en",
        initial_prompt="",
        overwrite=True):
    r'''
    RuntimeError: Library cublas64_12.dll is not found or cannot be loaded. 'copy and rename' Solve the problem
    C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\bin
    https://github.com/SYSTRAN/faster-whisper/issues/535

    insanely-fast-whisper
    "torch @ https://download.pytorch.org/whl/cu115/torch-1.11.0%2Bcu115-cp310-cp310-win_amd64.whl",
    "torchaudio @ https://download.pytorch.org/whl/cu115/torchaudio-0.11.0%2Bcu115-cp310-cp310-win_amd64.whl",
    "torchvision @ https://download.pytorch.org/whl/cu115/torchvision-0.12.0%2Bcu115-cp310-cp310-win_amd64.whl",
    '''

    outDir = audioPath.parent / whisper_mode
    if whisper_mode == "wc2":
        #  --vad_threshold 0.93以上才能过滤背景音乐,
        vad_filter = "--vad_filter True --vad_threshold 0.98"
        model = "--model medium.en" if lang == "en" else "--model medium"
        initial_prompt = f'--initial_prompt "{initial_prompt}"'
        command = f'whisper-ctranslate2 --language {lang} --output_dir "{outDir.as_posix()}" {vad_filter} {model}  --word_timestamps True {initial_prompt} "{audioPath.as_posix()}"'
        jsonPath = outDir / f"{audioPath.stem}.{lang}.json"
        srtPath = outDir / f"{audioPath.stem}.{lang}.srt"
        wordSrtPath = outDir / f"{audioPath.stem}.word.{lang}.srt"
        textSrtPath = outDir / f"{audioPath.stem}.text.{lang}.srt"
        path_list = [srtPath, wordSrtPath, textSrtPath, jsonPath]

        if not overwrite and check_exists(path_list):
            return path_list

        print(command)
        subprocess.run(command)

        # 保证生成文件命名格式一致
        arr = []
        word_arr = []
        text_arr = []
        n = 1
        rename_file((outDir / f"{audioPath.stem}.json"), jsonPath)
        with open(jsonPath, "r", encoding="utf-8") as file:
            data = json.load(file)
        for i in data["segments"]:
            arr.append(
                f"{i['id']}\n{convert_time(i['start'])} --> {convert_time(i['end'])}\n{i['text'].strip()}\n\n"
            )
            for i in i["words"]:
                word_arr.append(
                    f"{n}\n{convert_time(i['start'])} --> {convert_time(i['end'])}\n{i['word'].strip()}\n\n"
                )
                text_arr.append(f"{i['word'].strip()} ")
                n += 1
        with open(srtPath, "w", encoding="utf-8") as file:
            file.writelines(arr)
        with open(wordSrtPath, "w", encoding="utf-8") as file:
            file.writelines(word_arr)
        with open(textSrtPath, "w", encoding="utf-8") as file:
            file.writelines(text_arr)

        suffix = [".json", ".srt", ".tsv", ".txt", ".vtt"]
        for i in suffix:
            if i == ".json":
                pass
            else:
                (outDir / f"{audioPath.stem}{i}").unlink(missing_ok=True)
        return path_list
