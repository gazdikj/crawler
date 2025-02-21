from celery import Celery
import time

from crawlerType import get_crawler
from datoidCrawler import DatoidCrawler

# Inicializace Celery s Redis brokerem
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Redis jako fronta zpráv
    backend="redis://localhost:6379/0",  # Redis jako úložiště výsledků
    celery_broker_connection_retry_on_startup=True
)

task_progress = {}  # Uchovávání stavů úloh

@celery_app.task(bind=True)
def long_running_task(self, url, what_to_crawl, browser, device):
    # Dynamicky najdeme třídu podle jejího názvu
    #crawler_class = globals().get(crawler_class_name)
    
    crawler_class = get_crawler("https://datoid.cz")

    if not crawler_class:
        raise ValueError(f"Crawler třída nebyla nalezena.")    

    # Vytvoříme instanci crawleru
    crawler = crawler_class(browser, device)  

    # Spustíme crawling
    crawler.crawl(url, self, what_to_crawl)  
    time.sleep(5)

    return f"Crawling of {url} completed"


    """
    for i in range(1, 4):
        self.update_state(state="PROGRESS", meta={"current": i, "total": 3})  # Aktualizace stavu
        print(f"Průběh: {i}/3")
        time.sleep(3)  # Simulace práce

    return {"status": "Completed", "result": 100}
    """