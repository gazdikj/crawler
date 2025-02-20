import streamlit as st
import requests
import time

API_URL = "http://localhost:5000"  # Adresa Flask API

st.title("Celery Task Monitor")

# Tlačítko pro spuštění nové úlohy
if st.button("Spustit novou úlohu"):
    response = requests.post(f"{API_URL}/start-task")
    if response.status_code == 202:
        st.success("Úloha byla spuštěna!")
    else:
        st.error("Chyba při spuštění úlohy.")

st.subheader("Seznam běžících úloh")

# Automatická aktualizace seznamu úloh
placeholder = st.empty()

while True:
    response = requests.get(f"{API_URL}/tasks-status")
    if response.status_code == 200:
        tasks = response.json()
        with placeholder.container():
            st.table(tasks)  # Zobrazíme úlohy v tabulce
    time.sleep(5)  # Aktualizace každých 5 sekund
