from celery import Celery
from time import sleep

from crawlerType import get_crawler
from testFile import testFile, analyseFile

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

@celery_app.task(bind=True)
def analyse_sample(self, file_name, byte_data): 
    self.update_state(state="File uploaded for testing")  
    test_id = testFile(file_name, byte_data)

    self.update_state(state="Analysing file")
    data = None  
    while not data:
        data = analyseFile(test_id)
        print('Waiting 10 seconds\n')        
        sleep(10)        

    return {
        "status": "Analysis completed",
        "data": data
    }