from playwright.sync_api import sync_playwright

def get_latest_aibase_daily_id() -> int:
    url = "https://www.aibase.com/zh/daily"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)

        link = page.query_selector(".article-item a")
        href = link.get_attribute("href") if link else None

        browser.close()

    if href and "/zh/daily/" in href:
        return int(href.strip("/").split("/")[-1])
    else:
        raise Exception("❌ 无法提取最新日报链接")
