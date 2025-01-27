import fire
from pathlib import Path
import csv
import pandas as pd
import shutil
import rarfile
import pysubs2

import chardet


def detect_encoding(file_path):
    with open(file_path, "rb") as file:
        detector = chardet.universaldetector.UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result["encoding"]


def convert_file(file_path, code):
    with open(file_path, "r", encoding=code) as f:
        data = f.read()
    with open(file_path, "w", encoding="utf8") as f:
        f.write(data)


def load_csv(path):
    return pd.read_csv(path)


def search_name(columns, search_array):
    for i in search_array:
        for x in columns:
            if i in str(x):
                return True
    return False


def ass2srt(
    path="",
    select="",
):
    """
    select 1 保留第一行, 2 保留第二行
    """
    path = Path(path)
    code = detect_encoding(path)
    convert_file(path, code)
    subs = pysubs2.load(path)
    srtPath = path.parent / (f"{path.stem}_{select}.srt")
    subs.save(srtPath)
    if select != "":
        subs = pysubs2.load(srtPath)
        for i in subs:
            s = i.text.replace("\\N", "\n").split("\n")
            if select <= len(s):
                i.text = s[select - 1]
        subs.save(srtPath)

def get_srt(
    outDir,
    search_array,
    archiveDir="",
    archiveCsv="",
):
    '''
    py_gs "C:\Users\qmlib\Downloads\test" "破产姐妹,2 Broke Girls"
    '''
    search_array = search_array.split(",")

    csvPath = Path(archiveCsv)
    df = load_csv(csvPath)
    res = df.loc[
        df.apply(
            lambda x: search_name([x["中文名"], x["英文名"]], search_array), axis=1
        )
    ]
    for i in range(len(res)):
        row = res.iloc[i]
        file_path = Path(archiveDir) / row["字幕相对路径"]
        if file_path.is_file():
            try:
                out_path = Path(outDir) / file_path.name
                # file_path.rename(out_path)

                shutil.copy(file_path, out_path)
                if out_path.suffix == ".rar":
                    rf = rarfile.RarFile(out_path)
                    rf.extractall(out_path.parent / row["filename"])
                else:
                    shutil.unpack_archive(out_path, out_path.parent / row["filename"])

                out_path.unlink(missing_ok=True)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    fire.Fire({"gs": get_srt, "as": ass2srt})
