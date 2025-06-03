from playwright.sync_api import sync_playwright

def fetch_dynamic_aibase():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 打开目录页并等待加载
        page.goto("https://www.aibase.com/zh/daily/")
        page.wait_for_timeout(6000)

        # 获取最新日报链接
        first_link = page.locator("a[href^='/zh/daily/']").first
        href = first_link.get_attribute("href")

        if not href:
            return "❌ 没有找到日报链接"

        full_url = "https://www.aibase.com" + href

        # 打开详情页
        page.goto(full_url)
        page.wait_for_timeout(5000)

        # 抓取正文文本
        content = page.locator("div.break-all").inner_text()

        return f"""## 🤖 AI日报自动推送（关键词触发）

{content}

👉 [查看原文]({full_url})"""
