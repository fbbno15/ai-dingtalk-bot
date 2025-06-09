from playwright.sync_api import sync_playwright

def get_aibase_raw_text(daily_id: int) -> str:
    url = f"https://www.aibase.com/zh/daily/{daily_id}"
    print(f"正在抓取：{url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 改为无头模式，方便部署
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(8000)  # 等待页面加载动态内容

        title = page.locator(".prose h1").inner_text()
        date = page.locator(".prose time").inner_text()
        paragraphs = page.locator(".prose p").all_inner_texts()
        browser.close()

    raw_text = f"{title}\n{date}\n\n" + "\n".join(paragraphs)
    return raw_text
