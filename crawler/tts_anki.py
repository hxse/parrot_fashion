import genanki
import random
from pathlib import Path
import fire


def gen_model(model_name):
    # model_id = random.randrange(1 << 30, 1 << 31)  # 随机唯一id
    model_id = sum([ord(char) for char in model_name])
    my_model = genanki.Model(
        model_id,
        model_name,
        fields=[
            {"name": "expression"},
            {"name": "meaning"},
            {"name": "audio"},
        ],
        templates=[
            {
                "name": "audio_templates",
                "qfmt": "<h1>{{audio}}</h1>",  # AND THIS
                "afmt": "<!-- {{FrontSide}}--><h1>{{audio}}</h1><br><h1>{{furigana:expression}}</h1><br><h2>{{furigana:meaning}}<h2>",
            },
        ],
        css="h1, h2{text-align: center;}",  # white-space: pre-line
    )
    return my_model


def gen_note(my_model, textArr, textArr2, audioArr):
    noteArr = []
    for t, t2, audio in zip(textArr, textArr2, audioArr):
        my_note = genanki.Note(
            model=my_model,
            fields=[
                t.strip().replace("\n", "<br>"),
                t2.strip().replace("\n", "<br>"),
                f"[sound:{audio.name}]",
            ],
        )
        noteArr.append(my_note)
    return noteArr


def get_file_arr(audioDir, textPath):
    audioArr = []
    textArr = []
    textArr2 = []
    with open(textPath, "r", encoding="utf8") as f:
        data = f.readlines()
        for i in data:
            text = i.strip().split("\t")[0]
            text2 = i.strip().split("\t")[1]
            textArr.append(text)
            textArr2.append(text2)
    for n, i in enumerate(textArr):
        audioArr.append(Path(audioDir) / f"{n}.mp3")
    assert len(audioArr) == len(textArr) == len(textArr2), f"数量不对,请检查{textPath}"
    return audioArr, textArr, textArr2


def gen_apkg(
    audioDir,
    textPath,
):
    """
    pdm run .\tts_anki.py "D:\my_repo\parrot_fashion\download\tts_demo\IELTS100\tts_cache" "D:\my_repo\parrot_fashion\download\tts_demo\IELTS100\IELTS100.txt"
    """
    audioArr, textArr, textArr2 = get_file_arr(audioDir, textPath)
    outPath = Path(textPath).parent / (Path(textPath).stem + ".apkg")

    deck_name = Path(outPath).name
    deck_id = random.randrange(1 << 30, 1 << 31)  # 随机唯一id
    my_deck = genanki.Deck(deck_id, deck_name)
    my_package = genanki.Package(my_deck)

    my_model = gen_model(deck_name.split(":")[0])
    noteArr = gen_note(my_model, textArr, textArr2, audioArr)
    for my_note in noteArr:
        my_deck.add_note(my_note)

    for i in audioArr:
        my_package.media_files.append(str(i))

    my_package.write_to_file(outPath)


if __name__ == "__main__":
    fire.Fire(gen_apkg)
