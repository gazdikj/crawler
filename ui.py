import streamlit as st
import requests
import time

API_URL = "http://localhost:5000"  # Adresa Flask API

st.title("Crawler Task Monitoring")

col1, col2 = st.columns(2)

with col1:
    web_url = st.selectbox("Vyberte web pro crawlování:", ["https://datoid.cz", "Možnost 2", "Možnost 3"])
    driver = st.selectbox("Vyberte prohližeč:", ["chrome", "firefox"])

with col2:
    what_to_crawl = st.text_input("Co crawlovat:")
    device = st.selectbox("Vyberte zařízení:", ["desktop", "mobile"])

# Tlačítko pro spuštění nové úlohy
if st.button("Spustit novou úlohu"):
    data = {
        "web": web_url,
        "filter": what_to_crawl,
        "driver": driver,
        "device": device
    }    
    response = requests.post(f"{API_URL}/start-task", json=data)
    if response.status_code == 202:
        st.success("Úloha byla spuštěna!")
    else:
        st.error("Chyba při spuštění úlohy.")

st.subheader("Seznam běžících crawlerů")

# Automatická aktualizace seznamu úloh
placeholder = st.empty()

while True:
    response = requests.get(f"{API_URL}/tasks-status")
    if response.status_code == 200:
        tasks = response.json()
        with placeholder.container():
            st.table(tasks)  # Zobrazíme úlohy v tabulce
    time.sleep(5)  # Aktualizace každých 5 sekund
