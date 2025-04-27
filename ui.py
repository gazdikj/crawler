import streamlit as st
import requests
import time
import pandas as pd
import os
import base64
import json

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


uploaded_file = st.file_uploader("Vyber soubor k analýze")

if uploaded_file:
    byte_data = uploaded_file.getvalue()
    encoded_data = base64.b64encode(byte_data).decode("utf-8")

    if st.button("Analyzovat vzorek"):
        data = {
            "file_name": uploaded_file.name,
            "byte_data": encoded_data  # <- string, safe for JSON
        }    
        response = requests.post(f"{API_URL}/start-analysis", json=data)
        if response.status_code == 202:
            st.success("Analýza byla spuštěna!")
        else:
            st.error("Chyba při analýze úlohy.")   


while True:
    analysis = requests.get(f"{API_URL}/get-analysis")
    if analysis.status_code == 200:

        # Předpokládáme, že data = analysis.json()
        data = analysis.json()

        # Vytažení potřebných údajů
        data = data.get("data")
        attributes = data.get("data", {}).get("attributes", {})
        stats = attributes.get("stats", {})
        results_raw = attributes.get("results", {})

        meta = data.get("meta", {}).get("file_info", {})

        # Připravíme seznam výsledků
        results = []
        for engine_name, result_info in results_raw.items():
            result_text = result_info.get("result")
            if result_text:
                results.append({
                    "engine": engine_name,
                    "result": result_text
                })
            #result_text = result_info.get("result", "Undetected")
            #results.append({
            #    "engine": engine_name,
            #    "result": result_text if result_text else "Undetected"
            #})          

        # Připravíme základní info
        #domain = meta.get("sha256", "N/A")  # Např. místo domény zobrazíme hash souboru
        md5 = meta.get("md5", "N/A")
        undetected = stats.get("undetected", "N/A")
        malicious = stats.get("malicious", "N/A")
        harmless = stats.get("harmless", "N/A")

        # Výpis na obrazovku
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Analysis detail")
                st.markdown(f"**File name:** {uploaded_file.name}")
                st.markdown(f"**MD5:** {md5}")
                st.markdown(f"**Undetected:** {undetected}")
                st.markdown(f"**Malicious:** {malicious}")
                st.markdown(f"**Harmless:** {harmless}")

            with col2:
                st.subheader("Engines & Threats")
                if results:
                    for result in results:
                        st.markdown(f"**{result['engine']}:** {result['result']}")
                else:
                    st.markdown("No threats were found")



    response = requests.get(f"{API_URL}/tasks-status")
    if response.status_code == 200:
        tasks = response.json()
        progress_data = [item["progress"] for item in tasks]
        df = pd.DataFrame(progress_data)
        with placeholder.container():
            st.dataframe(df, use_container_width=True)
            #st.subheader("Aktuálně běžící úlohy")
            #st.write(df)


        
    time.sleep(5)  # Aktualizace každých 5 sekund
