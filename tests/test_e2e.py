import pytest
from playwright.sync_api import sync_playwright
import threading
import time
from app import create_app

# -------------------------------------------------------------------
# Start Flask Server in Background
# -------------------------------------------------------------------
def run_server():
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

@pytest.fixture(scope="session", autouse=True)
def start_flask_app():
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(1)   # Allow server to start


# -------------------------------------------------------------------
#   E2E TEST – COMPLETE REAL USER FLOW (Assignment Requirement)
# -------------------------------------------------------------------
def test_full_user_flow_add_and_borrow():
    """
    REQUIRED BY ASSIGNMENT:
        1. Launch browser
        2. Add a new book
        3. Verify it appears in catalog
        4. Borrow it
        5. Verify confirmation message
    """

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()

        # ----------------------------------------------------------
        # 1. Open the catalog page
        # ----------------------------------------------------------
        page.goto("http://127.0.0.1:5000/catalog")
        assert "Catalog" in page.inner_text("body")

        # ----------------------------------------------------------
        # 2. Navigate to Add Book page
        # routes/catalog_routes.py -> /add_book
        # ----------------------------------------------------------
        page.click("text=Add Book")
        assert page.url.endswith("/add_book")

        # ----------------------------------------------------------
        # 3. Fill Add Book form (REAL FORM FIELDS FROM HTML)
        # ----------------------------------------------------------
        import random

        test_title = "Playwright Testing Book"
        test_author = "Test Author"

        # Generating a unique 13-digit ISBN so it never clashes with DB (i added this because i didnt want any issues with clashing isbn's existent within library.db)
        test_isbn = "9" + "".join(str(random.randint(0, 9)) for _ in range(12))

        test_copies = "5"

        page.fill("#title", test_title)
        page.fill("#author", test_author)
        page.fill("#isbn", test_isbn)
        page.fill("#total_copies", test_copies)

        page.click("text=Add Book to Catalog")

        # Wait for flash message
        page.wait_for_timeout(800)
        body_text = page.inner_text("body").lower()

        assert "success" in body_text or "successfully" in body_text


        # ----------------------------------------------------------
        # 4. Go back to catalog and confirm book is truly visible
        # ----------------------------------------------------------
        page.goto("http://127.0.0.1:5000/catalog")
        page.wait_for_timeout(500)

        catalog_text = page.inner_text("body").lower()
        assert test_title.lower() in catalog_text

        # ----------------------------------------------------------
        # 5. Borrow the correct book row ONLY
        # Using the Playwright row selector: tr:has-text('<title>')
        # Filling the patron ID inside that SAME row.
        # ----------------------------------------------------------
        row_selector = f"tr:has-text('{test_title}')"

        page.fill(f"{row_selector} input[name='patron_id']", "123456")
        page.click(f"{row_selector} button.btn-success")

        # ----------------------------------------------------------
        # 6. Verify borrowing success message (borrowing_routes.py flashes messages)
        # ----------------------------------------------------------
        page.wait_for_timeout(1200)
        final_text = page.inner_text("body").lower()

        assert "successfully borrowed" in final_text

        browser.close()
