from crawlerManager import CrawlerManager
from datoidCrawler import DatoidCrawler

if __name__ == "__main__":
    manager = CrawlerManager()

    # Přidání crawlerů pro různé weby
    manager.add_crawler(DatoidCrawler, "https://datoid.cz", browser="chrome", device="desktop")
    
    # Může běžet více crawlerů současně
    # manager.add_crawler(datoidCrawler, "https://anotherwebsite.com", browser="firefox", device="mobile")
