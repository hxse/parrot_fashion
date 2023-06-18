* cd parrot fashion
* python .\crawler\get-youtube.py gp https://www.youtube.com/playlist?list=PLcetZ6gSk96-FECmH9l7Vlx5VDigvgZpt 0
* .\backend\run_server.bat
* 使用yt-dlp下载视频和字幕: `yt-dlp --proxy  127.0.0.1:7890 --concurrent-fragments 10 --yes-playlist   --download-archive archive.txt   --sub-langs "en,en-us,zh-CN,zh-TW,zh-HK,ja" --convert-subs srt --write-auto-subs   --write-subs   -o '%(uploader)s/%(playlist)s/%(upload_date)s %(title)s [%(id)s].%(ext)s'  --extract-audio  --audio-format mp3 $args[0]`
* 用脚本调用autosub
    * .\crawler\autosub_tool.py gt <fileName> <fileDir>
    * .\crawler\autosub_tool.py ts <inPath> <outPath>
* 使用autosub生成字幕
    * 记得安装dev版本,dev版本修复了很多bug
    * https://github.com/BingLingGroup/autosub/blob/dev/docs/README.zh-Hans.md
    * autosub -hsp http://127.0.0.1:7890 -i "视频音频文件"  -S en-us
    * autosub -hsp http://127.0.0.1:7890 -i "字幕文件" -SRC en -D zh-cn
    * 使用半自动操作deepi: https://github.com/BingLingGroup/autosub/issues/141#
* 解除windows文件名长度限制,(不过好像没用?)
    * ```powershell
    New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
    ```
# install cuda, cudnn, zlibwapi.dll
  * install cudo:
    * https://cangmang.xyz/articles/1682852371010
    * 查看cuda系统兼容版本: `nvidia-smi`, 这个只是显示兼容版本, 而不是安装版本
    * 下载cuda(版本要与系统兼容): https://developer.nvidia.com/cuda-toolkit-archive
    * 验证cuda是否安装成功: `nvcc -V`
  * install cudnn:
    * cuda安装成功后,下载cudnn(要与cuda版本兼容): https://developer.nvidia.com/rdp/cudnn-download
    * 然后把cudnn的解压文件复制到cuda路径对应目录中, `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA`
    * 把下面的路径添加到环境变量
    * ```
            C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\bin
            C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\libnvvp
            C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\include
            C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\lib
        ```
    * 运行下面两条命令,如果都出现`Result = PASS`,就说明cudnn安装成功
        * `. "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\extras\demo_suite\deviceQuery.exe"`
        * `. "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\extras\demo_suite\bandwidthTest.exe"`
  * install ziplib:
    * 下载ziplib,不然会提示报错, "Please make sure cudnn_ops_infer64_8.dll is in your library path!"
    * 下载地址: http://www.winimage.com/zLibDll/zlib123dllx64.zip
    * 参考: https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html#install-zlib-windows
    * 然后把zlibwapi.dll所在目录添加进环境变量

# download huggingface model
  * 把`huggingface.co`加入代理,避免网络问题

# install whisper-ctranslate2
  * 需要先安装cuda11.x, cudnn for cuda11.x, zlibwapi.dll
  * 安装后可用命令行调用, pip install -U whisper-ctranslate2
  * whisper-ctranslate2是faster-whisper的cli包装器, 因为faster-whisper不支持cli
  * whisper-ctranslate2 --language en  --word_timestamps True  --vad_filter True  "<audio file>" --output_dir "<output dir>"

# install faster-whisper(不用这个, 用whisper-ctranslate2,cli更方便)
  * whisper-ctranslate2是这个的cli包装器
    * pip install -U whisper-ctranslate2
  * https://github.com/guillaumekln/faster-whisper
  * `pdm add faster-whisper`
  * `pdm add setuptools`,解决报错`ModuleNotFoundError: No module named 'pkg_resources'`


# install whisperx, (不用这个,用faster-whisper, 因为更快)
  * 首先查看cuda版本,打开NVIDIA控制面板,点击 帮助->系统信息->组件->在'3D设置'里的'产品名称'字段里找到cuda版本号
  * 举例,如果cuda版本号是11.5.121,那么打开 https://download.pytorch.org/whl/torch/ 找到cu115,找到对应系统版本和python版本的,复制链接
  * `pip3 uninstall torch torchvision torchaudio`
  * `pip3 cache purge`
  * `pip3 install https://download.pytorch.org/whl/cu115/torch-1.11.0%2Bcu115-cp310-cp310-win_amd64.whl`
  * `pip3 install https://download.pytorch.org/whl/cu115/torchaudio-0.11.0%2Bcu115-cp310-cp310-win_amd64.whl`
  * `pip3 install https://download.pytorch.org/whl/cu115/torchvision-0.12.0%2Bcu115-cp310-cp310-win_amd64.whl`
  * 判断whisper是否走gpu: `python -c 'import torch; print(\"CUDA enabled:\", torch.cuda.is_available());'`
  * `pip3 install transformers`
  * 安装 https://github.com/m-bain/whisperX

# todo
  * whisper-ctranslate2, 生成的词级时间戳是json文件,不是srt文件,重写一下,不考虑兼容whisperx了
  * autosub,可以考虑换成hugging-face-translate,opus-mt模型
