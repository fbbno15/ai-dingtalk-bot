from playwright.sync_api import sync_playwright
import requests
import os

# 从 aibase 抓取单篇日报
def fetch_aibase_article(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # 等待页面主要结构加载
        page.wait_for_selector(".prose h1", timeout=15000)

        title = page.locator(".prose h1").inner_text()
        date = page.locator(".prose time").inner_text()
        paragraphs = page.locator(".prose p").all_inner_texts()

        browser.close()

    full_text = f"{title}\n{date}\n\n" + "\n".join(
        para.strip() for para in paragraphs if para.strip()
    )
    return full_text

# 调用 Azure OpenAI 清洗日报内容
def clean_with_gpt_azure(raw_text: str) -> str:
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
                "content": (
                    "以下是从 AIbase 抓取的原始日报内容，请你按照以下清洗规则严格执行：\n\n"
                    "✅ 清洗规则汇总（严格执行）\n"
                    "1. 只保留两类内容：现有模型或工具的「迭代升级」、全新可用/可测试的工具「正式发布」\n"
                    "2. 删除所有预期/即将上线内容（如“计划推出”“预计上线”等）\n"
                    "3. 保留所有带链接的内容，即使内容中使用了“预计”等词，也不剔除\n"
                    "4. 删除所有“政策类”内容\n"
                    "5. 删除所有无链接的预测、概念阶段内容\n\n"
                    "✅ 内容结构筛选\n"
                    "每条内容只保留：\n• 一级标题（即内容标题）\n• 标题下方的【AiBase提要】中的每一条（无正文段落、无图片、无emoji）\n• 提要每条前加「·」\n\n"
                    "✅ 输出格式（Markdown）：\n"
                    "# YYYY-MM-DD AI资讯日报\n\n"
                    "今天共 N 条资讯\n\n"
                    "### 💡AI工具新动态\n\n"
                    "## 标题\n· 提要1\n· 提要2\n[详情链接](https://xxx)\n#话题标签1 #话题标签2\n\n"
                    f"原始内容如下：\n{raw_text}"
                )
            }
        ]
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

# 主函数：抓取 + 清洗
if __name__ == "__main__":
    url = "https://www.aibase.com/zh/daily/18404"  # 可替换成动态 ID 链接

    raw = fetch_aibase_article(url)
    print("✅ 已抓取原始日报内容\n")

    result = clean_with_gpt_azure(raw)
    print("\n✅ ChatGPT 清洗输出如下：\n")
    print(result)
