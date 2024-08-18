from deeplx import run_deeplx
import pysrt
from pysrt.srtitem import SubRipItem
from pathlib import Path
import fire
from tool import check_file


def get_outpath(in_file):
    outPath = ".".join(
        [
            in_file.as_posix().rsplit(".", 1)[0],
            "deeplx",
            in_file.as_posix().rsplit(".", 1)[1],
        ]
    )
    return outPath


def run_deeplx_hook(in_file, timeout=300, overwrite=False):
    in_file = Path(in_file)
    outPath = get_outpath(in_file)
    if check_file(outPath):
        print(f"skip deeplx {outPath}")
        return outPath

    with open(in_file, "r", encoding="utf8") as f:
        file_data = f.readlines()

    srtPath = in_file.parent / (in_file.stem + ".srt")
    with open(srtPath, "w", encoding="utf8") as f:
        f.write("")

    subs = pysrt.open(srtPath, encoding="utf-8")

    data = []
    for n, i in enumerate(file_data):
        text = i.strip().split("\t")[0]
        text2 = i.strip().split("\t")[1]
        data.append({"text": text, "text2": text2, "n": n + 1})

        s = SubRipItem()
        s.index = n + 1
        s.text = text
        s.start.seconds = 10
        s.end.seconds = 20
        subs.append(s)
        subs.save(srtPath, encoding="utf-8")

    [transSrtPath] = run_deeplx(srtPath, timeout=timeout, overwrite=overwrite)
    subs2 = pysrt.open(transSrtPath, encoding="utf-8")

    with open(outPath, "w", encoding="utf8") as f:
        for s, s2 in zip(subs, subs2):
            f.write(f"{s.text}\t{s2.text}\n")

    srtPath.unlink(missing_ok=False)
    Path(transSrtPath).unlink(missing_ok=False)
    return outPath


if __name__ == "__main__":
    fire.Fire(run_deeplx_hook)
