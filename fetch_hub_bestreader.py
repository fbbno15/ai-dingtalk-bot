import requests
import datetime

def get_last_week_range(date=None):
    if date is None:
        date = datetime.date.today()
    # 本周一
    this_monday = date - datetime.timedelta(days=date.weekday())
    # 上周一
    last_monday = this_monday - datetime.timedelta(days=7)
    last_sunday = last_monday + datetime.timedelta(days=6)
    return last_monday, last_sunday

# 获取上周一和上周日
monday, sunday = get_last_week_range()
url = f"https://hub.bestreader.ai/data/{monday.year}_{monday.strftime('%m-%d')}_{sunday.strftime('%m-%d')}.json"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'Referer': f'https://hub.bestreader.ai/zh/{monday.strftime("%Y-%m-%d")}%20-%20{sunday.strftime("%Y-%m-%d")}',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

resp = requests.get(url, headers=headers)
print(f"抓取URL: {url}")
data = resp.json()

# 按 upvote 排序，取前20条
def upvote_int(item):
    try:
        return int(item.get("upvote", "0"))
    except:
        return 0

top_items = sorted(data, key=upvote_int, reverse=True)[:20]

md_lines = []

for item in top_items:
    name = item.get("name", "")
    website = item.get("website", "")
    image_url = item.get("styles_item_Dk_img", "")
    tag1 = item.get("tag1", "")
    tag2 = item.get("tag2", "")
    zh_intro = item.get("中文简介", "")
    zh_usage = item.get("用途说明", "")

    desc = f"{zh_intro}{zh_usage}"

    md_lines.append(f"## {name}\n")
    md_lines.append(f"{desc}\n")
    if image_url:
        md_lines.append(f"![{name}]({image_url})\n")
    tags = " ".join([f"#{tag1}", f"#{tag2}"]).strip()
    if website:
        md_lines.append(f"[{name}]({website}) {tags}\n")
    else:
        md_lines.append(tags)
    md_lines.append("\n---\n")

with open("bestreader_ai_products.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("已保存为 bestreader_ai_products.md")

