import mysql.connector

def get_connection():
    """Επιστρέφει ενεργή σύνδεση με τη βάση δεδομένων BinGo!"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12martiou",  # Ο σωστός κωδικός της MySQL σου
            database="bingo_v2_db"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"❌ Σφάλμα σύνδεσης στη βάση δεδομένων: {err}")
        return None