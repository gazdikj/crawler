from celery import Celery

from crawlerType import get_crawler

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
    crawler_class = get_crawler(url)
    if not crawler_class:
        raise ValueError(f"Crawler třída nebyla nalezena.")    

    # Vytvoříme instanci crawleru
    crawler = crawler_class(url, what_to_crawl, browser, device)  

    # Spustíme crawling
    crawler.crawl(self)  

    return f"Crawling of {url} completed"