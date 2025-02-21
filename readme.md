spuštění celé aplikace:
1) redis-server
2) celery -A worker worker -P threads --loglevel=info
3) python runner.py
4) streamlit run ui.py

spuštění crawleru 
1) python main.py

uložení závislostí
1) pip freeze > requirements.txt

načtení závislostí
1) pip install -r requirements.txt