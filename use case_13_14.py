import mysql.connector
import random
import sys

# =====================================================================
# ΣΤΟΙΧΕΙΑ ΣΥΝΔΕΣΗΣ MYSQL
# =====================================================================
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # <--- Εδώ έχεις βάλει το δικό σου password
}
DB_NAME = 'bingo_v2_db'

# =====================================================================
# 0. ΔΗΜΙΟΥΡΓΙΑ ΚΑΙ ΠΡΟΕΤΟΙΜΑΣΙΑ ΤΗΣ ΝΕΑΣ ΒΑΣΗΣ (MySQL v2)
# =====================================================================
def setup_database():
    """Δημιουργεί τη νέα βάση bingo_v2_db και εισάγει τα τελικά δεδομένα"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Καθαρισμός και Δημιουργία Βάσης (Ακριβώς από τα αρχεία v2)
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8' COLLATE 'utf8_general_ci'")
        cursor.execute(f"USE {DB_NAME}")
        
        # 1. ΚΛΑΣΕΙΣ ΧΡΗΣΤΩΝ & ΠΡΟΦΙΛ
        cursor.execute("""
        CREATE TABLE User (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            registrationDate DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """)
        
        cursor.execute("""
        CREATE TABLE Citizen (
            citizenID INT PRIMARY KEY,
            totalPoints INT DEFAULT 0,
            location VARCHAR(255),
            badges TEXT,
            FOREIGN KEY (citizenID) REFERENCES User(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """)
        
        cursor.execute("""
        CREATE TABLE Employee (
            employeeID INT PRIMARY KEY,
            FOREIGN KEY (employeeID) REFERENCES User(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """)
        
        # 2. ΚΛΑΣΕΙΣ ΔΙΚΤΥΟΥ & ΑΠΟΚΟΜΙΔΗΣ
        cursor.execute("""
        CREATE TABLE RecyclingBin (
            binID INT AUTO_INCREMENT PRIMARY KEY,
            materialType VARCHAR(50),
            location VARCHAR(255),
            status ENUM('Λειτουργικός', 'Εκτός Λειτουργίας') DEFAULT 'Λειτουργικός'
        ) ENGINE=InnoDB;
        """)
        
        cursor.execute("""
        CREATE TABLE Report (
            reportID INT AUTO_INCREMENT PRIMARY KEY,
            citizenID INT,
            binID INT,
            issueType ENUM('Βλάβη', 'Υπερχείλιση'),
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (citizenID) REFERENCES Citizen(citizenID),
            FOREIGN KEY (binID) REFERENCES RecyclingBin(binID)
        ) ENGINE=InnoDB;
        """)
        
        # 3. ΚΛΑΣΕΙΣ "ΕΞΥΠΝΩΝ" ΛΕΙΤΟΥΡΓΙΩΝ
        cursor.execute("""
        CREATE TABLE EcoRoute (
            routeID INT AUTO_INCREMENT PRIMARY KEY,
            optimalPath TEXT,
            citizenID INT,
            FOREIGN KEY (citizenID) REFERENCES Citizen(citizenID)
        ) ENGINE=InnoDB;
        """)
        
        cursor.execute("""
        CREATE TABLE AI_Assistant (
            assistantID INT AUTO_INCREMENT PRIMARY KEY,
            citizenID INT,
            FOREIGN KEY (citizenID) REFERENCES Citizen(citizenID)
        ) ENGINE=InnoDB;
        """)
        
        cursor.execute("""
        CREATE TABLE GreenChallenge (
            challengeID INT AUTO_INCREMENT PRIMARY KEY,
            goal TEXT,
            timeLimit DATETIME,
            badgeToUnlock VARCHAR(100),
            citizenID INT,
            FOREIGN KEY (citizenID) REFERENCES Citizen(citizenID)
        ) ENGINE=InnoDB;
        """)
        
        # 4. ΚΛΑΣΕΙΣ ΕΠΙΒΡΑΒΕΥΣΗΣ & ΑΞΙΟΛΟΓΗΣΗΣ
        cursor.execute("""
        CREATE TABLE Reward (
            rewardID INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100),
            pointsRequired INT,
            description TEXT
        ) ENGINE=InnoDB;
        """)
        
        cursor.execute("""
        CREATE TABLE Review (
            reviewID INT AUTO_INCREMENT PRIMARY KEY,
            citizenID INT,
            binID INT,
            rating INT CHECK (rating BETWEEN 1 AND 5),
            comment TEXT,
            FOREIGN KEY (citizenID) REFERENCES Citizen(citizenID),
            FOREIGN KEY (binID) REFERENCES RecyclingBin(binID)
        ) ENGINE=InnoDB;
        """)

        # ΕΙΣΑΓΩΓΗ ΔΕΔΟΜΕΝΩΝ ΤΗΣ ΟΜΑΔΑΣ (ΠΑΤΡΑ)
        users = [
            (1, 'Αριάδνη Σέχαι', 'ariadni@upatras.gr', 'pass1'),
            (2, 'Ελένη Καφίρη', 'eleni@upatras.gr', 'pass2'),
            (3, 'Ιωάννα Δούκα', 'ioanna@upatras.gr', 'pass3'),
            (4, 'Αιμιλιανός Κωνσταντόπουλος', 'aimilios@upatras.gr', 'pass4'),
            (5, 'Μαρία Πετροπούλου', 'maria@upatras.gr', 'pass5'),
            (6, 'Νίκος Ζέρβας', 'nikos@email.com', 'pass6'),
            (7, 'Δήμητρα Πατρινή', 'dimitra@email.com', 'pass7'),
            (8, 'Κώστας Αχαϊκός', 'kostas@email.com', 'pass8'),
            (9, 'Σοφία Ρίου', 'sofia@email.com', 'pass9'),
            (10, 'Ανδρέας Γεωργίου', 'andreas@email.com', 'pass10')
        ]
        cursor.executemany("INSERT INTO User (id, name, email, password) VALUES (%s,%s,%s,%s)", users)
        
        citizens = [
            (1, 1200, 'Αγυιά', 'Eco-Warrior, Early-Bird'),
            (2, 850, 'Ψηλαλώνια', 'Recycle-King'),
            (3, 450, 'Κάστρο', 'Starter'),
            (4, 2100, 'Ρίο', 'Champion, Green-Master'),
            (5, 150, 'Ζαρουχλέικα', 'Novice'),
            (8, 900, 'Σύνορα', 'Silver-Member'),
            (9, 320, 'Μποζαΐτικα', 'Beginner'),
            (10, 1100, 'Πλατεία Γεωργίου', 'Consistent')
        ]
        cursor.executemany("INSERT INTO Citizen (citizenID, totalPoints, location, badges) VALUES (%s,%s,%s,%s)", citizens)
        
        employees = [(6,), (7,)]
        cursor.executemany("INSERT INTO Employee (employeeID) VALUES (%s)", employees)
        
        bins = [
            (1, 'Πλαστικό', 'Πλατεία Όλγας', 'Λειτουργικός'),
            (2, 'Χαρτί', 'Πεζόδρομος Τριών Ναυάρχων', 'Λειτουργικός'),
            (3, 'Γυαλί', 'Βόρειος Λιμένας', 'Εκτός Λειτουργίας'),
            (4, 'Αλουμίνιο', 'Νότιο Πάρκο', 'Λειτουργικός')
        ]
        cursor.executemany("INSERT INTO RecyclingBin (binID, materialType, location, status) VALUES (%s,%s,%s,%s)", bins)
        
        # Εισαγωγή μερικών reviews για να δουλεύουν δυναμικά τα στατιστικά
        reviews = [
            (1, 1, 1, 5, 'Πολύ καθαρό σημείο!'),
            (2, 2, 2, 4, 'Γεμίζει γρήγορα.'),
            (3, 4, 1, 5, 'Εύκολη πρόσβαση στο Ρίο.')
        ]
        cursor.executemany("INSERT INTO Review (reviewID, citizenID, binID, rating, comment) VALUES (%s,%s,%s,%s,%s)", reviews)

        conn.commit()
        cursor.close()
        conn.close()
        print("[Σύστημα]: Η βάση δεδομένων v2 αρχικοποιήθηκε επιτυχώς!")
    except mysql.connector.Error as err:
        print(f"[Σφάλμα Βάσης]: {err}")
        sys.exit(1)


# =====================================================================
# 1. CONTROL CLASSES (Λογική Ελέγχου - Use Case Handlers)
# =====================================================================

class StatisticsController:
    """Διαχειρίζεται τον δυναμικό υπολογισμό στατιστικών από τη νέα βάση"""
    def __init__(self):
        self.categories = [
            "Συνολικοί Πράσινοι Πόντοι ανά Περιοχή (totalPoints)",
            "Κατάσταση Λειτουργίας Κάδων Ανακύκλωσης (status)",
            "Μέσος Όρος Αξιολογήσεων Πολιτών (Reviews)"
        ]

    def get_available_categories(self):
        return self.categories

    def fetch_and_process_stats(self, category_idx, time_filter):
        """Ανακτά δυναμικά τα δεδομένα (Βήματα 5 & 6)"""
        config = db_config.copy()
        config['database'] = DB_NAME
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # 12.α.1 - Εναλλακτική Ροή: Προσομοίωση απουσίας δεδομένων για Ώρα/Ημέρα
        if time_filter in ["Ημέρα", "Ώρα"] and random.choice([True, False, False]):
            cursor.close()
            conn.close()
            return None

        processed_data = {}

        if category_idx == 1:
            # Στατιστικά πόντων ανά περιοχή
            cursor.execute("SELECT location, SUM(totalPoints) FROM Citizen GROUP BY location")
            for loc, total in cursor.fetchall():
                processed_data[loc] = total

        elif category_idx == 2:
            # Κατάσταση κάδων
            cursor.execute("SELECT status, COUNT(*) FROM RecyclingBin GROUP BY status")
            for status, count in cursor.fetchall():
                processed_data[status] = count

        elif category_idx == 3:
            # Μέσος όρος αξιολογήσεων ανά κάδο/περιοχή
            cursor.execute("""
                SELECT B.location, AVG(R.rating) 
                FROM Review R 
                JOIN RecyclingBin B ON R.binID = B.binID 
                GROUP BY B.location
            """)
            for loc, avg_rating in cursor.fetchall():
                processed_data[loc] = round(avg_rating, 2)

        cursor.close()
        conn.close()
        return processed_data if len(processed_data) > 0 else None


class NotificationController:
    """Διαχειρίζεται την επικοινωνία με τους χρήστες με βάση το νέο schema"""
    def __init__(self):
        pass

    def fetch_users_from_disposal_fleet(self):
        """Ανακτά τους πολίτες (Βήμα 2)"""
        config = db_config.copy()
        config['database'] = DB_NAME
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        query = """
            SELECT U.id, U.name, U.email, C.location, C.totalPoints 
            FROM User U 
            INNER JOIN Citizen C ON U.id = C.citizenID
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def get_user_phone_mock(self, citizen_id):
        """11.α.2 - Εναλλακτική Ροή: Ανάκτηση τηλεφώνου από τα στοιχεία χρήστη"""
        return f"2610-99{citizen_id:02d}XX"

    def send_automated_message(self):
        """Βήμα 8: Προσομοίωση αναφοράς παράδοσης (True=Επιτυχής, False=Αποτυχία)"""
        return random.choice([True, False])


# =====================================================================
# 2. BOUNDARY CLASSES / UI (Διεπαφές Χρήστη)
# =====================================================================

class EmployeeDashboardUI:
    def __init__(self):
        self.stats_controller = StatisticsController()
        self.notify_controller = NotificationController()

    def run(self):
        while True:
            print("\n" + "="*50)
            print("     BinGo! Clean Service v2.0 - ΠΛΑΤΦΟΡΜΑ ΥΠΑΛΛΗΛΟΥ ")
            print("="*50)
            print("1. [ΠΧ 13] Προβολή Στατιστικών Στοιχείων")
            print("2. [ΠΧ 14] Επικοινωνία με Χρήστη / Ειδοποίηση")
            print("3. Έξοδος από το Σύστημα")
            print("-" * 50)
            choice = input("Παρακαλώ επιλέξτε ενέργεια (1-3): ")

            if choice == "1":
                self.render_statistics_flow()
            elif choice == "2":
                self.render_notification_flow()
            elif choice == "3":
                print("\nΑποσύνδεση επιτυχής. Έξοδος από την πλατφόρμα v2!")
                break
            else:
                print("[Σφάλμα]: Μη έγκυρη επιλογή, προσπαθήστε ξανά.")

    def render_statistics_flow(self):
        print("\n--- [Βήμα 1-2] ΑΝΑΖΗΤΗΣΗ ΔΙΑΘΕΣΙΜΩΝ ΚΑΤΗΓΟΡΙΩΝ ---")
        categories = self.stats_controller.get_available_categories()
        
        print("Παρακαλώ επιλέξτε τον τύπο αναφοράς που επιθυμείτε:")
        for idx, cat in enumerate(categories, 1):
            print(f"  {idx}. {cat}")
            
        try:
            cat_choice = int(input("Επιλογή κατηγορίας (1-3): "))
            if cat_choice not in [1, 2, 3]:
                print("[Σφάλμα]: Εκτός ορίων επιλογή.")
                return
        except ValueError:
            print("[Σφάλμα]: Απαιτείται αριθμός.")
            return

        print("\n--- [Βήμα 4] ΕΠΙΛΟΓΗ ΧΡΟΝΙΚΟΥ ΦΙΛΤΡΟΥ ---")
        print("1. Ανά Ημέρα")
        print("2. Ανά Ώρα")
        print("3. Ανά Μήνα")
        time_choice = input("Επιλέξτε ανάλυση χρόνου (1-3): ")
        
        time_filters = {"1": "Ημέρα", "2": "Ώρα", "3": "Μήνας"}
        selected_filter = time_filters.get(time_choice)
        
        if not selected_filter:
            print("[Σφάλμα]: Μη έγκυρο φίλτρο.")
            return

        # Ανάκτηση και επεξεργασία από τη νέα βάση
        results = self.stats_controller.fetch_and_process_stats(cat_choice, selected_filter)

        # 12.α.2 - Εναλλακτική Ροή: Απουσία Δεδομένων
        if results is None:
            print("\n" + "!"*50)
            print("Ειδοποίηση: Δεν υπάρχουν πληροφορίες για την αναφορά αυτή.")
            print("!"*50)
            input("\nΠιέστε [Enter] για επιστροφή...")
            return

        print(f"\n==================================================")
        print(f"   ΟΘΟΝΗ ΣΤΑΤΙΣΤΙΚΩΝ: {selected_filter.upper()}    ")
        print(f"   Αναφορά: {categories[cat_choice-1]}")
        print(f"==================================================")
        
        for key, val in results.items():
            if cat_choice == 1:
                print(f" * Περιοχή: {key:<15} -> Συνολικοί Πόντοι: {val} pts")
            elif cat_choice == 2:
                print(f" * Κατάσταση: {key:<15} -> Πλήθος Κάδων: {val}")
            else:
                print(f" * Περιοχή: {key:<15} -> Μέση Βαθμολογία: {val}/5 Αστέρια")
                
        print("="*50)
        input("\n[Βήμα 8] Η προβολή ολοκληρώθηκε. Πιέστε [Enter] για επιστροφή...")

    def render_notification_flow(self):
        print("\n--- [Βήμα 1-2] ΟΘΟΝΗ ΛΙΣΤΑΣ ΧΡΗΣΤΩΝ (CITIZEN FLT) ---")
        users = self.notify_controller.fetch_users_from_disposal_fleet()
        
        if not users:
            print("Δεν βρέθηκαν εγγεγραμμένοι χρήστες στη βάση.")
            return

        for idx, user in enumerate(users, 1):
            print(f" {idx}. [ID: {user[0]}] {user[1]:<28} | Γειτονιά: {user[3]:<15}")

        try:
            user_idx = int(input("\n[Βήμα 4] Επιλέξτε τον αριθμό του χρήστη για επικοινωνία: "))
            if user_idx < 1 or user_idx > len(users):
                print("[Σφάλμα]: Επιλογή εκτός λίστας.")
                return
        except ValueError:
            print("[Σφάλμα]: Παρακαλώ δώστε αριθμό.")
            return

        selected_user = users[user_idx - 1]

        # Βήμα 5: Εμφάνιση Προφίλ Χρήστη
        print("\n--------------------------------------------------")
        print("               ΟΘΟΝΗ ΠΡΟΦΙΛ ΧΡΗΣΤΗ                ")
        print("--------------------------------------------------")
        print(f"  • Κωδικός Χρήστη: {selected_user[0]}")
        print(f"  • Ονοματεπώνυμο:  {selected_user[1]}")
        print(f"  • Email Επικοινωνίας: {selected_user[2]}")
        print(f"  • Περιοχή/Location:  {selected_user[3]}")
        print(f"  • Συνολικοί Πόντοι:  {selected_user[4]}")
        print("--------------------------------------------------")

        action = input("[Βήμα 6] Επιλέγετε 'Αποστολή μηνύματος'; (ν/ο): ")
        if action.lower() != 'ν':
            print("Η διαδικασία επικοινωνίας ακυρώθηκε.")
            return

        print(f"\n[Σύστημα]: Αποστολή αυτοματοποιημένου μηνύματος: \"Παρακαλώ επικοινωνήστε με την υπηρεσία...\"")
        
        success = self.notify_controller.send_automated_message()

        if success:
            # Βασική Ροή (Βήμα 9 & 10)
            print("\n>>> [Βήμα 9]: Το μήνυμα ΠΑΡΑΔΟΘΗΚΕ και ΔΙΑΒΑΣΤΗΚΕ επιτυχώς!")
            input(">>> [Βήμα 10 - Οθόνη Επιβεβαίωσης]: Πιέστε [Enter] για επιβεβαίωση λήψης...")
        else:
            # 11.α.1 & 11.α.2 - Εναλλακτική Ροή (Απουσία αναφοράς παράδοσης)
            print("\n" + "!"*50)
            print("[Σφάλμα]: Αδυναμία λήψης αναφοράς παράδοσης του μηνύματος.")
            print("--- [11.α.2] ΟΘΟΝΗ ΚΟΙΝΟΠΟΙΗΣΗΣ ΣΤΟΙΧΕΙΩΝ ---")
            phone = self.notify_controller.get_user_phone_mock(selected_user[0])
            print(f" Το σύστημα ανέκτησε αυτόματα το τηλέφωνο του χρήστη {selected_user[1]}:")
            print(f" 📞 Τηλέφωνο Επικοινωνίας: {phone}")
            print("!"*50)
            input("\nΠιέστε [Enter] για επιστροφή στην αρχική οθόνη...")


# =====================================================================
# ΚΥΡΙΑ ΕΚΤΕΛΕΣΗ ΕΦΑΡΜΟΓΗΣ
# =====================================================================
if __name__ == "__main__":
    # 1. Έλεγχος, καθαρισμός και χτίσιμο της βάσης v2
    setup_database()
    
    # 2. Εκκίνηση του Interface του Υπαλλήλου
    app = EmployeeDashboardUI()
    app.run()