import os
import hashlib
import json

# Nastavení složky ke sledování
WATCHED_FOLDER = "downloads\\datoidCrawler"  
HASH_FILE = "hashes.json"

# Funkce pro výpočet SHA-256 hash
def calculate_sha256(file_path) -> str:
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Chyba při hashování souboru {file_path}: {e}")
        return None

def save_hashes(file_name, hash_value): 
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    
    # Přidání nového záznamu
    data[file_name] = hash_value
    
    # Uložení aktualizovaných dat
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)        
