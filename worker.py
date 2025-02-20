from celery import Celery
import time

# Inicializace Celery s Redis brokerem
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Redis jako fronta zpráv
    backend="redis://localhost:6379/0",  # Redis jako úložiště výsledků
    celery_broker_connection_retry_on_startup=True
)

task_progress = {}  # Uchovávání stavů úloh

@celery_app.task(bind=True)
def long_running_task(self):
    for i in range(1, 4):
        self.update_state(state="PROGRESS", meta={"current": i, "total": 3})  # Aktualizace stavu
        print(f"Průběh: {i}/3")
        time.sleep(3)  # Simulace práce

    return {"status": "Completed", "result": 100}