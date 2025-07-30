import grequests  # must sure first import
import pysrt
from tool import (
    create_srt,
    check_exists,
    searchLangs,
    get_timeout_log,
    fix_unicode_bug,
    mergeCache,
)
from pathlib import Path
import json
import time

from rich.progress import Progress


langs = [  # 格式为: [[originSuffix, tagetSuffix, -SRC, -D]]
    [".en.srt", "deeplx", "EN", "ZH"],
    [".en-us.srt", "deeplx", "EN", "ZH"],
    [".en-GB.srt", "deeplx", "EN", "ZH"],
    [".en-en.srt", "deeplx", "EN", "ZH"],
    [".en-en-GB.srt", "deeplx", "EN", "ZH"],
    [".txt.srt", "deeplx", "EN", "ZH"],
    [".ja.srt", "deeplx", "JA", "ZH"],
]

with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

proxies = {
    "http": config.get("http_proxy", None),
    "https": config.get("https_proxy", None),
}


def exception_handler(request, exception):
    print("Request failed", exception)


def get_data_list(data_list):
    return [
        {**i, "index": index}
        for index, i in enumerate(data_list)
        if "text2" not in i or i["text2"] == ""
    ]


def run_deeplx(
    srtPath, overwrite=True, timeout=300, size=6, max_retry=6, enable_timeout_skip=False
):
    srtPath = Path(fix_unicode_bug(srtPath))

    [code, langArr] = searchLangs(srtPath, langs)
    outSrtPath = ".".join(
        [
            srtPath.as_posix().rsplit(".", 1)[0],
            langArr[1],
            langArr[3].lower(),
            srtPath.as_posix().rsplit(".", 1)[1],
        ]
    )
    cacheOutSrtPath = outSrtPath + ".cache"
    path_list = [outSrtPath]

    if not overwrite and check_exists(path_list):
        return path_list

    data_list = []
    subs = pysrt.open(srtPath)
    for sub in subs:
        data_list.append({"start": sub.start, "end": sub.end, "text": sub.text})

    data_list = mergeCache(cacheOutSrtPath, data_list, mode="load")

    _data_list = get_data_list(data_list)

    with Progress() as progress:
        task = progress.add_task("[green]translate...", total=len(_data_list))

        for retry in range(max_retry):
            _data_list = get_data_list(data_list)
            if len(_data_list) == 0:
                continue
            _l = [i["index"] for i in _data_list] if len(_data_list) < 10 else "..."
            print(f"retry: {retry + 1} count: {len(_data_list)} list: {_l}")

            urls = (
                grequests.post(
                    config["deeplx_api"],
                    json={
                        "text": i["text"],
                        "source_lang": langArr[2],
                        "target_lang": langArr[3],
                    },
                    proxies=proxies,
                )
                for i in _data_list
            )

            for index, r in grequests.imap_enumerated(urls, size=size):
                if r and r.status_code == 200:
                    json_data = r.json()
                    if "data" in json_data and json_data["data"] != "":
                        _data_list[index]["text2"] = json_data["data"]
                        progress.update(task, advance=1)
            for i in _data_list:
                data_list[i["index"]] = i

            mergeCache(cacheOutSrtPath, data_list, mode="dump")

            time.sleep(3)

    _data_list = get_data_list(data_list)
    if len(_data_list) > 0:
        if enable_timeout_skip:
            with open(get_timeout_log(srtPath), "w") as f:
                f.write("")
        raise RuntimeError(f"数量不对, 请重试 {len(_data_list)}")

    mergeCache(cacheOutSrtPath, data_list, mode="clean")

    data = create_srt([[i["text2"], str(i["start"]), str(i["end"])] for i in data_list])
    with open(outSrtPath, "w", encoding="utf8") as f:
        f.write(data)

    return path_list


def test():
    print("run test2")
    run_deeplx(
        r"D:\my_repo\parrot_fashion\download\Kurzgesagt – In a Nutshell\Kurzgesagt – In a Nutshell - Videos UCsXVk37bltHxD1rDPwtNM8Q\2023\20230214 TYPFenJQciw\wc2\20230214 TYPFenJQciw.rewrite.en.srt"
    )
    return


if __name__ == "__main__":
    # run_deeplx(
    #     r"D:\my_repo\parrot_fashion\download\Kurzgesagt – In a Nutshell\Kurzgesagt – In a Nutshell - Videos UCsXVk37bltHxD1rDPwtNM8Q\2023\20230214 TYPFenJQciw\wc2\20230214 TYPFenJQciw.rewrite.en.srt"
    # )

    url = config["deeplx_api"]
    headers = {
        "Content-Type": "application/json",
    }
    payload = {"text": "hello world", "source_lang": "EN", "target_lang": "ZH"}

    reqs = (
        grequests.post(url, data=json.dumps(data), proxies=proxies)
        for url, data in [[url, payload]]
    )

    for index, r in grequests.imap_enumerated(reqs, size=1):
        print(r.status_code)
        if r and r.status_code == 200:
            json_data = r.json()
            print(json_data)
