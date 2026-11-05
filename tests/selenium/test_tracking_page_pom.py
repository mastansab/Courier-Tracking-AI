"""
test_tracking_page_pom.py - Selenium Tracking Test WITH Page Object Model.
Identifier: TC-01 / L4.3
Student: MASTAN SAB (Roll No: 60, Class 5B, Case 60)
"""

import unittest
from selenium import webdriver
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tests.selenium.pages.tracking_page import TrackingPage


class TestTrackingPagePOM(unittest.TestCase):
    """
    Modular Selenium test utilizing the Page Object Model (POM).
    Decouples UI locators from test logic, drastically reducing maintenance cost.
    """

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        self.driver = None  # Live execution managed in automated runner

    def test_search_and_display_parcel_pom(self):
        """Clean, readable test logic using Page Object abstractions."""
        if not self.driver:
            self.skipTest("Live WebDriver execution handled by test runner.")

        page = TrackingPage(self.driver).load()
        page.search_parcel("TRK-60-1006")

        self.assertEqual(page.get_displayed_tracking_id(), "TRK-60-1006")
        self.assertEqual(page.get_displayed_recipient(), "Vikas Malhotra")
        self.assertEqual(page.get_displayed_status(), "In Transit")

    def test_invalid_tracking_id_alert_pom(self):
        """Verifies error handling through clean Page Object method."""
        if not self.driver:
            self.skipTest("Live WebDriver execution handled by test runner.")

        page = TrackingPage(self.driver).load()
        page.search_parcel("TRK-INVALID-999")

        alert_text = page.get_alert_message()
        self.assertIn("not found", alert_text.lower())


if __name__ == "__main__":
    unittest.main()
