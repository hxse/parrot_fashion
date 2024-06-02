import fire
from pathlib import Path
from tool import fix_unicode_bug, getPathList
from rich import print
from run_whisper import run_whisper
from rewrite_text import rewrite_text
from autosub_tool import autosub_translate_srt
from gen_anki import generate_anki_deck
from import_apkg import import_anki_apkg

initial_prompt_default = "Hello, welcome to my lecture. Separate sentences with punctuation symbols, use punctuation symbols to shorten sentences, mandatory use of punctuation symbols."


def loop(
    dirPath,
    overwrite=False,
    whisper_mode="wc2",
    rewrite_mode="punctuation",  #default #punctuation #aurora
    lang="en",
    initial_prompt=initial_prompt_default,
    import_anki="",
    anki_app="",
):
    """
    pdm run python .\loop.py loop "d:\my_repo\parrot_fashion\download\Kurzgesagt – In a Nutshell\Kurzgesagt – In a Nutshell - Videos UCsXVk37bltHxD1rDPwtNM8Q" 1 1 1 1
    """
    dirPath = Path(fix_unicode_bug(dirPath))
    assert dirPath.is_dir(), f"dirPath,不是文件夹 {dirPath}"

    pathList = getPathList(dirPath)

    for index, audioPath in enumerate(pathList):

        print(
            f"run:  {index + 1}/{len(pathList)} [bold black]{audioPath.name}[/bold black]"
        )

        [srtPath, wordSrtPath, textSrtPath,
         jsonPath] = run_whisper(audioPath=audioPath,
                                 whisper_mode=whisper_mode,
                                 lang=lang,
                                 initial_prompt=initial_prompt,
                                 overwrite=overwrite)

        [rewriteSrtPath] = rewrite_text(textSrtPath,
                                        wordSrtPath,
                                        srtPath,
                                        rewrite_mode=rewrite_mode,
                                        overwrite=overwrite)

        [transSrtPath] = autosub_translate_srt(rewriteSrtPath,
                                               overwrite=overwrite)

        [outApkgPath] = generate_anki_deck(audioPath=audioPath,
                                           srtPath=rewriteSrtPath,
                                           srt2Path=transSrtPath,
                                           overwrite=overwrite)

        if import_anki:
            import_anki_apkg(import_anki=import_anki, ankiPath=outApkgPath)


if __name__ == '__main__':
    fire.Fire({
        "loop": loop,
    })
