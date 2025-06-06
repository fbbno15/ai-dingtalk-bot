from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # headless=True 可关闭浏览器窗口
    page = browser.new_page()

    # 你要抓的日报详情页链接
    url = "https://www.aibase.com/zh/daily/18404"
    print(f"正在抓取：{url}")
    page.goto(url)

    # 等待页面加载
    page.wait_for_timeout(8000)  # 等 8 秒足够加载动态内容

    # 抓取标题、日期、正文段落
    title = page.locator(".prose h1").inner_text()
    date = page.locator(".prose time").inner_text()
    paragraphs = page.locator(".prose p").all_inner_texts()

    # 输出内容
    print(f"\n# {title}\n")
    print(f"🗓️ {date}\n")
    print("## 内容摘要\n")
    for para in paragraphs:
        text = para.strip()
        if text:
            print(f"- {text}\n")

    # 可选：保存为 Markdown 文件
    md_content = f"# {title}\n\n🗓️ {date}\n\n## 内容摘要\n\n"
    for para in paragraphs:
        text = para.strip()
        if text:
            md_content += f"- {text}\n\n"

    with open("aibase_18404.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print("✅ 已保存为 aibase_18404.md")
    browser.close()
