#!/usr/bin/env python3
# coding: utf-8
import json
from fastapi import Request, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
rootPath = Path("../download")
config_path = rootPath / "config.json"


@app.get("/config")
async def read_config():
    with open(config_path, "r", encoding="utf8") as f:
        data = f.read()
    json_data = jsonable_encoder(data)
    print(json_data)
    return JSONResponse(content=json_data)


@app.post("/config")
async def write_config(request: Request):
    json_data = await request.json()
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)
    return JSONResponse(content=json_data)


blacklist = ["archive.txt"]


@app.get("/file_all")
async def file_all():
    fileArr = []
    level = 4
    for file in rootPath.rglob("*"):
        data = {}
        if not file.is_file():
            continue
        if file.name in blacklist:
            continue
        if len(file.parents) < 4:
            continue
        data.update(
            {
                "fileSuffix": file.suffix,
                "author": [*file.parents][-level].name,
                "type": [*file.parents][-(level - 1)].name,
            }
        )
        data.update(
            {
                "filePath": file.as_posix(),
                "fileName": file.name,
                "name": file.name,
                "isFile": file.is_file(),
                "parent": file.parent.name,
            }
        )
        fileArr.append(data)
    json_data = jsonable_encoder(fileArr)
    return JSONResponse(content=json_data)


@app.get("/file")
async def file(path: str):
    print(path)
    return FileResponse(path=path, filename=Path(path).name)


from stardict.stardict import StarDict
from stardict.stardict import LemmaDB

star = StarDict("stardict/stardict.sqlit")
lemma = LemmaDB()
lemma.load("stardict/lemma.en.txt")


@app.get("/dict")
async def get_dict(word: str, stem: bool):
    """
    http://127.0.0.1:8000/dict?word=gave&stem=1
    """
    if stem:
        try:
            data = star.query(lemma.word_stem(word)[0])
        except:
            data = None
    else:
        data = star.query(word)

    json_data = jsonable_encoder(data)
    return JSONResponse(content=json_data)
