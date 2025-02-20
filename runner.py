from flask import Flask, jsonify, request
from celery.result import AsyncResult
from worker import celery_app, long_running_task

app = Flask(__name__)

# Seznam běžících úloh
active_tasks = {}

@app.route("/start-task", methods=["POST"])
def start_task():
    """Spustí novou úlohu a uloží její ID."""
    task = long_running_task.apply_async()
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
    app.run(debug=True)
