from flask import Flask, jsonify, request
from celery.result import AsyncResult
from worker import celery_app, long_running_task, analyse_sample

import base64
import json

from datoidCrawler import DatoidCrawler

app = Flask(__name__)

# Seznam běžících úloh
active_tasks = {}

@app.route("/start-analysis", methods=["POST"])
def start_analysis():
    data = request.get_json()

    file_name = data.get("file_name")
    encoded_data = data.get("byte_data")
    try:
        byte_data = base64.b64decode(encoded_data)
        print(f"Přijal jsem soubor: {file_name}, velikost: {len(byte_data)} bajtů")
        
        args = [file_name, byte_data]
        task = analyse_sample.apply_async(args=args)
        active_tasks[task.id] = "PENDING"  # Uložíme do seznamu aktivních úloh
        return jsonify({"task_id": task.id}), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/start-task", methods=["POST"])
def start_task():
    """Spustí novou úlohu a uloží její ID."""

    # Ověříme, zda požadavek obsahuje JSON
    data = request.get_json()

    # Získání parametrů z JSON
    url = data.get("web")
    what_to_crawl = data.get("filter")
    driver = data.get("driver")
    device = data.get("device")
    print(url, what_to_crawl, driver, device)

    #args = ["https://datoid.cz", "katy perry roar", "chrome", "desktop"]
    args = [url, what_to_crawl, driver, device]
    task = long_running_task.apply_async(args=args)
    active_tasks[task.id] = "PENDING"  # Uložíme do seznamu aktivních úloh
    return jsonify({"task_id": task.id}), 202

@app.route("/tasks-status", methods=["GET"])
def get_all_tasks_status():
    """Vrací stav všech běžících úloh."""
    task_status_list = []

    for task_id in list(active_tasks.keys()):  # Iterujeme přes aktivní úlohy
        task_result = AsyncResult(task_id, app=celery_app)
        
        # Pokud je úloha dokončena, odstraníme ji ze seznamu
        if task_result.status in ["SUCCESS", "FAILURE", "REVOKED"]:
            active_tasks.pop(task_id, None)

        task_status_list.append({
            "task_id": task_id,
            "status": task_result.status,
            "progress": task_result.info if task_result.info else {}
        })          

    return jsonify(task_status_list)

if __name__ == "__main__":
    app.run(debug=False)
