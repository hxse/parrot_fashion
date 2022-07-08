#!/usr/bin/env python3
# coding: utf-8
from msilib.schema import Class
from turtle import down
from pytube.helpers import install_proxy
from pytube import Playlist, Caption
import fire
import re
from pathlib import Path
from pytube.helpers import safe_filename
from caption_download import download, is_file, validateName, get_caption_file_path
from pytube import YouTube
from urllib.parse import urlparse, parse_qs


proxy = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
timeout = 30
max_retries = 5
install_proxy(proxy)
captionArr = ["en", "en-GB", "zh-HK", "zh-TW", "ja"]
only_audio = True
suffix = ".mp3" if only_audio else ".mp4"


def download_video(
    video,
    videoId,
    preNum=None,
    count=None,
    fileName=None,
    suffix=".mp3",
    output_path=".",
    captionArr=captionArr,
):
    output_path = Path(output_path)
    url = video.watch_url
    author = validateName(video.author)
    title = validateName(video.title)
    if not fileName:
        fileName = validateName(f"{title}" if preNum == None else f"{preNum} {title}")
    [p, isSkip] = is_file(output_path / (fileName + suffix))
    if isSkip:
        print("已跳过mp3:", f"{preNum}/{count}", fileName, url)
    else:
        print("开始下载:", f"{preNum}/{count}", fileName, url)
        # 这里用filename参数,用自己的validateName去处理,如果忽略的话,就会用默认的file_safe去处理,会把单引号处理掉
        # 自带的skip_existing=True, 这个选项太慢了
        video.streams.filter(only_audio=only_audio).first().download(
            filename=fileName + suffix,
            output_path=output_path,
            timeout=timeout,
            max_retries=max_retries,
        )

    for caption in captionArr:
        if caption in video.captions:
            fileName = f"{fileName}.ytb.{caption}"
            c = video.captions[caption]

            fn, file_path = get_caption_file_path(
                fileName, caption, output_path=output_path
            )
            [p, isSkip] = is_file(file_path)
            if isSkip:
                print("已跳过srt:", fileName)
            else:
                c.download = download
                c.download(c, fileName, output_path=output_path)


def get_videoId(url):
    urlObj = urlparse(url)
    return urlObj.query.split("=")[1]


def get_video(url, captionArr=captionArr, output_path=None):
    """
    get video from youtube
    """
    video = YouTube(url)
    author = video.author
    videoId = get_videoId(url)
    if not output_path:
        output_path = f"download/{validateName(author)}/videos"
    download_video(
        video,
        videoId,
        preNum=1,
        count=1,
        output_path=output_path,
        captionArr=captionArr,
    )


def get_playlist(url, skip=0, captionArr=captionArr):
    """
    get all videos from youtube playlist
    url: example -> https://www.youtube.com/playlist?list=PLcetZ6gSk96-FECmH9l7Vlx5VDigvgZpt
    captionArr: default -> ["en", "en-GB", "zh-HK", "zh-TW", "ja"]
    """
    playlist = Playlist(url)
    playListTitle = validateName(playlist.title)
    owner = validateName(playlist.owner)
    count = len(playlist.videos)
    print(f"Downloading: {playlist.title}")
    for num in range(count, 0, -1):
        idx = count - num + 1
        if idx <= skip:
            print(f"指定跳过前{idx}个")
            continue
        preNum = str(idx).zfill(len(str(count)))
        url = playlist.video_urls[num - 1]

        video = playlist.videos[num - 1]
        videoId = get_videoId(url)
        output_path = (
            f"download/{validateName(owner)}/playlist/{validateName(playListTitle)}"
        )
        download_video(
            video,
            videoId,
            preNum=preNum,
            count=count,
            output_path=output_path,
            captionArr=captionArr,
        )


if __name__ == "__main__":
    # '''
    # 解决报错: pytube.exceptions.RegexMatchError: get_throttling_function_name: could not find match for multiple
    # 试试这个：
    # 打开文件 C:\Users\jjpj1390\AppData\Local\Programs\Python\Python310\lib\site-packages\pytube\cipher.py
    # 更改第 272 ~ 273 行

    # r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
    # r'\([a-z]\s*=\s*([a-zA-Z0-9$]{2,3})(\[\d+\])?\([a-z]\)'

    # 并更改第 288 行
    # nfunc=re.escape(function_match.group(1)))

    # https://github.com/pytube/pytube/issues/1281
    # https://stackoverflow.com/questions/68945080/pytube-exceptions-regexmatcherror-get-throttling-function-name-could-not-find/71903013#71903013
    # '''

    """
    解决: start = float(child.attrib["start"])  KeyError: 'start'
    https://github.com/pytube/pytube/issues/1085
    """
    fire.Fire({"gp": get_playlist, "gv": get_video})
