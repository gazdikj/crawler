import os
import hashlib
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Nastavení složky ke sledování
WATCHED_FOLDER = "downloads\\datoidCrawler"  
HASH_FILE = "hashes.json"

# Funkce pro výpočet SHA-256 hash
def calculate_sha256(file_path):
    time.sleep(1)
    try:
        if not os.access(file_path, os.R_OK):  # Zkontroluje, zda je soubor čitelný
            print(f"⚠️ Nelze číst soubor: {file_path}")
            return None

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Chyba při hashování souboru {file_path}: {e}")
        return None

# Funkce pro načtení existujících hashů
def load_hashes():
    if os.path.exists(HASH_FILE):
        try:
            with open(HASH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

# Funkce pro uložení hashů
def save_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=4)

# Event handler pro sledování složky
class FileHandler(FileSystemEventHandler):
    def __init__(self, hashes):
        self.hashes = hashes

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            
            if file_name not in self.hashes:
                file_hash = calculate_sha256(file_path)
                if file_hash:
                    self.hashes[file_name] = file_hash
                    save_hashes(self.hashes)
                    print(f"Hash vytvořen: {file_name} -> {file_hash}")

# Načtení existujících hashů
hashes = load_hashes()

# Inicializace sledování
event_handler = FileHandler(hashes)
observer = Observer()
observer.schedule(event_handler, WATCHED_FOLDER, recursive=False)
observer.start()

print(f"Sledování složky: {WATCHED_FOLDER}")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
