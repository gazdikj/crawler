import requests
import glob
import sys
import argparse
import os
import ntpath
from time import sleep

import dbVTManager as db
from config import VT_API_KEY

url_files = "https://www.virustotal.com/api/v3/files"

headers = {
    "accept": "application/json",
    "x-apikey": VT_API_KEY # je třeba dodat vlastní API klíč
}

url_analyses_start = "https://www.virustotal.com/api/v3/analyses/"
url_analyses_end = "%3D%3D"

def testFile(file_name, byte_data):
    print('Path: ' + file_name)   

    file = {"file": (file_name, byte_data)}  #open(file_path, "rb")
    response = requests.post(url_files, files=file, headers=headers)
    data = response.json()
    test_id = data['data']['id']
    print('id testu: ' + test_id)

    # uložení informací o testu cracku do databáze
    db.insert_sample(filename=file_name, test_id=test_id)
    print("New sample added for testing.")

    return test_id


def analyseFile(test_id):
    #url pro získaní analýzy k danému cracku pokud je analýza dokončena
    url_analyses = url_analyses_start + test_id[:-2] + url_analyses_end        

    response = requests.get(url_analyses, headers=headers)
    data = response.json()

    # rozparsování potřebných dat
    sha256 = data['meta']['file_info']['sha256']
    status = data['data']['attributes']['status']
    harmless = data['data']['attributes']['stats']['harmless']
    malicious = data['data']['attributes']['stats']['malicious']
    undetected = data['data']['attributes']['stats']['undetected']

    print('\nsha256: ' + sha256)
    print('status: ' + status)
    print('harmless: ' + str(harmless))
    print('malicious: ' + str(malicious))
    print('undetected: ' + str(undetected))    

    # případě, že je analýza kompletní je uložena do databáze podle hashe příslušného cracku, pokud již analýza s tímto hashem nepřidáva se znovu
    if str(status) == 'completed':
        analysis_id = db.insert_analysis(status, undetected, malicious, harmless, sha256)

        # uložení antivirových programu a případných detekcí k patřičné analýze
        print('Added new analysis.\n')
        for item in data['data']['attributes']['results']:
            engine_name = data['data']['attributes']['results'][f'{item}']['engine_name']
            engine_category = data['data']['attributes']['results'][f'{item}']['category']
            engine_result = data['data']['attributes']['results'][f'{item}']['result']
            print('Added new engine ' + str(engine_name) + ' with analysisId ' + str(analysis_id) + ' and result ' + str(engine_result))
            db.insert_antivirus(engine_name, engine_category, engine_result, analysis_id)                   
        
        # nastavení atributu analysed = TRUE značí, že crack byl otestován
        db.update_sample(test_id, analysis_id)

        return data
        
    else:
        print('The analysis is not yet complete.\n')
        return None


if __name__ == "__main__":
    # pokud není cesta správná 
    path = "D:\\vyska\\bakalarka\\BP\\python\\soubory\\girl.jpg"

    if not os.path.exists(path):
        print('Wrong path')
        sys.exit(1)

    with open(path, "rb") as f:
        byte_data = f.read()
        test_id = testFile(path, byte_data)

    # pokud nejsou všechny cracky otestvány na první běh, čeka se minutu pro další dokud analýza nedoběhne
    while not analyseFile(test_id):
        print('Waiting 60 seconds\n')
        sleep(60)    
    
