from playwright.sync_api import sync_playwright
import requests
import os

# 从 aibase 抓取单篇日报
def fetch_aibase_article_markdown(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"正在抓取：{url}")
        page.goto(url)
        page.wait_for_timeout(8000)  # 等待动态内容加载

        title = page.locator(".prose h1").inner_text()
        date = page.locator(".prose time").inner_text()
        paragraphs = page.locator(".prose p").all_inner_texts()

        browser.close()

    md_content = f"# {title}\n\n🗓️ {date}\n\n## 内容摘要\n\n"
    for para in paragraphs:
        text = para.strip()
        if text:
            md_content += f"- {text}\n\n"
    return md_content

# 调用 Azure OpenAI 清洗日报内容
def clean_with_gpt_azure(raw_markdown: str) -> str:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_KEY")
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
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
    response = requests.post(endpoint, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

# 主函数：抓取 + 清洗
if __name__ == "__main__":
    url = "https://www.aibase.com/zh/daily/18404"  # 可替换成动态 ID 链接
    raw_md = fetch_aibase_article_markdown(url)
    print("✅ 已抓取原始日报内容\n")

    cleaned_md = clean_with_gpt_azure(raw_md)
    print("\n✅ ChatGPT 清洗输出如下：\n")
    print(cleaned_md)

    with open("aibase_18404_cleaned.md", "w", encoding="utf-8") as f:
        f.write(cleaned_md)
    print("✅ 已保存为 aibase_18404_cleaned.md")
