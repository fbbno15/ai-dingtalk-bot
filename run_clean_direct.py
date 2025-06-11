from playwright.sync_api import sync_playwright
import requests
import os,json
from bs4 import BeautifulSoup

def get_today_daily_url(list_url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page.goto(list_url)
        page.wait_for_timeout(8000)
        daily_link = page.locator('a:has-text("查看日报")').first.get_attribute("href")
        browser.close()
    if daily_link:
        if daily_link.startswith("/"):
            return "https://www.aibase.com" + daily_link
        else:
            return daily_link
    else:
        raise Exception("未找到今日日报链接")

def fetch_aibase_article_markdown(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page.goto(url)
        page.wait_for_timeout(8000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    # 提取标题和日期
    title = soup.find("h1")
    date = soup.find("time")
    title_text = title.get_text(strip=True) if title else "AI日报"
    date_text = date.get_text(strip=True) if date else ""

    # 提取所有日报条目
    items = []
    for strong in soup.find_all("strong"):
        strong_text = strong.get_text(strip=True)
        # 只抓取以数字加顿号开头的标题（如1、2、3...）
        if strong_text and strong_text[0].isdigit() and '、' in strong_text:
            item_title = strong_text
            # 找到下一个 blockquote 作为提要
            blockquote = strong.find_next("blockquote")
            if blockquote:
                summary_lines = [line.strip() for line in blockquote.stripped_strings if line.strip()]
                items.append((item_title, summary_lines))

    # 拼 Markdown
    md_content = f"# {title_text}\n\n🗓️ {date_text}\n\n## 内容摘要\n\n"
    for idx, (item_title, summary_lines) in enumerate(items, 1):
        md_content += f"## {item_title}\n"
        for line in summary_lines:
            md_content += f"· {line}\n"
        md_content += "\n"
    return md_content

def clean_with_gpt_azure(raw_markdown: str) -> str:
    url = 'https://api.openai.com/v1/chat/completions'
    api_key = os.getenv("OPENAI-KEY")
    print('api_key'+api_key+'====')
    Authorization = 'Bearer {0}'.format(api_key)
    headers = {'content-type': 'application/json','Authorization': Authorization}
    payload = {
        "messages": [
            {
                "role": "user",
                "content": f"""以下是从 AIbase 抓取的原始日报内容（Markdown），请你按照以下清洗规则严格执行：\n\n
✅ 清洗规则汇总（严格执行）
1. 只保留两类内容：
• 现有模型或工具的「迭代升级」
• 全新可用/可测试的工具「正式发布」
2. 删除所有预期/即将上线内容（如"计划推出""预计上线"等）
3. 保留所有带链接的内容，即使内容中使用了"预计"等词，也不剔除
4. 删除所有"政策类"内容
5. 不保留无链接、且为预测、概念阶段的内容（记住，一定删除无链接内容！！）\n\n
✅ 内容结构筛选
每条内容只保留：
• 一级标题（即内容标题）
• 标题下方的【AiBase提要】中的每一条（无正文段落、无图片、无emoji）
• 提要每条前加「·」\n\n
✅ 以Markdown的形式输出给我，Markdown格式规范如下：
# YYYY-MM-DD AI资讯日报\n\n今天共 N 条资讯\n\n### 💡AI工具新动态\n\n## 标题\n\n· 提要内容1  \n· 提要内容2  \n· 提要内容3  \n[详情链接](https://xxx)  \n#话题标签1 #话题标签2（作为正文段落）\n\n👉🏻AI 世界瞬息万变，在评论区留下观点，或投稿你关注的前沿链接，让更多人看到你的视角！\n\n原始内容如下：\n{raw_markdown}
"""
            }
        ]
    }

    postdata = {'model': 'gpt-4o', 'messages': payload['messages'], 'temperature': 0, 'max_tokens': 3000, 'top_p': 1,
			'frequency_penalty': 0.5, 'presence_penalty': 0.5}
    data = json.dumps(postdata)
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

if __name__ == "__main__":
    list_url = "https://www.aibase.com/zh/daily"
    today_url = get_today_daily_url(list_url)
    print(f"今日日报链接：{today_url}")
    raw_md = fetch_aibase_article_markdown(today_url)
    print("✅ 已抓取原始日报内容\n")

    cleaned_md = clean_with_gpt_azure(raw_md)
    print("\n✅ ChatGPT 清洗输出如下：\n")
    print(cleaned_md)

    # 以日报ID命名保存
    daily_id = today_url.rstrip('/').split('/')[-1]
    filename = f"aibase_{daily_id}_cleaned.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned_md)
    print(f"✅ 已保存为 {filename}")
