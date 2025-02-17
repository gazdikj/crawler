import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from baseCrawler import BaseCrawler
from downloader import Downloader

class datoidCrawler(BaseCrawler):

    def crawl(self, url):
            """Prochází hlavní stránku, vstupuje do detailu a stahuje soubory."""
            self.driver.get(url)

            try:
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
                                             
                    except Exception as e:
                        print(f"❌ Chyba při zpracování souboru {index + 1}: {e}")
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])

            except Exception as e:
                print(f"❌ Chyba při načítání hlavní stránky: {e}")

            finally:
                self.driver.quit()