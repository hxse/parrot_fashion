from faster_whisper import WhisperModel
import fire
from pathlib import Path


def run_faster_whisper(path, output_dir=None, mode="sentence"):
    # model_size = "large-v2"
    model_size = "medium"

    # Run on GPU with FP16
    model = WhisperModel(model_size, device="cuda", compute_type="float16")

    # or run on GPU with INT8
    # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    # or run on CPU with INT8
    # model = WhisperModel(model_size, device="cpu", compute_type="int8")

    data = []
    if mode == "sentence":
        segments, info = model.transcribe(path, beam_size=5)
        print(
            "Detected language '%s' with probability %f"
            % (info.language, info.language_probability)
        )
        for segment in segments:
            text = "[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text)
            data.append(text)
            print(text)

    if mode == "words":
        segments, _ = model.transcribe(path, word_timestamps=True)
        for segment in segments:
            for word in segment.words:
                text = "[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word)
                data.append([word.start, word.end, word.word])
                print(text)

    if output_dir:
        output_file = Path(output_dir) / Path(path).stem
        with open(output_file, "w", encoding="utf8") as f:
            f.writelines(data)
            import pdb

            pdb.set_trace()


if __name__ == "__main__":
    # 只是写个demo, 实际上用不着, 因为可以直接全局安装whisper-ctranslate2, 用cli的方式调用
    fire.Fire({"fw": run_faster_whisper})
