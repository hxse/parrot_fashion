import pysrt
from run_whisper import convert_time

# wordSrtPath = "D:/my_repo/parrot_fashion/download/影视/政治/20240822 iGL8rdiriMs/wc2/20240822 我听过的最挺台的演说：西方的榜样，中国的灯塔，世界的领袖！美国亏欠台湾太多，要对中共展开闪电战！中共已疯，妮基黑利或将荣登台独分子光荣榜 iGL8rdiriMs.word.en.srt"
# subs = pysrt.open(wordSrtPath)
# print(len(subs))
t = convert_time(27.0)
t2 = convert_time(26.8)
print(t)
print(t2)
