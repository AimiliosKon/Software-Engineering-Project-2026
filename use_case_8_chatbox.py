# ==============================================================================
# 🌟 BINGO AI: ΨΗΦΙΑΚΟΣ ΒΟΗΘΟΣ ΑΝΑΚΥΚΛΩΣΗΣ (USE CASE 8) - FINAL PRO VERSION 🌟
# ==============================================================================

import re                  # Για την αναγνώριση λέξεων (Regex)
import random              # Για τυχαίες επιλογές (Κουίζ, Χαιρετισμοί)
import urllib.request      # Για Web Scraping (Ειδήσεις)
import xml.etree.ElementTree as ET 

# --- 1. ΑΛΕΞΙΣΦΑΙΡΑ IMPORTS ---
# Έλεγχος για το Use Case 9 (Διαδρομές)
try:
    from use_case_9_routing import plan_eco_route
except ImportError:
    def plan_eco_route(citizen_id, user_input, context):
        return "❌ Σφάλμα: Δεν βρίσκω το αρχείο 'use_case_9_routing.py'. Βεβαιώσου ότι υπάρχει στον φάκελο!"

# Έλεγχος για τη Βάση Δεδομένων (MySQL)
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

# Έλεγχος για το Τοπικό AI (Ollama)
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

DB_PASSWORD = "12martiou" # Ο κωδικός της βάσης

def get_db_connection():
    if not MYSQL_AVAILABLE:
        raise Exception("Δεν βρέθηκε η βιβλιοθήκη mysql-connector-python.")
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=DB_PASSWORD,
        database="bingo_v2_db"
    )

# ==========================================
# 2. ΣΤΑΤΙΚΕΣ ΓΝΩΣΕΙΣ / ΧΑΙΡΕΤΙΣΜΟΙ
# ==========================================
def greeting(citizen_id, user_input, context):
    greetings = [
        "🤖 BinGo AI: Γεια σου! Είμαι ο ψηφιακός σου βοηθός. Πώς μπορώ να σε βοηθήσω σήμερα;", 
        "🤖 BinGo AI: Καλησπέρα! Είμαι γεμάτος πράσινη ενέργεια, τι θα κάνουμε;"
    ]
    return random.choice(greetings)

# ==========================================
# 3. LIVE ΕΙΔΗΣΕΙΣ & ΔΡΑΣΕΙΣ (WEB SCRAPING)
# ==========================================
def get_live_eco_news(citizen_id, user_input, context):
    print("⏳ Το BinGo ψάχνει ζωντανά τις τελευταίες περιβαλλοντικές δράσεις...")
    try:
        url = "https://news.google.com/rss/search?q=%CE%B1%CE%BD%CE%B1%CE%BA%CF%8D%CE%BA%CE%BB%CF%89%CF%83%CE%B7&hl=el&gl=GR&ceid=GR:el"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        news_list = []
        for item in root.findall('.//item')[:3]: 
            title = item.find('title').text
            clean_title = title.rsplit(' - ', 1)[0]
            news_list.append("🌱 " + clean_title)
            
        # Τοπική δράση Πάτρας
        news_list.append("\n📅 ΔΡΑΣΗ ΔΗΜΟΥ ΠΑΤΡΕΩΝ: Αυτή την Κυριακή, εθελοντικός καθαρισμός στο Νότιο Πάρκο! Σε περιμένουμε!")
        return "🤖 BinGo AI (LIVE ΔΡΑΣΕΙΣ):\n" + "\n".join(news_list)
    except Exception as e:
        return "🤖 BinGo AI: Δεν έχω σύνδεση στο ίντερνετ για να βρω τις σημερινές δράσεις."

# ==========================================
# 4. GAMIFICATION: SUPER QUIZ ΜΕ ΚΟΥΠΟΝΙ!
# ==========================================
def give_quiz_points(citizen_id, user_input, context):
    easy_questions = [
        {"q": "Τι χρώμα κάδο χρησιμοποιούμε για την ανακύκλωση συσκευασιών;", "opts": "1) Μπλε\n2) Πράσινο", "ans": "1", "msg": "Ο Μπλε κάδος είναι για τις συσκευασίες!"},
        {"q": "Πού πετάμε τις παλιές μπαταρίες;", "opts": "1) Στον Μπλε κάδο\n2) Ειδικούς κάδους ΑΦΗΣ", "ans": "2", "msg": "Οι μπαταρίες ανακυκλώνονται μόνο στην ΑΦΗΣ."},
        {"q": "Τι κάνουμε τα πλαστικά μπουκάλια πριν τα πετάξουμε;", "opts": "1) Τα γεμίζουμε με νερό\n2) Τα συμπιέζουμε", "ans": "2", "msg": "Η συμπίεση εξοικονομεί τεράστιο χώρο!"},
        {"q": "Επιτρέπονται οργανικά σκουπίδια (αποφάγια) στον Μπλε Κάδο;", "opts": "1) Ναι\n2) Όχι", "ans": "2", "msg": "Τα αποφάγια καταστρέφουν την ανακύκλωση."}
    ]

    hard_questions = [
        {"q": "Τι ανακυκλώνεται άπειρες φορές χωρίς να χάσει ΚΑΘΟΛΟΥ την ποιότητά του;", "opts": "1) Χαρτί\n2) Πλαστικό\n3) Γυαλί", "ans": "3", "msg": "Το γυαλί μπορεί να ανακυκλωθεί άπειρες φορές!"},
        {"q": "Πού πετάμε το λαδωμένο κουτί από πίτσα;", "opts": "1) Μπλε κάδο\n2) Πράσινο κάδο", "ans": "2", "msg": "Τα λάδια καταστρέφουν το χαρτί. Πάει στα σύμμικτα!"},
        {"q": "Μπορούμε να πετάξουμε καθρέφτες στον Μπλε Κάδο;", "opts": "1) Ναι\n2) Όχι", "ans": "2", "msg": "Οι καθρέφτες έχουν άλλη θερμοκρασία τήξης από τα μπουκάλια."},
        {"q": "Πώς πρέπει να ρίχνουμε τα υλικά στον Μπλε Κάδο;", "opts": "1) Μέσα σε δεμένη σακούλα\n2) Χύμα και άδεια", "ans": "2", "msg": "Πρέπει να πέφτουν χύμα για εύκολο διαχωρισμό."},
        {"q": "Ποιο υλικό ΧΡΕΙΑΖΕΤΑΙ ΤΗΝ ΠΕΡΙΣΣΟΤΕΡΗ ενέργεια για να φτιαχτεί από την αρχή;", "opts": "1) Αλουμίνιο\n2) Χαρτί\n3) Γυαλί", "ans": "1", "msg": "Η ανακύκλωση αλουμινίου σώζει το 95% της ενέργειας παραγωγής του!"}
    ]

    print("\n" + "="*60)
    print("🏆 BINGO SUPER QUIZ: ΞΕΚΛΕΙΔΩΣΕ ΚΟΥΠΟΝΙ ΑΞΙΑΣ 3€!")
    print("="*60)
    print("🟢 ΕΠΙΠΕΔΟ 1: ΕΥΚΟΛΕΣ ΕΡΩΤΗΣΕΙΣ (Στόχος: 4/4 για +100 πόντους)")
    
    # --- ΦΑΣΗ 1 ---
    for i, item in enumerate(easy_questions):
        ans = input(f"\n❓ [Εύκολη {i+1}/4] {item['q']}\n{item['opts']}\n👤 Απάντηση: ").strip()
        if ans == item['ans']:
            print(f"✅ Σωστά! {item['msg']}")
        else:
            print(f"❌ Λάθος! {item['msg']}")
            print("\n🏁 Δεν κατάφερες το 4/4. Δοκίμασε ξανά αργότερα!")
            return "🤖 BinGo AI: Το κουίζ τερματίστηκε."

    print("\n" + "~"*60)
    print("🎉 ΜΠΡΑΒΟ! Έκανες 4/4 στις Εύκολες (+100 Πόντοι). Περνάς στην τελική φάση!")
    print("🔴 ΕΠΙΠΕΔΟ 2: ΔΥΣΚΟΛΕΣ ΕΡΩΤΗΣΕΙΣ (Στόχος: 5/5 για 1200 Πόντους & ΚΟΥΠΟΝΙ!)")
    
    # --- ΦΑΣΗ 2 ---
    for i, item in enumerate(hard_questions):
        ans = input(f"\n❓ [Δύσκολη {i+1}/5] {item['q']}\n{item['opts']}\n👤 Απάντηση: ").strip()
        if ans == item['ans']:
            print(f"✅ Σωστά! {item['msg']}")
        else:
            print(f"❌ Λάθος! {item['msg']}")
            print("\n🏁 Έχασες στις δύσκολες. Κρατάς τους 100 πόντους από το Επίπεδο 1!")
            if MYSQL_AVAILABLE:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE citizen SET totalPoints = COALESCE(totalPoints, 0) + 100 WHERE citizenID = %s", (citizen_id,))
                    conn.commit()
                except: pass
            return "🤖 BinGo AI: Το κουίζ τερματίστηκε."

    # --- ΝΙΚΗ! ---
    print("\n" + "="*60)
    print("🥳 ΑΠΙΣΤΕΥΤΟ! ΕΙΣΑI MASTER ΤΗΣ ΑΝΑΚΥΚΛΩΣΗΣ! 🏆")
    coupon_code = f"BINGO-{random.randint(10000, 99999)}"
    
    if not MYSQL_AVAILABLE:
        return f"🌟 (Safe Mode): +1200 Πόντοι!\n🎟️ ΚΟΥΠΟΝΙ 3€: {coupon_code}"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("UPDATE citizen SET totalPoints = COALESCE(totalPoints, 0) + 1200 WHERE citizenID = %s", (citizen_id,))
        conn.commit()
        cursor.execute("SELECT totalPoints FROM citizen WHERE citizenID = %s", (citizen_id,))
        result = cursor.fetchone()
        
        return f"🎉 Πιστώθηκαν +1200 Πράσινοι Πόντοι! (Σύνολο: {result['totalPoints']})\n🎟️ ΕΠΙΒΡΑΒΕΥΣΗ: Ξεκλείδωσες Κουπόνι 3€!\n👉 ΚΩΔΙΚΟΣ: ** {coupon_code} **"
    except:
        return f"🎉 Κέρδισες 1200 Πόντους!\n🎟️ ΚΩΔΙΚΟΣ ΚΟΥΠΟΝΙΟΥ: {coupon_code}"

# ==========================================
# 5. ΕΓΚΕΦΑΛΟΣ ΕΥΡΕΣΗΣ ΚΑΔΩΝ (Η ΜΝΗΜΗ)
# ==========================================
def handle_bins_request(citizen_id, user_input, context):
    material = None
    area = None
    
    # 1. Αναγνώριση Υλικού
    if re.search(r"(πλαστικ|μπουκαλι|πλαστικό|μπουκάλι)", user_input, re.IGNORECASE): material = "Πλαστικό (Μπλε Κάδος)"
    elif re.search(r"(χαρτι|κουτι|χαρτί|κουτί)", user_input, re.IGNORECASE): material = "Χαρτί (Μπλε Κάδος)"
    elif re.search(r"(γυαλι|γυαλί|μπουκαλα|μπουκάλα)", user_input, re.IGNORECASE): material = "Γυαλί (Κίτρινος Κάδος)"
    elif re.search(r"(αλουμινι|αλουμίνιο|κουτακι|κουτάκι)", user_input, re.IGNORECASE): material = "Αλουμίνιο (Μπλε Κάδος)"
    
    # 2. Αναγνώριση Περιοχής
    if re.search(r"(κεντρο|κέντρο|ψηλαλωνια|ψιλαλώνια)", user_input, re.IGNORECASE): area = "Κέντρο"
    elif re.search(r"(ριο|ρίο|νοσοκομειο|νοσοκομείο)", user_input, re.IGNORECASE): area = "Ρίο"
    elif re.search(r"(τει|κουκουλι|κουκούλι)", user_input, re.IGNORECASE): area = "ΤΕΙ"

    # 3. Ενημέρωση Μνήμης
    if material: context['last_material'] = material
    if area: context['last_area'] = area
    
    saved_mat = context.get('last_material')
    saved_area = context.get('last_area')

    # 4. Βάση Δεδομένων Σημείων
    bins_db = {
        "Πλαστικό (Μπλε Κάδος)": {"Κέντρο": ["Πλατεία Ψηλαλωνίων"], "Ρίο": ["Πλατεία Αγίας Σοφίας"], "ΤΕΙ": ["Έξω από το ΤΕΙ (Κουκούλι)"]},
        "Χαρτί (Μπλε Κάδος)": {"Κέντρο": ["Σκαγιοπούλειο"], "Ρίο": ["Νοσοκομείο Ρίου"], "ΤΕΙ": ["Κεντρική Βιβλιοθήκη ΤΕΙ"]},
        "Γυαλί (Κίτρινος Κάδος)": {"Κέντρο": ["Πεζόδρομος Τριών Ναυάρχων"], "Ρίο": ["Μποζαΐτικα"], "ΤΕΙ": ["Κυλικείο ΤΕΙ"]},
        "Αλουμίνιο (Μπλε Κάδος)": {"Κέντρο": ["Ρήγα Φεραίου"], "Ρίο": ["Κέντρο Ρίου"], "ΤΕΙ": ["Κλειστό Γυμναστήριο (Ταρταράς)"]}
    }

    # 5. Λογική Απάντησης
    if saved_mat and saved_area:
        locations = bins_db.get(saved_mat, {}).get(saved_area, [])
        context['last_material'] = None 
        context['last_area'] = None
        if locations:
            return f"📍 BinGo AI: Για {saved_mat} στο {saved_area}, η πιο κοντινή στάση είναι: {locations[0]}"
        return f"🤖 BinGo AI: Δεν βρήκα κάδο για {saved_mat} στο {saved_area}."
    elif saved_mat and not saved_area:
        return f"🤖 BinGo AI: Θέλεις να πετάξεις {saved_mat}. Σε ποια περιοχή βρίσκεσαι;"
    elif not saved_mat and saved_area:
        return f"🤖 BinGo AI: Είσαι εδώ: {saved_area}. Τι υλικό θέλεις να πετάξεις;"
    else:
        return "🤖 BinGo AI: Τι υλικό θέλεις να πετάξεις και πού βρίσκεσαι;"

# ==========================================
# 6. ΤΟ ΥΠΕΡ-ΛΕΞΙΚΟ (REGEX MAPPING)
# ==========================================
LOCAL_PAIRS = [
    (r".*(γεια|καλημερα|καλημέρα|hello).*", greeting),
    (r".*(κουιζ|κουίζ|quiz|παιχνιδι|παιχνίδι).*", give_quiz_points),
    (r".*(νεα|νέα|ειδησεις|ειδήσεις|δρασεις|δράσεις).*", get_live_eco_news),
    (r".*(διαδρομη|διαδρομή|δρομολογιο|δρομολόγιο|eco-routing|πολλαπλα|ξεκινα|ξεκινά|εφτασα|έφτασα|ακυρωση|ακύρωση).*", plan_eco_route),
    (r".*(καδ|κάδ|πετα|πετά|περιοχ|γυαλι|γυαλί|χαρτι|χαρτί|πλαστικ|πλαστικό|αλουμινι|αλουμίνιο|κεντρο|κέντρο|ριο|ρίο|τει|κουκουλι).*", handle_bins_request), 
]

# ==========================================
# 7. AI FALLBACK (OLLAMA / GEMMA)
# ==========================================
def smart_search(user_message):
    if not OLLAMA_AVAILABLE:
        return "🧠 BinGo (Safe Mode): Ρώτα με για 'κάδους', 'δράσεις', ή πες 'κουίζ'!"
    try:
        response = ollama.chat(model='gemma2:2b', messages=[
            {'role': 'system', 'content': 'Είσαι ο BinGo AI, βοηθός ανακύκλωσης. Να απαντάς ΠΑΝΤΑ στα Ελληνικά, σύντομα και ευγενικά.'},
            {'role': 'user', 'content': user_message},
        ])
        return "🧠 BinGo (Gemma AI): \n" + response['message']['content'].strip()
    except Exception as e:
        return "🧠 BinGo (Safe Mode): Το τοπικό μοντέλο AI δεν είναι ενεργό αυτή τη στιγμή."

# ==========================================
# 8. ΤΟ ΚΕΝΤΡΙΚΟ LOOP (Η ΚΑΡΔΙΑ ΤΟΥ BINGO)
# ==========================================
def converse(citizen_id):
    print("\n" + "="*50)
    print("🌟 BINGO AI - ΕΞΥΠΝΟΣ ΒΟΗΘΟΣ ΑΝΑΚΥΚΛΩΣΗΣ 🌟")
    print("="*50)
    print("💡 Μπορείς να ρωτήσεις για: Κάδους (π.χ. πού έχει γυαλί στο ΤΕΙ;)")
    print("💡 Μπορείς να ζητήσεις: 'Δράσεις', 'Κουίζ' ή 'Διαδρομή'")
    print("💡 Γράψε 'τέλος' για έξοδο.\n")

    chatbot_memory = {"last_material": None, "last_area": None}

    while True: 
        user_input = input("👤 Εσύ: ").strip()

        if user_input.lower() in ['έξοδος', 'εξοδος', 'exit', 'τέλος', 'τελος']:
            print("🤖 BinGo AI: Τα λέμε! Συνέχισε να ανακυκλώνεις! 🌍")
            break

        if not user_input: continue

        match_found = False
        for pattern, action in LOCAL_PAIRS:
            if re.match(pattern, user_input, re.IGNORECASE):
                print(action(citizen_id, user_input, chatbot_memory))
                match_found = True
                break
        
        if not match_found:
            print("⏳ Το BinGo AI σκέφτεται...")
            print(smart_search(user_input))

# Εκκίνηση του προγράμματος
if __name__ == "__main__":
    converse(citizen_id=1)