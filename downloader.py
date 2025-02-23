import os
import requests
import random
import mimetypes

class Downloader:
    def __init__(self):
        self.proxies = self.get_proxies()

    def get_proxies(self):
        """Získá seznam veřejných proxy serverů."""
        url = "https://www.free-proxy-list.net/"
        response = requests.get(url)

        # Extrahuje proxy servery ze stránky
        proxies = set()
        for line in response.text.split("\n"):
            if line.count(".") == 3 and ":" in line:
                proxies.add(line.strip())

        return list(proxies)   

    def get_random_proxy(self):
        # Náhodné vybrání proxy
        return random.choice(self.proxies)  

    def download_with_proxy(self, url, save_path="downloads"):
        """Stáhne soubor přes náhodnou proxy."""
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        filename = os.path.join(save_path, os.path.basename(url))

        proxy = {"http": self.get_random_proxy(), "https": self.get_random_proxy()}

        try:
            response = requests.get(url, proxies=proxy, timeout=10, stream=True)
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"✅ Soubor stažen přes proxy {proxy}")
            else:
                print(f"❌ Chyba při stahování: {response.status_code}")
        except Exception as e:
            print(f"❌ Proxy {proxy} nefunguje: {e}")     


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
    

    def get_unique_file_path(self, directory, filename):
        """Zkontroluje, zda soubor existuje, a pokud ano, přidává číslo v závorce před příponu"""
        base_name, extension = os.path.splitext(filename)
        unique_filename = filename
        counter = 1

        while os.path.exists(os.path.join(directory, unique_filename)):
            unique_filename = f"{base_name}({counter}){extension}"
            counter += 1
        
        return os.path.join(directory, unique_filename)
    

    def download_file(self, url, save_folder):
        """Stáhne soubor z URL a uloží ho do zadané složky s automatickým názvem a ošetřením chyb"""
        try:          
            # Odeslání GET požadavku
            response = requests.get(url, stream=True, timeout=15)  # Přidána timeout ochrana
            response.raise_for_status()  # Ověříme, zda request byl úspěšný (200 OK)
            
            # Automatické získání názvu souboru
            file_name = self.get_file_name(response, url)

            # Získáme unikátní cestu k souboru
            file_path = self.get_unique_file_path(save_folder, file_name)
            
            try:
                # Otevřeme soubor pro zápis
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):  # Stahování po blocích
                        if chunk:  # Zajistíme, že chunk není prázdný
                            file.write(chunk)

                print(f"✅  Soubor byl úspěšně stažen: {file_path}")
                return "Soubor byl úspěšně stažen", file_path

            except (OSError, IOError) as file_error:
                # Pokud nastane problém se zápisem, smažeme neúplný soubor
                print(f"❌ Chyba při zápisu souboru: {file_error}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️  Neúplný soubor smazán: {file_path}")
                return "Chyba při zápisu souboru", file_path

        except requests.exceptions.RequestException as req_error:
            print(f"❌ Chyba při stahování souboru: {req_error}")
            return "Chyba při stahování souboru", None

