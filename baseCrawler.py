from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

class BaseCrawler(ABC):
    def __init__(self, browser="chrome", device="desktop"):
        self.driver = self.init_browser(browser, device)

    def init_browser(self, browser, device):
        """Inicializace Selenium WebDriveru s emulací zařízení."""
        options = Options()

        download_folder = "downloads" #"downloads\\" + self.__class__.__name__
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        download_folder = os.path.abspath(download_folder)

        # Nastavení složky pro stahování specifické pro crawler
        prefs = {
            "download.default_directory": download_folder,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)            
        
        # Nastavení User-Agent pro různé prohlížeče a zařízení
        user_agents = {
            "chrome_desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "firefox_desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",
            "chrome_mobile": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36",
            "firefox_mobile": "Mozilla/5.0 (Android 10; Mobile; rv:107.0) Gecko/107.0 Firefox/107.0"
        }

        profile = f"{browser}_{device}"
        options.add_argument(f"user-agent={user_agents.get(profile, user_agents['chrome_desktop'])}")

        # Spustíme prohlížeč v headless režimu (může se vypnout pro debugging)
        options.headless = False

        service = Service("drivers\\chromedriver-win64\\chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    @abstractmethod
    def crawl(self, url, task, what_to_crawl=""):
        """Každý crawler musí implementovat vlastní metodu crawl."""
        pass

    def close(self, task):
        """Uzavření Selenium driveru."""
        self.driver.quit()
