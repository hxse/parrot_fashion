#!/usr/bin/env python3
# coding: utf-8
from fileinput import filename
import subprocess
import json
from caption_download import download, is_file, validateName, get_caption_file_path
from get_youtube import get_video, download_video
from pytube import YouTube
from pathlib import Path

aria2 = '--external-downloader aria2c --external-downloader-args "-x 16  -k 1M"'


def convert_json(data):
    # outData = data.encode().decode(
    #     # "unicode-escape"
    # )  # or string-escape https://stackoverflow.com/questions/2969044/python-string-escape-vs-unicode-escape
    outJson = json.loads(data)
    return outJson


def get_ydl_video(url, proxy="127.0.0.1:7890"):
    command = (
        f'youtube-dl --proxy {proxy} -j --flat-playlist --no-playlist {aria2} "{url}"'
    )
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, encoding="utf8")
    out, err = p.communicate()
    outJson = convert_json(out.split("\n")[0])

    webpage_url = outJson["webpage_url"]
    uploader_url = outJson["uploader_url"]
    title = outJson["title"]
    id = outJson["id"]
    abr = outJson["abr"]

    import pdb

    pdb.set_trace()


def get_ydl_playlist(url, proxy="127.0.0.1:7890", suffix=".mp3", skip=0):
    command = f'yt-dlp --proxy {proxy} -j --flat-playlist --yes-playlist  -o "%(playlist_index)s-%(title)s"  {aria2} "{url}"'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, encoding="utf8")
    out, err = p.communicate()

    data = []
    for i in out.split("\n"):
        if not i.strip():
            continue
        outJson = convert_json(i)
        data.append(outJson)

    count = len(data)
    for num in range(count, 0, -1):
        idx = count - num + 1
        if idx <= skip:
            print(f"指定跳过前{idx}个")
            continue
        preNum = str(idx).zfill(len(str(count)))

        value = data[num - 1]
        title = value["title"]
        url = f"https://www.youtube.com/watch?v={value['id']}"
        uploader = value["uploader"]
        output_path = Path(f"download/{validateName(uploader)}/videos")
        output_path = Path(
            f"download/{validateName(uploader)}/playlist/{validateName(playListTitle)}"
        )
        fileName = validateName(f"{preNum} {title}")
        [p, isSkip] = is_file((output_path / (fileName + suffix)))
        if isSkip:
            print("已跳过mp3 from playlist:", f"{preNum}/{count}", fileName, url)
            continue

        download_video(
            YouTube(url),
            value["id"],
            preNum=preNum,
            count=count,
            fileName=fileName,
            suffix=".mp3",
            output_path=output_path,
        )
        import pdb

        pdb.set_trace()
    return data


if __name__ == "__main__":
    url = "https://www.youtube.com/playlist?list=PLWizOw9GU6dXEIycdApPtINlJ-VowPLWJ"
    url = "https://www.youtube.com/playlist?list=PLnzvH6pAJKSpPCJaNDqSbJ-s0N3c1cKAQ"
    proxy = "127.0.0.1:7890"

    data = get_ydl_playlist(url, proxy)
    print(data)

    # url = "https://www.youtube.com/watch?v=koiYSKRkIqc"
    # data = get_video(url)
