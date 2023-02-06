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
# install whisperx
  * 首先查看cuda版本,打开NVIDIA控制面板,点击 帮助->系统信息->组件->在'3D设置'里的'产品名称'字段里找到cuda版本号
  * 举例,如果cuda版本号是11.5.121,那么打开 https://download.pytorch.org/whl/torch/ 找到cu115,找到对应系统版本和python版本的,复制链接
  * `pip3 uninstall torch torchvision torchaudio`
  * `pip cache purge`
  * `pip3 install https://download.pytorch.org/whl/cu115/torch-1.11.0%2Bcu115-cp310-cp310-win_amd64.whl`
  * `pip3 install https://download.pytorch.org/whl/cu115/torchaudio-0.11.0%2Bcu115-cp310-cp310-win_amd64.whl`
  * `pip3 install https://download.pytorch.org/whl/cu115/torchvision-0.12.0%2Bcu115-cp310-cp310-win_amd64.whl`
  * 判断whisper是否走gpu: `python -c 'import torch; print(\"CUDA enabled:\", torch.cuda.is_available());'`
