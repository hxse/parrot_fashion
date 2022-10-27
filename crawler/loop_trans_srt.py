#!/usr/bin/env python3
# coding: utf-8
from pathlib import Path

from autosub_tool import gen_srt, gen_trans, trans_srt, set_middle_suffix
from caption_download import is_file
from pathlib import Path
import json
import yt_dlp
import fire


def get_ydl():
    ydl_opts = {"proxy": "127.0.0.1:7890"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        # data = json.dumps(ydl.sanitize_info(info))
        id = info["id"]
        title = info["title"]
        uploader = info["uploader"]
        upload_date = info["upload_date"] if "upload_date" in info else None
        isPlaylist = info["Playlist"] if "Playlist" in info else None

        import pdb

        pdb.set_trace()


def trans2srt(i: Path):
    [path, isSkip] = is_file(set_middle_suffix(i.as_posix(), "autosub.zh-cn"))
    if isSkip or ".autosub.zh-cn.srt" in i.as_posix():
        print("已存在,跳过", i.as_posix())
        return
    trans_srt(i.as_posix(), set_middle_suffix(i.as_posix(), "autosub"), langs)


langs = [  # 格式为: [[originSuffix, tagetSuffix, -SRC, -D]]
    [".en.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    [".en-us.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    # [".en-GB.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    # [".en-en-GB.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    [".txt.srt", ".autosub.zh-ch.srt", "en", "zh-cn"],
    [".ja.srt", ".autosub.zh-ch.srt", "ja", "zh-cn"],
]


def searchLangs(path, langs=langs):
    for i in langs:
        if path.as_posix().endswith(i[0]):
            return [True, i]
    return [False, None]


def loop_trans_srt(dirPath, langs=langs):
    fileArr = [i for i in Path(dirPath).rglob(f"*.srt")]
    for i in fileArr:
        [code, langArr] = searchLangs(i)
        if code == False:
            # print("跳过: ", i)
            continue
        targetPath = Path(set_middle_suffix(i.as_posix(), "autosub"))
        realTargetPath = Path(set_middle_suffix(i.as_posix(), f"autosub.{langArr[3]}"))
        [path, isSkip] = is_file(realTargetPath)
        if isSkip:
            print("已存在,跳过", i.as_posix())
            continue
        print('start: ',i)
        trans_srt(i.as_posix(), targetPath, langArr)


def trans_srt_from_url(url, dirPath, langs=langs):
    """待完善,参考loop_trans_srt"""
    if "&list=" in url:
        print("请输入video url, 或者playlist url")
        return
    last = url.split("/")[-1]
    videoTag = "watch?v="
    playlistTag = "playlist?list="
    if videoTag in last:
        print("is video url")
        key = last.split(videoTag)[-1]

        fileArr = [i for i in Path(dirPath).rglob(f"* {key}*")]
        for file in fileArr:
            if file.suffix == ".srt":
                if Path(file.stem).suffix in langs:
                    trans2srt(file)

    elif playlistTag in last:
        print("is playlist url")
        key = last.split(playlistTag)[-1]

        playlistDir = [i for i in Path(dirPath).rglob(f"* {key}")][0]
        if not playlistDir:
            print("找不到文件夹", playlistDir)
            return
        fileArr = [i for i in playlistDir.rglob(f"*")]

        for file in fileArr:
            if file.suffix == ".srt":
                if Path(file.stem).suffix in langs:
                    trans2srt(file)


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=XyCY6mjWOPc"
    url = "https://www.youtube.com/playlist?list=PLOGi5-fAu8bGPtHQUIlPPCJkYsTsRbATs"
    # url = "https://www.youtube.com/watch?v=L7vXZ1BnTBI&list=PLOGi5-fAu8bGPtHQUIlPPCJkYsTsRbATs&index=2"

    # get_video(url, "D:\my_repo\parrot_fashion\download")
    fire.Fire({"ts": loop_trans_srt})
