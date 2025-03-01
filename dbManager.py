import pyodbc
import time

from config import SERVER_NAME

# Nastavení připojení k databázi
DB_DRIVER = "SQL Server"
DB_SERVER = SERVER_NAME
DB_DATABASE = "CrawlerDB"

CONNECTION_STRING = f"""
    DRIVER={{{DB_DRIVER}}};
    SERVER={SERVER_NAME};
    DATABASE={DB_DATABASE};
    Trust_Connection=yes;
"""

class DBManager:
    def __init__(self, url, keyword, driver, device):        
        self.webdriver_id = self.insert_webdriver(driver)
        self.device_id = self.insert_device(device)
        self.crawler_id = self.insert_crawler(url)
        self.job_id = self.insert_crawl_job(keyword, self.crawler_id, self.webdriver_id, self.device_id)


    # Pomocná funkce pro získání ID existujícího záznamu (nebo vložení nového)
    def get_or_create(self, cursor, table, column, value):
        cursor.execute(f"SELECT {table}ID FROM {table} WHERE {column} = ?", (value,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", (value,))
            cursor.connection.commit()
            return cursor.execute(f"SELECT {table}ID FROM {table} WHERE {column} = ?", (value,)).fetchone()[0]

    # Funkce pro vložení WebDriver
    def insert_webdriver(self, name):
        with pyodbc.connect(CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            return self.get_or_create(cursor, "WebDriver", "Name", name)

    # Funkce pro vložení Device
    def insert_device(self, name):
        with pyodbc.connect(CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            return self.get_or_create(cursor, "Device", "Name", name)

    # Funkce pro vložení Crawler
    def insert_crawler(self, url):
        with pyodbc.connect(CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            return self.get_or_create(cursor, "Crawler", "WebURL", url)

    # Funkce pro vložení CrawlJob
    def insert_crawl_job(self, keyword, crawler_id, web_driver_id, device_id):
        with pyodbc.connect(CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO CrawlJob (Keyword, StartTime, CrawlerID, WebDriverID, DeviceID) 
                    OUTPUT INSERTED.JobID  
                    VALUES (?, GETDATE(), ?, ?, ?)
                """, (keyword, crawler_id, web_driver_id, device_id))
                
                new_id = cursor.fetchone()[0]  
                conn.commit()
                
                print(f"Nový CrawlJob vložen s ID: {new_id}")
                return new_id

            except pyodbc.IntegrityError:
                print("Chyba při vkládání CrawlJobu")
                return None    

    # Funkce pro vložení Hash
    def insert_hash(self, hash):
        with pyodbc.connect(CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            return self.get_or_create(cursor, "Hash", "Hash", hash)

    # Funkce pro vložení Crack (staženého souboru)
    def insert_crack(self, title, size, extension, zipfile, hash_id=None):
        with pyodbc.connect(CONNECTION_STRING) as conn:      
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO Crack (Title, Size, Extension, ZIPFileTitle, CreatedAt, JobID, HashID) 
                    OUTPUT INSERTED.CrackID  
                    VALUES (?, ?, ?, ?, GETDATE(), ?, ?)
                """, (title, size, extension, zipfile, self.job_id, hash_id))
                
                new_id = cursor.fetchone()[0] 
                conn.commit()
                
                print(f"Nový Crack vložen s ID: {new_id}")
                return new_id

            except pyodbc.IntegrityError:
                print("Chyba při vkládání Cracku")
                return None         
        
    # Funkce pro vložení Error 
    def insert_error(self, error_message, crack_id):
        with pyodbc.connect(CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO Error (ErrorMessage, OccurredAt, CrackID)
                    OUTPUT INSERTED.ErrorID 
                    VALUES (?, GETDATE(), ?)
                """, (error_message, crack_id))

                new_id = cursor.fetchone()[0]
                conn.commit() 

                print(f"Nový Error vložen s ID: {new_id}")
                return new_id                          

            except pyodbc.IntegrityError:
                print("Chyba při vkládání Cracku")     

# Testovací volání funkcí
if __name__ == "__main__":
    db = DBManager("ChromeDriver", "Windows 10")

    t = time.time()
    #db.set_crawler_id("url.com")
    #db.set_job_id("pes")
    hash_id = db.insert_hash("1234567890abcdef")
    crack_id = db.insert_crack("ABC.mp3","10 MB", ".MP3", "ABC.zip", hash_id)
    #db.insert_error("chyba", crack_id)

    print(f"Cas: {time.time() - t}")
