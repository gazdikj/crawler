from datoidCrawler import DatoidCrawler

CRAWLER_MAP = {
    "https://datoid.cz": DatoidCrawler
}

def get_crawler(url: str):
    for domain, crawler_class in CRAWLER_MAP.items():
        if domain in url:
            return crawler_class  # Vrátí instanci odpovídající třídy
        
if __name__ == "__main__":
    print(get_crawler("https://datoid.cz"))