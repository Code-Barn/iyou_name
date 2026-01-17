import os

import pytest
from playwright.sync_api import sync_playwright


def test_pdf_generation():
    """Test PDF generation by submitting a POST request to /generator/generate/."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to the HUD page
        page.goto("http://localhost:8000/hud/display-tree/")

        # Wait for the page to load
        page.wait_for_selector(".alert-info")

        # Submit the hud-settings-form directly to /generator/generate/
        with page.expect_download() as download_info:
            page.evaluate("""() => {
                const form = document.getElementById('hud-settings-form');
                if (form) {
                    form.action = '/generator/generate/';
                    form.submit();
                }
            }""")

        # Submit a POST request to /generator/generate/
        with page.expect_download() as download_info:
            page.evaluate(f"""() => {{
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/generator/generate/';

                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = '{csrf_token}';
                form.appendChild(csrfInput);

                const individualInput = document.createElement('input');
                individualInput.type = 'hidden';
                individualInput.name = 'individual_id';
                individualInput.value = '{individual_id}';
                form.appendChild(individualInput);

                document.body.appendChild(form);
                form.submit();
            }}""")

            # Wait for the download to complete
            download = download_info.value
            download_path = download.path()
            assert download_path, "PDF download failed"

            # Verify the file is a PDF
            assert download_path.endswith(".pdf"), "Downloaded file is not a PDF"
            assert os.path.getsize(download_path) > 0, "Downloaded PDF is empty"

            print(f"SUCCESS: PDF generated and saved to {download_path}")

        browser.close()
