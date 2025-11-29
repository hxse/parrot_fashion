from pathlib import Path
import os

a = "D:/my_repo/parrot_fashion/download/MSA previously My Story Animated/MSA previously My Story Animated - Videos UCYzEMRKqrh01-tauv7MYyVQ/2023/20230104 Ur_fjJ42J_Y/wc2/20230104 I Told Everyone Mom went into a Coma for Attention Ur_fjJ42J_Y.rewrite.en.srt"
b = "D:/my_repo/parrot_fashion/download/MSA previously My Story Animated/MSA previously My Story Animated - Videos UCYzEMRKqrh01-tauv7MYyVQ/2023/20230104 Ur_fjJ42J_Y/wc2/20230104 I Told Everyone Mom went into a Coma for Attention Ur_fjJ42J_Y.rewrite.en.deeplx.zh.srt"

path_a = Path(a)
path_b = Path(b)

print(f"Path a exists: {path_a.exists()}")
print(f"Path a is_file: {path_a.is_file()}")
print(f"OS path exists a: {os.path.exists(a)}")
print(f"OS path isfile a: {os.path.isfile(a)}")
print()

print(f"Path b exists: {path_b.exists()}")
print(f"Path b is_file: {path_b.is_file()}")
print(f"OS path exists b: {os.path.exists(b)}")
print(f"OS path isfile b: {os.path.isfile(b)}")
print()

print(f"Path a name: {path_a.name}")
print(f"Path b name: {path_b.name}")
print()

# 尝试使用原始字符串
b_raw = r"D:/my_repo/parrot_fashion/download/MSA previously My Story Animated/MSA previously My Story Animated - Videos UCYzEMRKqrh01-tauv7MYyVQ/2023/20230104 Ur_fjJ42J_Y/wc2/20230104 I Told Everyone Mom went into a Coma for Attention Ur_fjJ42J_Y.rewrite.en.deeplx.zh.srt"
print(f"Raw string path exists: {Path(b_raw).exists()}")
print(f"Raw string path is_file: {Path(b_raw).is_file()}")

# 获取目录中的实际文件列表并比较
dir_path = Path(
    "D:/my_repo/parrot_fashion/download/MSA previously My Story Animated/MSA previously My Story Animated - Videos UCYzEMRKqrh01-tauv7MYyVQ/2023/20230104 Ur_fjJ42J_Y/wc2"
)
files = list(dir_path.glob("*.srt"))
print("\n目录中的 .srt 文件:")
for f in files:
    print(f"  {f.name}")

# 查找包含 deeplx 的文件
deeplx_files = [f for f in files if "deeplx" in f.name]
print(f"\n包含 deeplx 的文件:")
for f in deeplx_files:
    print(f"  完整路径: {f}")
    print(f"  是否存在: {f.exists()}")
    print(f"  是否为文件: {f.is_file()}")

# 尝试读取文件内容
try:
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
        print(f"  文件大小: {len(content)} 字符")
        print(f"  前50个字符: {content[:50]}")
except Exception as e:
    print(f"  读取文件时出错: {e}")

# 尝试使用 os.stat
import os

try:
    stat = os.stat(f)
    print(f"  文件大小: {stat.st_size} 字节")
except Exception as e:
    print(f"  获取文件状态时出错: {e}")

# 检查路径长度
path_str = str(f)
print(f"  路径长度: {len(path_str)} 字符")
print(f"  路径: {path_str}")

# 尝试使用长路径前缀
long_path = "\\\\?\\" + path_str
print(f"  长路径前缀存在: {Path(long_path).exists()}")
print(f"  长路径前缀是文件: {Path(long_path).is_file()}")
