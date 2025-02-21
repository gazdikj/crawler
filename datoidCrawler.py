import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from baseCrawler import BaseCrawler
from downloader import Downloader

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
        

    def crawl_page(self, task):
        # Počkáme, než se načtou všechny položky
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.filename"))
        )

        items = self.driver.find_elements(By.CSS_SELECTOR, "a:has(span.filename)")
        
        print(f"🔹  Nalezeno {len(items)} souborů ke stažení.")

        for index, item in enumerate(items):
            try:
                file_link = item.get_attribute("href")
                print(f"➡️   Otevírám detail souboru: {file_link}")

                # Otevřeme nový detail souboru
                self.driver.execute_script("window.open(arguments[0]);", file_link)
                self.driver.switch_to.window(self.driver.window_handles[1])  # Přepnout na nové okno

                print("➡️   Klikám na tlačítko 'Stáhnout'")
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-download.detail-download"))
                ).click()

                print("⏳  Čekám 30s pro stahování")
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.download"))
                ).click()

                print("✅  Stažení souboru zahájeno")
                WebDriverWait(self.driver, 40).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.link-to-file"))
                ).click()

                # Po stažení zavřeme detail souboru a vrátíme se zpět
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

                # informace o statu jobu
                task.update_state(state="CRAWLING", meta={"current": index + 1, "total": len(items)})

                break
                                        
            except Exception as e:
                print(f"❌ Chyba při zpracování souboru {index + 1}: {e}")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])     


    def crawl(self, url, task, what_to_crawl=""):
        index = 1
        try:
            while True: 
                formatted_url = self.format_url(url, what_to_crawl, index) 
                print(formatted_url)
                self.driver.get(formatted_url)
                try:
                    self.crawl_page(task=task) 
                    #time.sleep(5)           
                    index = index + 1
                    if not self.find_next_button():
                        break
                    #time.sleep(1)

                except Exception as e:
                    print(f"❌ Chyba při načítání hlavní stránky: {e}")

        finally:
            self.driver.quit()