from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

class PixelStreamingPage:
    def __init__(self, driver):
        self.driver = driver
        
    # Locators
    PLAY_BUTTON = (By.ID, "playButton")
    FULLSCREEN_BUTTON = (By.ID, "fullscreen-btn")
    SETTINGS_BUTTON = (By.ID, "settingsBtn")
    STATS_BUTTON = (By.ID, "statsBtn")
    PLAYER = (By.ID, "player")
    MESSAGE_OVERLAY = (By.ID, "messageOverlay")
    SETTINGS_PANEL = (By.ID, "settings-panel")
    STATS_PANEL = (By.ID, "stats-panel")

    def load_page(self, base_url):
        self.driver.get(base_url)
        self.wait_for_element(self.PLAY_BUTTON)

    def wait_for_element(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def click_play_button(self):
        self.wait_for_element(self.PLAY_BUTTON).click()

    def click_fullscreen_button(self):
        self.wait_for_element(self.FULLSCREEN_BUTTON).click()

    def click_settings_button(self):
        self.wait_for_element(self.SETTINGS_BUTTON).click()

    def click_stats_button(self):
        self.wait_for_element(self.STATS_BUTTON).click()

    def click_player(self):
        self.wait_for_element(self.PLAYER).click()

    def press_key(self, key):
        self.driver.find_element(By.TAG_NAME, "body").send_keys(key)

    def get_message_overlay_text(self):
        try:
            return self.wait_for_element(self.MESSAGE_OVERLAY).text
        except:
            return ""

    def is_settings_panel_visible(self):
        try:
            return self.driver.find_element(*self.SETTINGS_PANEL).is_displayed()
        except:
            return False

    def is_stats_panel_visible(self):
        try:
            return self.driver.find_element(*self.STATS_PANEL).is_displayed()
        except:
            return False 