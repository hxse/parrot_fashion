#!/usr/bin/env python3
# coding: utf-8
from pathlib import Path
import re


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
