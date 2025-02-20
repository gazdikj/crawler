spusteni cele aplikace:
1) redis-server
2) celery -A worker worker -P threads --loglevel=info
3) python runner.py
4) streamlit run ui.py

spusteni crawleru 
1) python main.py