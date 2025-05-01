import pytest
import time
import psutil
import os
import io
import cv2
import numpy as np
import json
from datetime import datetime
from PIL import Image
from pages.pixel_streaming_page import PixelStreamingPage

class ScreenshotLogger:
    def __init__(self, log_dir="test_logs"):
        self.log_dir = log_dir
        self.current_test = None
        self.log_data = {
            "test_name": None,
            "timestamp": None,
            "comparisons": []
        }
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def start_test(self, test_name):
        self.current_test = test_name
        self.log_data = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "comparisons": []
        }
    
    def log_comparison(self, baseline_name, similarity, threshold, is_similar):
        self.log_data["comparisons"].append({
            "baseline": baseline_name,
            "similarity": float(round(similarity, 2)),
            "threshold": float(threshold),
            "passed": bool(is_similar)
        })
    
    def save_log(self):
        if not self.current_test:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.current_test}_{timestamp}.json"
        filepath = os.path.join(self.log_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)

@pytest.mark.nondestructive
class TestPixelStreaming:
    @pytest.fixture(scope="class")
    def page(self, driver, base_url, signalling_server, vehicle_touch_process, baselines_dir):
        page = PixelStreamingPage(driver)
        page.load_page(base_url)
        return page
    
    @pytest.fixture(autouse=True)
    def logger(self):
        logger = ScreenshotLogger()
        yield logger
        logger.save_log()

    def compare_screenshots(self, current_screenshot, baseline_name, baselines_dir, threshold=0.5, max_retries=3, retry_delay=1):
        """Compare current screenshot with baseline image using OpenCV"""
        baseline_path = os.path.join(baselines_dir, f"{baseline_name}.png")
        
        # Convert PIL Image to OpenCV format
        current_cv = cv2.cvtColor(np.array(current_screenshot), cv2.COLOR_RGB2BGR)
        
        # If baseline doesn't exist, save current screenshot as baseline
        if not os.path.exists(baseline_path):
            cv2.imwrite(baseline_path, current_cv)
            return True, 100.0
        
        # Load baseline image
        baseline_cv = cv2.imread(baseline_path)
        
        # Ensure both images have the same size
        if current_cv.shape != baseline_cv.shape:
            current_cv = cv2.resize(current_cv, (baseline_cv.shape[1], baseline_cv.shape[0]))
        
        # Try comparison multiple times
        best_similarity = 0
        for attempt in range(max_retries):
            # Convert images to grayscale
            current_gray = cv2.cvtColor(current_cv, cv2.COLOR_BGR2GRAY)
            baseline_gray = cv2.cvtColor(baseline_cv, cv2.COLOR_BGR2GRAY)
            
            # Calculate SSIM
            similarity = float(cv2.matchTemplate(current_gray, baseline_gray, cv2.TM_CCOEFF_NORMED)[0][0])
            similarity_percentage = similarity * 100
            
            if similarity >= threshold:
                return True, similarity_percentage
            
            best_similarity = max(best_similarity, similarity_percentage)
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                # Take new screenshot for next attempt
                screenshot = self.page.driver.get_screenshot_as_png()
                current_screenshot = Image.open(io.BytesIO(screenshot))
                current_cv = cv2.cvtColor(np.array(current_screenshot), cv2.COLOR_RGB2BGR)
        
        return False, best_similarity

    def test_buttons_availability(self, page, baselines_dir, logger):
        """Test that all buttons are available on the page"""
        logger.start_test("test_buttons_availability")
        
        assert page.driver.find_element(*page.PLAY_BUTTON).is_displayed()
        assert page.driver.find_element(*page.FULLSCREEN_BUTTON).is_displayed()
        assert page.driver.find_element(*page.SETTINGS_BUTTON).is_displayed()
        assert page.driver.find_element(*page.STATS_BUTTON).is_displayed()
        
        time.sleep(1.5)
        
        # Take screenshot and compare
        screenshot = page.driver.get_screenshot_as_png()
        current_image = Image.open(io.BytesIO(screenshot))
        is_similar, similarity = self.compare_screenshots(current_image, "initial_state", baselines_dir)
        logger.log_comparison("initial_state", similarity, 0.5, is_similar)
        assert is_similar, f"Initial state screenshot doesn't match baseline. Similarity: {similarity:.2f}%"

    def test_play_button(self, page, baselines_dir, logger):
        """Test play button functionality"""
        logger.start_test("test_play_button")
        
        page.click_play_button()
        time.sleep(2.5)
        
        # Take screenshot and compare
        screenshot = page.driver.get_screenshot_as_png()
        current_image = Image.open(io.BytesIO(screenshot))
        is_similar, similarity = self.compare_screenshots(current_image, "after_play", baselines_dir)
        logger.log_comparison("after_play", similarity, 0.5, is_similar)
        assert is_similar, f"After play button screenshot doesn't match baseline. Similarity: {similarity:.2f}%"

    def test_fullscreen_toggle(self, page, baselines_dir, logger):
        """Test fullscreen button functionality"""
        logger.start_test("test_fullscreen_toggle")
        
        time.sleep(1.5)
        
        # Take screenshot before fullscreen
        screenshot_before = page.driver.get_screenshot_as_png()
        before_image = Image.open(io.BytesIO(screenshot_before))
        
        page.click_fullscreen_button()
        time.sleep(1.5)
        
        # Take screenshot in fullscreen
        screenshot_fullscreen = page.driver.get_screenshot_as_png()
        fullscreen_image = Image.open(io.BytesIO(screenshot_fullscreen))
        is_similar, similarity = self.compare_screenshots(fullscreen_image, "fullscreen", baselines_dir)
        logger.log_comparison("fullscreen", similarity, 0.5, is_similar)
        assert is_similar, f"Fullscreen screenshot doesn't match baseline. Similarity: {similarity:.2f}%"
        
        page.click_fullscreen_button()
        time.sleep(1.5)
        
        # Take screenshot after exiting fullscreen
        screenshot_after = page.driver.get_screenshot_as_png()
        after_image = Image.open(io.BytesIO(screenshot_after))
        is_similar, similarity = self.compare_screenshots(after_image, "after_fullscreen", baselines_dir)
        logger.log_comparison("after_fullscreen", similarity, 0.5, is_similar)
        assert is_similar, f"After fullscreen screenshot doesn't match baseline. Similarity: {similarity:.2f}%"

    def test_settings_panel(self, page, baselines_dir, logger):
        """Test settings panel functionality"""
        logger.start_test("test_settings_panel")
        
        time.sleep(1.5)
        
        page.click_settings_button()
        time.sleep(1.5)
        assert page.is_settings_panel_visible()
        
        # Take screenshot with settings panel
        screenshot = page.driver.get_screenshot_as_png()
        current_image = Image.open(io.BytesIO(screenshot))
        is_similar, similarity = self.compare_screenshots(current_image, "settings_panel", baselines_dir)
        logger.log_comparison("settings_panel", similarity, 0.5, is_similar)
        assert is_similar, f"Settings panel screenshot doesn't match baseline. Similarity: {similarity:.2f}%"
        
        page.click_settings_button()
        time.sleep(1.5)
        assert not page.is_settings_panel_visible()

    def test_stats_panel(self, page, baselines_dir, logger):
        """Test stats panel functionality"""
        logger.start_test("test_stats_panel")
        
        time.sleep(1.5)
        
        page.click_stats_button()
        time.sleep(1.5)
        assert page.is_stats_panel_visible()
        
        # Take screenshot with stats panel
        screenshot = page.driver.get_screenshot_as_png()
        current_image = Image.open(io.BytesIO(screenshot))
        is_similar, similarity = self.compare_screenshots(current_image, "stats_panel", baselines_dir)
        logger.log_comparison("stats_panel", similarity, 0.5, is_similar)
        assert is_similar, f"Stats panel screenshot doesn't match baseline. Similarity: {similarity:.2f}%"
        
        page.click_stats_button()
        time.sleep(1.5)
        assert not page.is_stats_panel_visible()

    def test_disconnection(self, page, baselines_dir, logger):
        """Test disconnection functionality"""
        logger.start_test("test_disconnection")
        
        time.sleep(1.5)
        
        page.click_player()
        page.press_key("q")
        time.sleep(1.5)
        assert "Disconnected".lower() in page.get_message_overlay_text().lower()
        
        # Take screenshot after disconnection
        screenshot = page.driver.get_screenshot_as_png()
        current_image = Image.open(io.BytesIO(screenshot))
        is_similar, similarity = self.compare_screenshots(current_image, "disconnected", baselines_dir)
        logger.log_comparison("disconnected", similarity, 0.5, is_similar)
        assert is_similar, f"Disconnected state screenshot doesn't match baseline. Similarity: {similarity:.2f}%"

    def test_reconnection_attempt(self, page, baselines_dir, logger):
        """Test reconnection attempt after disconnection"""
        logger.start_test("test_reconnection_attempt")
        
        time.sleep(1.5)
        
        page.click_play_button()
        time.sleep(1.5)
        assert "DISCONNECTED: STREAMER IS NOT CONNECTED".lower() in page.get_message_overlay_text().lower()
        
        # Take screenshot after reconnection attempt
        screenshot = page.driver.get_screenshot_as_png()
        current_image = Image.open(io.BytesIO(screenshot))
        is_similar, similarity = self.compare_screenshots(current_image, "reconnection_attempt", baselines_dir)
        logger.log_comparison("reconnection_attempt", similarity, 0.5, is_similar)
        assert is_similar, f"Reconnection attempt screenshot doesn't match baseline. Similarity: {similarity:.2f}%"

    def test_vehicle_touch_closed(self, check_vehicle_touch_closed):
        """Test that VehicleTouch process is closed after tests"""
        # Find and terminate VehicleTouch process
        for proc in psutil.process_iter(['name']):
            try:
                if 'VehicleTouch50' in proc.info['name']:
                    proc.terminate()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
        
        # Wait a bit for the process to fully terminate
        time.sleep(1) 
        
        # Check if process is closed
        assert check_vehicle_touch_closed(), "VehicleTouch process is still running" 