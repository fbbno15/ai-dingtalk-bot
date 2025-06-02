import requests
from bs4 import BeautifulSoup

def fetch_latest_aibase_fulltext():
    # Step 1: 打开目录页
    index_url = "https://www.aibase.com/zh/daily/"
    index_res = requests.get(index_url)
    index_soup = BeautifulSoup(index_res.text, "html.parser")

    # Step 2: 找到最新日报的链接（第一个链接）
    first_link_tag = index_soup.select_one('a.line-clamp-2')
    if not first_link_tag:
        return "❌ 未找到日报入口链接"

    relative_url = first_link_tag['href']
    full_url = "https://www.aibase.com" + relative_url

    # Step 3: 进入日报详情页
    detail_res = requests.get(full_url)
    detail_soup = BeautifulSoup(detail_res.text, "html.parser")

    # Step 4: 提取正文内容
    content_div = detail_soup.select_one("div.break-all")
    if not content_div:
        return "❌ 未找到日报正文"

    text = content_div.get_text(separator="\n", strip=True)
    return text
