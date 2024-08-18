import fire
from pathlib import Path
import subprocess
import os
from tts_anki import gen_apkg
from tts_deeplx import run_deeplx_hook
from tool import check_file


def run_subprocess(command, number, max_retry=2):
    for i in range(max_retry):
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if b"ClientConnectorError: Cannot connect to host" in result.stdout:
            print(number, "retry", i + 1)
        else:
            print(number, "success")
            return


def get_tts_outdir(in_file):
    return Path(in_file).parent / "tts_audio"


def get_tts_outfile(in_file, n):
    out_dir = get_tts_outdir(in_file)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{n}.mp3"
    return out_file


def create_tts(in_file, data, max_retry=5):
    resArr = []
    for i in data:
        n = i["n"]
        text = i["text"]
        text2 = i["text2"]

        out_file = get_tts_outfile(in_file, n)
        if not check_file(out_file):
            resArr.append({"text": text, "out_file": out_file, "text2": text2, "n": n})

    print(f"run{max_retry}... {len(resArr)}/{len(data)}")

    for i in resArr:
        text = i["text"]
        out_file = i["out_file"]
        text2 = i["text2"]
        command = f'edge-tts --text "{text}" --write-media "{out_file}"'
        run_subprocess(command, number=i["n"])

    if len(resArr) == 0 or max_retry == 0:
        print("balance", len(resArr))
        return
    else:
        return create_tts(in_file, data, max_retry - 1)


def main(in_file, enable_deeplx=True):
    """
    根据一个txt来自动生成ms-tts, 用\t分割字段, 没有译文会自动用deepl翻译
    """
    if enable_deeplx:
        in_file = run_deeplx_hook(in_file)

    with open(in_file, "r", encoding="utf8") as f:
        file_data = f.readlines()

    data = []
    for n, i in enumerate(file_data):
        text = i.strip().split("\t")[0]
        text2 = i.strip().split("\t")[1]
        data.append({"n": n, "text": text, "text2": text2})
    create_tts(in_file, data)

    for n, i in enumerate(file_data):
        out_file = get_tts_outfile(in_file, n)
        if not check_file(out_file):
            raise RuntimeError(f"ms-tts 数量不对,请重试 {out_file}")

    gen_apkg(get_tts_outdir(in_file), in_file)


if __name__ == "__main__":
    fire.Fire(main)
