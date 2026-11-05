"""
tracking_page.py - Page Object Model (POM) for Courier Tracking Page.
Identifier: TC-01 / L4.3
Student: MASTAN SAB (Roll No: 60, Class 5B, Case 60)
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TrackingPage:
    """
    Page Object Model encapsulating the UI elements, locators,
    and business actions for the Courier Tracking application.
    """

    # Locators (Centralized Maintenance)
    SEARCH_INPUT = (By.ID, "search-input")
    SEARCH_BUTTON = (By.ID, "btn-search")
    SAMPLE_BUTTON = (By.XPATH, "//button[contains(text(), 'Try Sample ID')]")
    TRACKING_ID_DISPLAY = (By.ID, "display-tracking-id")
    RECIPIENT_DISPLAY = (By.ID, "display-recipient")
    STATUS_BADGE = (By.ID, "display-status-badge")
    LOCATION_DISPLAY = (By.ID, "display-location")
    UPDATE_STATUS_SELECT = (By.ID, "update-status-select")
    UPDATE_LOCATION_INPUT = (By.ID, "update-location-input")
    UPDATE_NOTES_INPUT = (By.ID, "update-notes-input")
    UPDATE_BUTTON = (By.ID, "btn-update-status")
    ALERT_BANNER = (By.ID, "alert-banner")
    TAB_REGISTER = (By.ID, "tab-btn-register")
    TAB_MONITORING = (By.ID, "tab-btn-monitoring")

    def __init__(self, driver, base_url: str = "http://localhost:5000"):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def load(self):
        """Navigates to the tracking homepage."""
        self.driver.get(self.base_url)
        self.wait.until(EC.presence_of_element_located(self.SEARCH_INPUT))
        return self

    def search_parcel(self, tracking_id: str):
        """Searches for a parcel by tracking ID."""
        inp = self.driver.find_element(*self.SEARCH_INPUT)
        inp.clear()
        inp.send_keys(tracking_id)
        self.driver.find_element(*self.SEARCH_BUTTON).click()
        return self

    def get_displayed_tracking_id(self) -> str:
        elem = self.wait.until(EC.visibility_of_element_located(self.TRACKING_ID_DISPLAY))
        return elem.text.strip()

    def get_displayed_recipient(self) -> str:
        elem = self.wait.until(EC.visibility_of_element_located(self.RECIPIENT_DISPLAY))
        return elem.text.strip()

    def get_displayed_status(self) -> str:
        elem = self.wait.until(EC.visibility_of_element_located(self.STATUS_BADGE))
        return elem.text.strip()

    def update_status(self, target_status: str, location: str = "", notes: str = ""):
        """Executes status workflow transition via UI."""
        sel = self.driver.find_element(*self.UPDATE_STATUS_SELECT)
        for opt in sel.find_elements(By.TAG_NAME, "option"):
            if opt.text.strip() == target_status:
                opt.click()
                break

        if location:
            loc_input = self.driver.find_element(*self.UPDATE_LOCATION_INPUT)
            loc_input.clear()
            loc_input.send_keys(location)

        if notes:
            notes_input = self.driver.find_element(*self.UPDATE_NOTES_INPUT)
            notes_input.clear()
            notes_input.send_keys(notes)

        self.driver.find_element(*self.UPDATE_BUTTON).click()
        return self

    def get_alert_message(self) -> str:
        elem = self.wait.until(EC.visibility_of_element_located(self.ALERT_BANNER))
        return elem.text.strip()
