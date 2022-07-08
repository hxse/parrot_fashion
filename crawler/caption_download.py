#!/usr/bin/env python3
# coding: utf-8

from unittest import skip
from typing import Dict, Optional
import os
import re
from pathlib import Path


def validateName(name, target=""):
    re_str = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_name = re.sub(re_str, target, name)
    return new_name.strip()


def is_file(filePath, targetSize=None):
    isSkip = False
    if Path(filePath).is_file():
        size = Path(filePath).stat().st_size
        if targetSize == None:
            if size > 0:
                isSkip = True
        elif targetSize == size:
            isSkip = True
    return [filePath, isSkip]


def is_glob_file(output_path, videoId, targetSize=None):
    for i in output_path.glob(f"*_{videoId}.mp3"):
        [filePath, isSkip] = is_file(i, targetSize)
        return [filePath, isSkip]
    return [output_path, False]


def get_caption_file_path(
    title: str,
    code: str,
    srt: bool = True,
    output_path: Optional[str] = None,
    filename_prefix: Optional[str] = None,
):
    if title.endswith(".srt") or title.endswith(".xml"):
        filename = ".".join(title.split(".")[:-1])
    else:
        filename = title

    # if filename_prefix:
    #     filename = f"{safe_filename(filename_prefix)}{filename}"

    # filename = safe_filename(filename)
    filename_prefix = "" if filename_prefix == None else filename_prefix
    filename = validateName(f"{filename_prefix}{filename}")

    # filename += f"_{code}"

    if srt:
        filename += ".srt"
    else:
        filename += ".xml"

    # file_path = os.path.join(target_directory(output_path), filename)
    file_path = output_path / filename
    return filename, file_path


def download(
    self,
    title: str,
    srt: bool = True,
    output_path: Optional[str] = None,
    filename_prefix: Optional[str] = None,
) -> str:
    """
    这里是直接复制源代码然后修改一下
    https://github.com/pytube/pytube/blob/master/pytube/captions.py
    """
    """Write the media stream to disk.

    :param title:
        Output filename (stem only) for writing media file.
        If one is not specified, the default filename is used.
    :type title: str
    :param srt:
        Set to True to download srt, false to download xml. Defaults to True.
    :type srt bool
    :param output_path:
        (optional) Output path for writing media file. If one is not
        specified, defaults to the current working directory.
    :type output_path: str or None
    :param filename_prefix:
        (optional) A string that will be prepended to the filename.
        For example a number in a playlist or the name of a series.
        If one is not specified, nothing will be prepended
        This is separate from filename so you can use the default
        filename but still add a prefix.
    :type filename_prefix: str or None

    :rtype: str
    """

    filename, file_path = get_caption_file_path(
        title, self.code, output_path=output_path
    )

    with open(file_path, "w", encoding="utf-8") as file_handle:
        if srt:
            file_handle.write(self.generate_srt_captions())
        else:
            file_handle.write(self.xml_captions)

    return file_path
