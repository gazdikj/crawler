from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

from downloader import Downloader
from dbManager import DBManager

class BaseCrawler(ABC):
    def __init__(self, url, what_to_crawl="", browser="chrome", device="desktop"):
        self.url = url
        self.keyword = what_to_crawl
        self.download_folder = self.get_download_folder(what_to_crawl)
        self.downloader = Downloader(self.download_folder)             
        self.driver = self.init_browser(browser, device)
        self.db = DBManager(url, what_to_crawl, browser, device) 

    def get_download_folder(self, keyword): 
        download_folder = f"downloads\\{self.__class__.__name__}\\{keyword}"
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        return download_folder  


    def init_browser(self, browser, device):
        """Inicializace Selenium WebDriveru s emulací zařízení."""
        options = Options()

        options.add_argument(f"--proxy-server={self.downloader.proxy}")

        # Nastavení složky pro stahování specifické pro crawler
        prefs = {
            "download.default_directory": os.path.abspath(self.download_folder),  # Cesta ke složce pro stahování
            "download.prompt_for_download": False,  # Neptejte se kam uložit
            "download.directory_upgrade": True,  # Automatická změna složky
            "safebrowsing.enabled": False,  # Vypne bezpečnostní kontroly (potřebné)
            "safebrowsing.disable_download_protection": True,  # Povolit nebezpečné soubory
            "safebrowsing.for_trusted_sources_enabled": False  # Zabrání Chrome ve skenování souborů
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
    def crawl(self, task):
        """Každý crawler musí implementovat vlastní metodu crawl."""
        pass

    def close(self, task):
        """Uzavření Selenium driveru."""
        self.driver.quit()
