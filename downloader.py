import os
import requests
import random
import mimetypes
import zipfile
import time

class Downloader:
    def __init__(self, folder):
        self.proxy = self.get_proxy()
        self.download_folder = folder

    def get_proxy(self):
        proxies = self.get_proxies()
        proxy = self.get_good_random_proxy(proxies)
        return proxy

    def get_proxies(self):
        """Získá seznam veřejných proxy serverů."""
        url = "https://www.free-proxy-list.net/"
        response = requests.get(url)

        # Extrahuje proxy servery ze stránky
        proxies = set()
        for line in response.text.split("\n"):
            if line.count(".") == 3 and ":" in line:
                proxies.add(line.strip())

        return proxies  


    def get_good_random_proxy(self, proxies):
        for _ in proxies.copy():
            proxy = random.choice(list(proxies))
            try:
                res = requests.get("http://ipinfo.io/json", proxies={"http": proxy, "https": proxy}, timeout=1)
            except:
                proxies.remove(proxy)
                continue
            if res.status_code == 200:
                proxies.remove(proxy)
                return proxy                       
  

    def get_file_name(self, response, url):
        """Automaticky zjistí název souboru z hlaviček HTTP odpovědi nebo URL"""
        
        # Nejprve se podíváme na hlavičku `Content-Disposition`
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition and "filename=" in content_disposition:
            filename = content_disposition.split("filename=")[-1].strip("\"'")
            return filename  # Pokud server poskytne název, použijeme ho

        # Pokud není název v hlavičkách, vezmeme poslední část z URL
        filename = url.split("/")[-1]
        extension = self.get_file_extension(response)
        
        # Pokud URL již obsahuje příponu, ponecháme ji
        if "." in filename:
            return filename

        # Pokud v URL není přípona, přidáme automaticky detekovanou
        return filename + (extension if extension else "")
    

    def get_file_extension(self, response):
        """Získá příponu souboru na základě Content-Type"""
        content_type = response.headers.get("Content-Type")
        if content_type:
            return mimetypes.guess_extension(content_type) or ""
        return ""
    

    def get_unique_file_path(self, filename):
        """Zkontroluje, zda soubor existuje, a pokud ano, přidává číslo v závorce před příponu"""
        base_name, _ = os.path.splitext(filename)
        extension = ".zip"
        unique_filename = base_name + extension
        counter = 1
        directory = self.download_folder

        while os.path.exists(os.path.join(directory, unique_filename)):
            unique_filename = f"{base_name}({counter}){extension}"
            counter += 1
        
        return os.path.join(directory, unique_filename)
    

    def download_file(self, url):
        """Stáhne soubor z URL a uloží ho do zadané složky s automatickým názvem a ošetřením chyb"""
        try:        
            # Odeslání GET požadavku
            #response = requests.get(url, stream=True, proxies={"http": self.proxy, "https": self.proxy}, timeout=15)  # Přidána timeout ochrana
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()  # Ověříme, zda request byl úspěšný (200 OK)
            
            # Automatické získání názvu souboru
            file_name = self.get_file_name(response, url)

            # Získáme unikátní cestu k souboru
            file_path = self.get_unique_file_path(file_name)
            
            try:
                with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    with zipf.open(file_name, "w") as zip_file:
                        for chunk in response.iter_content(chunk_size=8192):  # Stahování po blocích
                            if chunk:
                                zip_file.write(chunk)                            

                print(f"✅  Soubor byl úspěšně stažen: {file_path}")
                return "Soubor byl úspěšně stažen", file_path, False

            except (OSError, IOError, zipfile.BadZipFile) as file_error:
                # Pokud nastane problém se zápisem, smažeme neúplný soubor
                print(f"❌ Chyba při zápisu souboru: {file_error}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️  Neúplný soubor smazán: {file_path}")
                return "Chyba při zápisu souboru", file_path, True

        except requests.exceptions.RequestException as req_error:
            print(f"❌ Chyba při stahování souboru: {req_error}")
            return "Chyba při stahování souboru", None, True 
        

if __name__ == "__main__":

    for _ in range(20):
        _ = Downloader()
        print(_.proxy)      




