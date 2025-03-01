from datoidCrawler import DatoidCrawler

class CrawlerManager:
    def __init__(self):
        self.crawlers = []

    def add_crawler(self, crawler_class, url, browser="chrome", device="desktop"):
        """Přidá crawler do seznamu a spustí ho."""
        crawler = crawler_class(url, "katy perry roar", browser, device)
        self.crawlers.append(crawler)
        crawler.crawl("")

    def stop_all(self):
        """Zastaví všechny crawlery."""
        for crawler in self.crawlers:
            crawler.close()
