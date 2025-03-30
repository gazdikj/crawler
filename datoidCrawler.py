import traceback
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from hashManager import calculate_sha256, save_hashes
from baseCrawler import BaseCrawler


class DatoidCrawler(BaseCrawler):        

    def format_url(self, url: str, text: str, index: int) -> str:
        formatted_text = text.replace(" ", "-")  # Nahrazení mezer pomlčkami .rstrip('/')
        return f"{url}/s/{formatted_text}/{index}"    
     

    def find_next_button(self) -> bool:
        try:
            # Čekáme až 5 sekund, než se objeví tlačítko Další
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.next.ajax"))
            )
            print("✅ Tlačítko 'Další stránka' nalezeno. Pokračujeme stahovnáním další page.")
            return True
        
        except:
            print("❌ Tlačítko 'Další stránka' nenalezeno. Posledni page ke stažení.")
            return False     
        

    def close_window(self) -> None:
        self.driver.close() # zavře aktualní okno s detailem
        self.driver.switch_to.window(self.driver.window_handles[0]) # vratí se na puvodní okno  


    def update_task_state(sefl, task, status, file_name, file_size, current_index, total_index, page) -> None:
        count = current_index + 25 * (page - 1)    
        #task.update_state(state="CRAWLING", meta={"file_name": file_name, "file_size": file_size, "current": count, "status": status})


    def get_parsed_file_info(self, file_info) -> str:
        cleared_data = [item.strip() for item in file_info.split("\n") if item.strip()]
        extension = cleared_data[0]
        size = cleared_data[-2]
        title = cleared_data[-1]
        print(f"title: {title}, extension: {extension}, size: {size}")
        return title, extension, size
    

    def check_size(self, file_size) -> bool:
        if 'GB' in file_size: 
            print(f"❌ Velikost souboru {file_size} je příliš velka a nepodporuje stažení")
            return False

        if 'MB' in file_size:           
            cislo = "".join(c for c in file_size if c.isdigit() or c == ".")
            size = float(cislo)

            if size > 20:
                print(f"❌ Velikost souboru {size} MB je příliš velka a nepodporuje stažení")
                return False
            else:
                print(f"✅  Velikost souboru {size} MB podporuje stažení")
                return True

        print(f"✅  Velikost souboru {file_size} MB podporuje stažení")
        return True        


    def crawl_page(self, task, page):
        # Počkáme, než se načtou všechny položky
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.filename"))
        )

        items = self.driver.find_elements(By.CSS_SELECTOR, "a:has(span.filename)")
        
        print(f"🔹  Nalezeno {len(items)} souborů ke stažení.")

        for index, item in enumerate(items):
            file_title = file_extension = file_size = download_exeption = file_extension = size_exception = timeout_exception = download_path = None
            try:
                file_info = item.get_attribute("text")
                file_title, file_extension, file_size = self.get_parsed_file_info(file_info)

                self.update_task_state(task, "Získávaní informací", file_title, file_size, index + 1, len(items), page)               

                if not self.check_size(file_size): 
                    size_exception = f"Velikost souboru {file_title} je příliš velká: {file_size}" 
                    self.update_task_state(task, "Velikost souboru nepodporuje stažení", file_title, file_size, index + 1, len(items), page)                    
                    continue

                file_onclick = item.get_attribute("onclick")
                file_onclick
                item_link = file_onclick.split('window.open("')[-1].split('");')[0]
                self.driver.execute_script("window.open(arguments[0]);", item_link) # Otevření nového okna pro detail souboru
                self.driver.switch_to.window(self.driver.window_handles[1])  # Přepnout na nové okno
                """
                file_link = item.get_attribute("href")
                print(f"➡️   Otevírám detail souboru: {file_link}")

                self.driver.execute_script("window.open(arguments[0]);", file_link) # Otevření nového okna pro detail souboru
                self.driver.switch_to.window(self.driver.window_handles[1])  # Přepnout na nové okno
                """

                print("➡️   Klikám na tlačítko 'Stáhnout'")
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-download.detail-download"))
                ).click()

                self.update_task_state(task, "Čekání 30s pro stahování", file_title, file_size, index + 1, len(items), page)
                print("⏳  Čekám 30s pro stahování")
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.download"))
                ).click()

                download_link_element = WebDriverWait(self.driver, 40).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.link-to-file"))
                )

                self.update_task_state(task, "Stahování souboru", file_title, file_size, index + 1, len(items), page)
                download_link = download_link_element.get_attribute("href")

                print(f"✅  Link pro stažení souboru: {download_link}")
                self.driver.get(download_link)
                #download_info, download_path, download_exeption = self.downloader.download_file(download_link)
                
                self.close_window()

                #self.update_task_state(task, download_info, file_title, file_size, index + 1, len(items), page)

                if download_path:
                    hash = calculate_sha256(download_path)
                    download_file_title = os.path.basename(download_path)
                    save_hashes(download_file_title, hash)
                    self.update_task_state(task, "Vytrořen hash pro stažený soubor", file_title, file_size, index + 1, len(items), page)

                print("✅  Stažení souboru dokončeno")
                                        
            except TimeoutException as e:
                print(f"❌ Timeout při pokusu o nalezení linku pro stažení souboru: {index + 1}")                 
                timeout_exception = f"Timeout při pokusu o stažení souboru: {file_title}" 
                self.close_window()   

            finally:
                if download_path:
                    db_hash_id = self.db.insert_hash(hash)
                    db_crack_id = self.db.insert_crack(file_title, file_size, file_extension, download_file_title, db_hash_id)
                else:
                    db_crack_id = self.db.insert_crack(file_title, file_size, file_extension, None, None)
                
                if download_exeption:
                    self.db.insert_error(download_info, db_crack_id) 

                if timeout_exception:
                    self.db.insert_error(timeout_exception, db_crack_id)                     

                if size_exception:
                    self.db.insert_error(size_exception, db_crack_id)
                


    def crawl(self, task):
        self.driver.get("http://whatismyipaddress.com")
        page = 0
        try:
            while True: 
                page = page + 1
                formatted_url = self.format_url(self.url, self.keyword, page) 
                print(formatted_url)
                self.driver.get(formatted_url)
                try:
                    self.crawl_page(task=task, page=page)          
                    if not self.find_next_button():
                        break

                except Exception as e:
                    print(f"❌ Chyba při načítání hlavní stránky: {e}")
                    #traceback.print_exc()
                    break

        finally:
            self.driver.quit()