import requests
import json
from pathlib import Path
from tool import check_exists, check_punctuation, create_word_srt
import pysrt

template = '''
1. Repartition the following text to shortest sentences with new line.
2. Do not change the punctuation of the original text.
3. Don't say anything unnecessary, return the code format directly.

example text
```
Hello, this is 6 Minute English from BBC Learning English. I'm Neil. And I'm Beth. Now, imagine a field polluted by spilled oil. Toxic waste has mixed into the water and chemical fumes have overtaken the air, leaving animals dead and the land unsafe for humans. Unfortunately, situations like this are common all over the world. Cleaning up chemical pollution is dangerous and expensive and mostly involves highly technological equipment. But what if there was a more natural solution? Recently, scientists have been developing a new technique for cleaning pollution – letting plants do the work instead. Yes, plants like water hyacinth have been used to clean rivers by sucking up oil spilled into the water, and researchers have successfully used fungi to break down plastic waste.
```

return example text
```
Hello, this is 6 Minute English from BBC Learning English.
I'm Neil.
And I'm Beth.
Now, imagine a field polluted by spilled oil.
Toxic waste has mixed into the water and chemical fumes have overtaken the air, leaving animals dead and the land unsafe for humans.
Unfortunately, situations like this are common all over the world.
Cleaning up chemical pollution is dangerous and expensive and mostly involves highly technological equipment.
But what if there was a more natural solution?
Recently, scientists have been developing a new technique for cleaning pollution – letting plants do the work instead.
Yes, plants like water hyacinth have been used to clean rivers by sucking up oil spilled into the water, and researchers have successfully used fungi to break down plastic waste.
```

Text that needs to be processed
```
{}
```
'''


def aurora_requests(text):
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)

    headers = {
        'Content-Type': 'application/json',
    }
    json_data = {
        'model': 'gpt-4-turbo',
        'messages': [
            {
                'role': 'user',
                'content': text,
            },
        ],
        'stream': False,
    }
    response = requests.post(config["aurora_api"],
                             headers=headers,
                             json=json_data)

    assert response.status_code == 200, f'aurora requests error {response.status_code }'

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return content


def rewrite_text(textSrtPath,
                 wordSrtPath,
                 srtPath,
                 rewrite_mode="aurora",
                 overwrite=True):

    rewriteSrtPath = Path(
        '.'.join(textSrtPath.as_posix().split(".")[:-3] + ["rewrite"] +
                 textSrtPath.as_posix().split(".")[-2:]))
    path_list = [rewriteSrtPath]

    if not overwrite and check_exists(path_list):
        return path_list

    with open(textSrtPath, 'r', encoding='utf8') as f:
        text_arr = f.read()

    data = ""
    if rewrite_mode == "aurora":
        data = aurora_requests(template.format(text_arr))
        data = data.strip()
        if data.startswith("```"):
            data = data[3:]
        if data.endswith("```"):
            data = data[:-3]

        # res = []
        # subs = pysrt.open(wordSrtPath)
        # index_list = []
        # _data = data
        # last_length = 0
        # x = 0
        # for sub in subs:
        #     x = _data[x + last_length:].index(sub.text)
        #     index_list.append([x, sub.text, str(sub.start), str(sub.end)])
        #     last_length = len(sub.text)
        #     print(x, '|', sub.text, '|', _data[:10])
        #     import pdb
        #     pdb.set_trace()

        # text = ''
        # for sub in res:
        #     try:
        #         text = text + f'{sub[0]}\n{sub[1]}\n{sub[2]}\n'
        #     except IndexError as e:
        #         print(sub)

    if rewrite_mode == "default":
        with open(srtPath, 'r', encoding='utf8') as f:
            data = f.read()

    res = [[[], [], []]]
    if rewrite_mode == "punctuation":
        subs = pysrt.open(wordSrtPath)
        for sub in subs:
            res[-1][0].append(sub.text)
            res[-1][1].append(str(sub.start))
            res[-1][2].append(str(sub.end))
            if check_punctuation(sub.text) and len(res[-1][0]) > 6:
                res.append([[], [], []])

    data = create_word_srt(res)

    with open(rewriteSrtPath, 'w', encoding='utf8') as f:
        f.write(data)

    return path_list


if __name__ == '__main__':
    text = '''Hello, this is 6 Minute English from BBC Learning English. I'm Neil. And I'm Rob. Now, I'm sure most of us have interacted with a chatbot. These are bits of computer technology that respond to text, with text, or respond to your voice. You ask it a question and usually it comes up with an answer. Yes, it's almost like talking to another human, but of course it's not. It's just a clever piece of technology. It's becoming more sophisticated, more advanced and complex. But could they replace real human interaction altogether? We'll discuss that more in a moment and find out if chatbots really think for themselves. But first I have a question for you, Rob. The first computer programme that allowed some kind of plausible conversation between humans and machines was invented in 1966. But what was it called? Was it... a. Alexa b. Eliza or c. Parry Well it's not Alexa, that's too new, so I'll guess c. Parry. I'll reveal the answer at the end of the programme.'''
    data = aurora_requests(text)
    print(data)
