import glob
import os

# 匹配 aibase_*_cleaned.md 文件
aibase_files = glob.glob("aibase_*_cleaned.md")
if aibase_files:
    aibase_file = max(aibase_files, key=os.path.getmtime)
else:
    aibase_file = None

# 读取各内容源
def read_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取 {filename} 失败，原因：{e}")
        return ""

# 1. AI 产品新发现
bestreader_content = read_file('bestreader_ai_products.md')

# 2. AI 行业新动态
xiaohu_content = read_file('xiaohu_cleaned_posts.md')
aibase_content = read_file(aibase_file) if aibase_file else ""

industry_content = "\n\n---\n\n".join([c for c in [aibase_content, xiaohu_content] if c.strip()])

# 合并为总md
final_md = (
    "# AI 产品新发现\n\n"
    f"{bestreader_content}\n\n"
    "# AI 行业新动态\n\n"
    f"{industry_content}\n"
)

with open('all_sources_raw.md', 'w', encoding='utf-8') as f:
    f.write(final_md)

print("已合并为 all_sources_raw.md")
