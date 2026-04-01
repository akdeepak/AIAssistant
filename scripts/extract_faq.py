from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(
        "https://www.allianz.co.uk/insurance/car-insurance/faqs/account-faqs.html"
    )

    # expand all FAQs
    page.locator("button").click(timeout=5000)

    text = page.inner_text("body")
    print(text)

    browser.close()
