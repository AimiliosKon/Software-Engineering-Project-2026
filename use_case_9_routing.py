import re

# ==========================================
# USE CASE 9: ΕΞΥΠΝΗ "ΠΡΑΣΙΝΗ" ΔΙΑΔΡΟΜΗ (ΔΙΑΔΡΑΣΤΙΚΟ GPS)
# ==========================================
def plan_eco_route(citizen_id, user_input, context):
    
    # --- 1. ΕΛΕΓΧΟΣ ΑΝ ΕΙΜΑΣΤΕ ΗΔΗ ΣΕ ΛΕΙΤΟΥΡΓΙΑ ΠΛΟΗΓΗΣΗΣ (GPS) ---
    if context.get('active_route'):
        if re.search(r"(ξεκινα|εφτασα|επόμενη|επομενη|ναι)", user_input, re.IGNORECASE):
            route = context['active_route']
            step = context['route_step']
            
            # Αν υπάρχουν κι άλλες στάσεις
            if step < len(route):
                stop = route[step]
                context['route_step'] += 1
                return f"🧭 [GPS]: Προχώρα προς 👉 **{stop['location']}** για να πετάξεις το **{stop['material']}**.\n💡 (Μόλις φτάσεις και ρίξεις τα υλικά, γράψε 'έφτασα' για την επόμενη στάση!)"
            else:
                # Τέλος διαδρομής - Εκκαθάριση Μνήμης
                context['active_route'] = None
                context['route_step'] = 0
                return "🎉 ΜΠΡΑΒΟ! Έφτασες στον τελικό προορισμό! Ολοκλήρωσες την Πράσινη Διαδρομή και κέρδισες +50 Bonus Πόντους! 🏆"
                
        elif re.search(r"(ακυρωση|σταματα|κλεισε)", user_input, re.IGNORECASE):
             context['active_route'] = None
             return "🛑 Η πλοήγηση ακυρώθηκε. Το GPS έκλεισε."

    # --- 2. ΣΧΕΔΙΑΣΜΟΣ ΝΕΑΣ ΔΙΑΔΡΟΜΗΣ ---
    materials_found = []
    if re.search(r"(πλαστικ|μπουκαλι)", user_input, re.IGNORECASE): materials_found.append("Πλαστικό (Μπλε)")
    if re.search(r"(χαρτι|κουτι)", user_input, re.IGNORECASE): materials_found.append("Χαρτί (Μπλε)")
    if re.search(r"(γυαλι|μπουκαλα)", user_input, re.IGNORECASE): materials_found.append("Γυαλί (Κίτρινος)")
    if re.search(r"(αλουμινι|κουτακι)", user_input, re.IGNORECASE): materials_found.append("Αλουμίνιο (Μπλε)")
    
    area = None
    if re.search(r"(κεντρο|ψηλαλωνια|ολγας|γεωργιου)", user_input, re.IGNORECASE): area = "Κέντρο"
    elif re.search(r"(ριο|νοσοκομειο|αγια σοφια)", user_input, re.IGNORECASE): area = "Ρίο"
    elif re.search(r"(ζαρουχλεικα)", user_input, re.IGNORECASE): area = "Ζαρουχλέικα"

    route_points = {
        "Κέντρο": {"Πλαστικό (Μπλε)": "Πλατεία Ψηλαλωνίων", "Χαρτί (Μπλε)": "Σκαγιοπούλειο", "Γυαλί (Κίτρινος)": "Τριών Ναυάρχων", "Αλουμίνιο (Μπλε)": "Ρήγα Φεραίου"},
        "Ρίο": {"Πλαστικό (Μπλε)": "Πλατεία Αγίας Σοφίας", "Χαρτί (Μπλε)": "Νοσοκομείο Ρίου", "Γυαλί (Κίτρινος)": "Μποζαΐτικα", "Αλουμίνιο (Μπλε)": "Κέντρο Ρίου"}
    }

    if len(materials_found) > 1 and area:
        # Φτιάχνουμε τις Στάσεις και τις ΑΠΟΘΗΚΕΥΟΥΜΕ στη μνήμη (για το GPS)
        stops = []
        for mat in materials_found:
            loc = route_points.get(area, {}).get(mat, "Κοντινός Κάδος")
            stops.append({"material": mat, "location": loc})
        
        # Ενεργοποίηση Μνήμης Πλοήγησης
        context['active_route'] = stops
        context['route_step'] = 0
        
        route_str = f"🗺️ ΕΞΥΠΝΟ GPS (Περιοχή: {area}): Βρήκα την ιδανική διαδρομή!\n"
        for i, stop in enumerate(stops):
            route_str += f"  📍 {i+1}η Στάση: {stop['location']} (για {stop['material']})\n"
        
        route_str += "\n🚙 Γράψε **'ξεκινάμε'** για να ανοίξω την πλοήγηση βήμα-βήμα, ή 'ακύρωση'!"
        return f"🤖 BinGo AI:\n{route_str}"
        
    elif len(materials_found) > 1 and not area:
        return "🤖 BinGo AI (GPS): Βλέπω πολλά υλικά! Σε ποια περιοχή είσαι για να βγάλω το δρομολόγιο;"
    else:
        return "🤖 BinGo AI (GPS): Για δρομολόγιο, πες μου τουλάχιστον 2 υλικά και την περιοχή. (π.χ. 'δρομολόγιο για χαρτί και γυαλί στο κέντρο')"