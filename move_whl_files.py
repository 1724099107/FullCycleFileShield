import os
import shutil

# 获取当前目录
current_dir = os.getcwd()
# 目标目录
target_dir = os.path.join(current_dir, "offline_deps")

# 确保目标目录存在
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# 移动所有.whl文件
for file in os.listdir(current_dir):
    if file.endswith(".whl"):
        src_path = os.path.join(current_dir, file)
        dst_path = os.path.join(target_dir, file)
        print(f"移动 {file} 到 {target_dir}")
        shutil.move(src_path, dst_path)

print("所有.whl文件已移动完成!")