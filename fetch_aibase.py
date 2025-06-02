import requests
from bs4 import BeautifulSoup

def fetch_latest_aibase_fulltext():
    # Step 1: 打开目录页
    index_url = "https://www.aibase.com/zh/daily/"
    index_res = requests.get(index_url)
    index_soup = BeautifulSoup(index_res.text, "html.parser")

    # Step 2: 找第一个含 /zh/daily/ 的有效链接（最新日报入口）
    first_link_tag = next((a for a in index_soup.find_all('a', href=True) if '/zh/daily/' in a['href']), None)
    if not first_link_tag:
        return "❌ 未找到日报入口链接"

    relative_url = first_link_tag['href']
    full_url = "https://www.aibase.com" + relative_url

    # Step 3: 打开日报详情页
    detail_res = requests.get(full_url)
    detail_soup = BeautifulSoup(detail_res.text, "html.parser")

    # Step 4: 提取正文内容
    content_div = detail_soup.select_one("div.break-all")
    if not content_div:
        return "❌ 未找到日报正文内容"

    text = content_div.get_text(separator="\n", strip=True)

    # Step 5: 返回格式化内容
    return f"""## 🤖 AI日报自动推送（关键词触发）

{text}

👉 [查看原文]({full_url})"""
