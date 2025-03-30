import pyodbc

from config import SERVER_NAME, DB_USER, DB_PASSWORD

# Nastavení připojení k databázi
DB_DRIVER = "SQL Server"
DB_SERVER = SERVER_NAME
DB_DATABASE = "CrackDB"

CONNECTION_STRING = f"""
    DRIVER={{{DB_DRIVER}}};
    SERVER={SERVER_NAME};
    DATABASE={DB_DATABASE};
    Trust_Connection=yes;
"""

def insert_sample(filename, test_id):
    with pyodbc.connect(CONNECTION_STRING) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO sample (name, testid, crack_id, analysis_id)
                OUTPUT INSERTED.id 
                VALUES (?, ?, NULL, NULL)
            """, (filename, test_id))                       

        except pyodbc.IntegrityError:
            print("Chyba při vkládání vzorku")  

def update_sample(test_id, analysis_id):
    with pyodbc.connect(CONNECTION_STRING) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE sample
                SET analysed = 1, analysis_id = ?
                WHERE testid = ?
            """, (analysis_id, test_id))                       

        except pyodbc.IntegrityError:
            print("Chyba při vkládání vzorku")             

# Funkce pro vložení analýzy 
def insert_analysis(status, undetected, malicious, harmless, sha256):
    with pyodbc.connect(CONNECTION_STRING) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO analysis (status, undetected, malicious, harmless, sha256)
                OUTPUT INSERTED.id 
                VALUES (?, ?, ?, ?, ?)
            """, (status, undetected, malicious, harmless, sha256))

            new_id = cursor.fetchone()[0]
            conn.commit() 

            print(f"Nová analýza vložena s ID: {new_id}")
            return new_id                          

        except pyodbc.IntegrityError:
            print("Chyba při vkládání analýzy")   

# Funkce pro antiviru analýzy 
def insert_antivirus(engine_name, engine_category, engine_result, analysisId):
    with pyodbc.connect(CONNECTION_STRING) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO antivirus (engine, category, result, analysis_id)
                OUTPUT INSERTED.id 
                VALUES (?, ?, ?, ?)
            """, (engine_name, engine_category, engine_result, analysisId))                       

        except pyodbc.IntegrityError:
            print("Chyba při vkládání analýzy")                               


# Testovací volání funkcí
if __name__ == "__main__":
    pass
