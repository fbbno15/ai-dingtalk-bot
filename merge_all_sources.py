import glob
import os

# 匹配所有 aibase_*_cleaned.md 文件
aibase_files = glob.glob("aibase_*_cleaned.md")
if aibase_files:
    # 取最新的（按文件修改时间排序）
    aibase_file = max(aibase_files, key=os.path.getmtime)
else:
    aibase_file = None

sources = [
    'xiaohu_cleaned_posts.md',
    'bestreader_ai_products.md'
]
if aibase_file:
    sources.append(aibase_file)
else:
    print("未找到 aibase 的 md 文件，合并时将跳过。")

all_content = []
for src in sources:
    try:
        with open(src, 'r', encoding='utf-8') as f:
            all_content.append(f.read())
    except Exception as e:
        print(f"读取 {src} 失败，原因：{e}")

with open('all_sources_raw.md', 'w', encoding='utf-8') as f:
    f.write('\n\n---\n\n'.join(all_content))

print("已合并为 all_sources_raw.md")
