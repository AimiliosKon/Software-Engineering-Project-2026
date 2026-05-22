# ======================================================
# BinGo — logic.py
# All 12 Use Cases, refactored for GUI use.
#
# Rules applied throughout:
#   - No print() anywhere  → every function returns a dict
#   - No input() anywhere  → GUI passes values as arguments
#   - No global db/cursor  → each function opens & closes its own connection
#   - All DB passwords via db.get_connection() only
#   - No code that runs on import (no bare calls at module level)
# ======================================================

import re
import random
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

from db import get_connection


# ======================================================
# DATA MODELS  (UC1 · UC2 · UC3)
# ======================================================

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email


class GreenChallenge:
    def __init__(self, title):
        self.title = title


class Citizen(User):
    def __init__(self, name, email, total_points, total_recycling, badges):
        super().__init__(name, email)
        self.total_points    = total_points
        self.total_recycling = total_recycling
        self.badges          = badges
        self.challenges      = []
        self.transactions    = []
        self.location_enabled  = True
        self.current_location  = "Πάτρα"

    def get_profile_data(self):
        """UC1 — Returns all green profile data as a dictionary."""
        trees = self.total_recycling // 5
        water = self.total_recycling * 10
        return {
            "name":            self.name,
            "email":           self.email,
            "total_points":    self.total_points,
            "total_recycling": self.total_recycling,
            "badges":          self.badges,
            "challenges":      [c.title for c in self.challenges],
            "transactions":    self.transactions,
            "trees_saved":     trees,
            "water_saved":     water,
            "has_activity":    self.total_recycling > 0,
        }


class RecyclingBin:
    def __init__(self, bin_id, material_type, location, distance,
                 capacity, available_slots, real_time_available,
                 last_update, photos, reviews, bonus_points):
        self.bin_id              = bin_id
        self.material_type       = material_type
        self.location            = location
        self.distance            = distance
        self.capacity            = capacity
        self.available_slots     = available_slots
        self.real_time_available = real_time_available
        self.last_update         = last_update
        self.photos              = photos
        self.reviews             = reviews
        self.bonus_points        = bonus_points


class BinMap:
    def __init__(self):
        self.bins = []

    def add_bin(self, recycling_bin):
        self.bins.append(recycling_bin)

    def get_nearby_bins(self, user):
        """UC2 — Returns bins sorted by distance, or an error if GPS is off."""
        if not user.location_enabled:
            return {"error": "Παρακαλώ ενεργοποιήστε το GPS.", "bins": []}

        sorted_bins = sorted(self.bins, key=lambda b: b.distance)
        return {
            "location": user.current_location,
            "bins":     sorted_bins,
            "nearest":  sorted_bins[0] if sorted_bins else None,
        }


class BinDetailsSystem:
    def get_bin_details(self, recycling_bin):
        """UC3 — Returns full bin details as a dictionary."""
        if recycling_bin is None:
            return {"error": "Δεν βρέθηκε κάδος."}
        return {
            "bin_id":          recycling_bin.bin_id,
            "material_type":   recycling_bin.material_type,
            "location":        recycling_bin.location,
            "capacity":        recycling_bin.capacity,
            "available_slots": recycling_bin.available_slots if recycling_bin.real_time_available else None,
            "last_update":     recycling_bin.last_update,
            "real_time":       recycling_bin.real_time_available,
            "reviews":         recycling_bin.reviews,
            "bonus_points":    recycling_bin.bonus_points,
        }


# ======================================================
# UC4 — Material Recognition
# ======================================================

_RECYCLABLE_MATERIALS = {
    "πλαστικό": {
        "bin_type":    "Πλαστικό",
        "bin_color":   "Μπλε κάδος",
        "instructions":"Ξεπλύνετε τη συσκευασία και συμπιέστε το μπουκάλι.",
        "points":      10,
    },
    "χαρτί": {
        "bin_type":    "Χαρτί",
        "bin_color":   "Μπλε κάδος",
        "instructions":"Το χαρτί πρέπει να είναι καθαρό και στεγνό.",
        "points":      8,
    },
    "γυαλί": {
        "bin_type":    "Γυαλί",
        "bin_color":   "Κάδος γυαλιού",
        "instructions":"Ξεπλύνετε το γυάλινο μπουκάλι και αφαιρέστε το καπάκι.",
        "points":      12,
    },
    "αλουμίνιο": {
        "bin_type":    "Αλουμίνιο",
        "bin_color":   "Μπλε κάδος",
        "instructions":"Ξεπλύνετε το κουτάκι πριν τη ρίψη.",
        "points":      10,
    },
}

_SPECIAL_MATERIALS = {
    "μπαταρία", "μπαταρίες",
    "ηλεκτρονικό", "ηλεκτρονικά",
    "λάμπα", "λάμπες",
}


def scan_material(citizen_id, material):
    """
    UC4 — Identifies a material and returns instructions + nearby bins.
    Returns a dict with key 'status': 'recyclable' | 'special' | 'non_recyclable'.
    """
    material = material.lower().strip()

    if material in _RECYCLABLE_MATERIALS:
        info = _RECYCLABLE_MATERIALS[material]
        nearby_bins = []
        try:
            conn   = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT binID, materialType, location, status
                FROM   RecyclingBin
                WHERE  LOWER(materialType) = LOWER(%s)
                  AND  status = 'Λειτουργικός'
                """,
                (info["bin_type"],),
            )
            nearby_bins = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception:
            pass  # DB unavailable — still return instructions without bin list

        return {
            "status":      "recyclable",
            "material":    material,
            "bin_color":   info["bin_color"],
            "instructions":info["instructions"],
            "points":      info["points"],
            "nearby_bins": nearby_bins,
        }

    if material in _SPECIAL_MATERIALS:
        return {
            "status":  "special",
            "material":material,
            "message": "Το υλικό αυτό απαιτεί ειδική ανακύκλωση. Δεν πρέπει να ριφθεί στους κοινούς κάδους.",
            "extra":   "Χρησιμοποιήστε Ειδικά Σημεία Συλλογής (κάδοι ΣΕΔΙ).",
        }

    return {
        "status":  "non_recyclable",
        "material":material,
        "message": "Το υλικό αυτό δεν ανακυκλώνεται. Παρακαλώ ρίξτε το στους κοινούς κάδους.",
    }


# ======================================================
# UC5 — Points Redemption & Donation
# ======================================================

def redeem_points(citizen_id, reward_id):
    """
    UC5 — Redeems a reward using the citizen's points.
    Returns a dict with 'success' True/False and a 'message'.
    """
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT citizenID, totalPoints FROM Citizen WHERE citizenID = %s",
            (citizen_id,),
        )
        citizen = cursor.fetchone()
        if citizen is None:
            cursor.close(); conn.close()
            return {"success": False, "message": "Ο πολίτης δεν βρέθηκε."}

        cursor.execute(
            "SELECT rewardID, title, pointsRequired, description FROM Reward WHERE rewardID = %s",
            (reward_id,),
        )
        reward = cursor.fetchone()
        if reward is None:
            cursor.close(); conn.close()
            return {"success": False, "message": "Η επιβράβευση δεν βρέθηκε."}

        current_points  = citizen["totalPoints"]
        required_points = reward["pointsRequired"]

        if current_points < required_points:
            cursor.close(); conn.close()
            return {
                "success":  False,
                "message":  f"Ανεπαρκές υπόλοιπο. Χρειάζεστε ακόμα {required_points - current_points} πόντους.",
                "current":  current_points,
                "required": required_points,
            }

        new_total = current_points - required_points
        cursor.execute(
            "UPDATE Citizen SET totalPoints = %s WHERE citizenID = %s",
            (new_total, citizen_id),
        )
        conn.commit()

        cursor.execute(
            "SELECT title, pointsRequired FROM Reward WHERE pointsRequired <= %s",
            (new_total,),
        )
        other_available = cursor.fetchall()
        cursor.close(); conn.close()

        return {
            "success":          True,
            "message":          "Η εξαργύρωση ολοκληρώθηκε επιτυχώς!",
            "reward_title":     reward["title"],
            "reward_description":reward["description"],
            "new_total":        new_total,
            "other_available":  other_available,
        }

    except Exception as e:
        return {"success": False, "message": f"Σφάλμα βάσης δεδομένων: {e}"}


def donate_points(citizen_id, points, organization_name="Περιβαλλοντική Δράση"):
    """
    UC5 — Donates a number of points to an environmental organisation.
    Returns a dict with 'success' True/False and a 'message'.
    """
    if points <= 0:
        return {"success": False, "message": "Οι πόντοι πρέπει να είναι θετικός αριθμός."}

    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT citizenID, totalPoints FROM Citizen WHERE citizenID = %s",
            (citizen_id,),
        )
        citizen = cursor.fetchone()
        if citizen is None:
            cursor.close(); conn.close()
            return {"success": False, "message": "Ο πολίτης δεν βρέθηκε."}

        current_points = citizen["totalPoints"]
        if current_points < points:
            cursor.close(); conn.close()
            return {"success": False, "message": "Δεν έχετε αρκετούς πόντους για αυτή τη δωρεά."}

        new_total = current_points - points
        cursor.execute(
            "UPDATE Citizen SET totalPoints = %s WHERE citizenID = %s",
            (new_total, citizen_id),
        )
        conn.commit()
        cursor.close(); conn.close()

        return {
            "success":     True,
            "message":     f"Η δωρεά {points} πόντων στην «{organization_name}» ολοκληρώθηκε!",
            "certificate": "Εκδόθηκε Ψηφιακή Πιστοποίηση Πράσινης Προσφοράς BinGo.",
            "new_total":   new_total,
        }

    except Exception as e:
        return {"success": False, "message": f"Σφάλμα βάσης δεδομένων: {e}"}


# ======================================================
# UC6 — Activity Reward Points
# ======================================================

_ACTIVITIES = {
    "daily_login":       5,
    "correct_recycling": 15,
    "qr_scan":           20,
    "green_challenge":   30,
}


def add_reward_points(citizen_id, activity):
    """
    UC6 — Adds points for a completed activity.
    Returns a dict with 'success', 'earned', and 'new_total'.
    """
    if activity not in _ACTIVITIES:
        return {"success": False, "message": "Μη έγκυρη δραστηριότητα."}

    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT citizenID, totalPoints FROM Citizen WHERE citizenID = %s",
            (citizen_id,),
        )
        citizen = cursor.fetchone()
        if citizen is None:
            cursor.close(); conn.close()
            return {"success": False, "message": "Ο πολίτης δεν βρέθηκε."}

        earned    = _ACTIVITIES[activity]
        new_total = citizen["totalPoints"] + earned
        cursor.execute(
            "UPDATE Citizen SET totalPoints = %s WHERE citizenID = %s",
            (new_total, citizen_id),
        )
        conn.commit()
        cursor.close(); conn.close()

        return {
            "success":   True,
            "earned":    earned,
            "activity":  activity,
            "new_total": new_total,
        }

    except Exception as e:
        return {"success": False, "message": f"Σφάλμα βάσης δεδομένων: {e}"}


def qr_bin_reward(citizen_id, bin_id, gps_confirmed):
    """
    UC6 — Processes the QR-scan reward after GPS confirmation.
    Returns a dict with 'success' and details.
    """
    if not gps_confirmed:
        return {
            "success": False,
            "message": "Αποτυχία επιβεβαίωσης GPS. Δεν είστε κοντά στον κάδο!",
        }

    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT binID, location, status FROM RecyclingBin WHERE binID = %s",
            (bin_id,),
        )
        bin_data = cursor.fetchone()
        cursor.close(); conn.close()

        if bin_data is None:
            return {"success": False, "message": "Ο κωδικός QR δεν αντιστοιχεί σε έγκυρο κάδο."}

        if bin_data["status"] != "Λειτουργικός":
            return {
                "success": False,
                "message": f"Ο κάδος στην τοποθεσία {bin_data['location']} είναι εκτός λειτουργίας.",
            }

        reward_result = add_reward_points(citizen_id, "qr_scan")
        return {
            "success":       True,
            "location":      bin_data["location"],
            "message":       "Η ρίψη επιβεβαιώθηκε! Πόντοι πιστώθηκαν.",
            "points_result": reward_result,
        }

    except Exception as e:
        return {"success": False, "message": f"Σφάλμα βάσης δεδομένων: {e}"}


# ======================================================
# UC7 — Bin Evaluation
# ======================================================

BIN_MAP = {
    "200101": {"db_id": 1, "name": "Πλαστικό - Ψηλαλώνια (Πλατεία)"},
    "200102": {"db_id": 2, "name": "Χαρτί - Σκαγιοπούλειο"},
    "200103": {"db_id": 3, "name": "Γυαλί - Ζαρουχλέικα (Πλατεία Ταραμπούρα)"},
    "200104": {"db_id": 4, "name": "Αλουμίνιο - Κουκούλι (Έξω από το ΤΕΙ)"},
    "200105": {"db_id": 1, "name": "Πλαστικό - Νότιο Πάρκο"},
    "200106": {"db_id": 2, "name": "Χαρτί - Νοσοκομείο Άγιος Ανδρέας"},
    "400101": {"db_id": 1, "name": "Πλαστικό - Αγία Σοφία (Πλατεία)"},
    "400102": {"db_id": 2, "name": "Χαρτί - Έξω Παναγίτσα"},
    "400103": {"db_id": 4, "name": "Αλουμίνιο - Αγυιά (Γήπεδο Παναχαϊκής)"},
    "400104": {"db_id": 3, "name": "Γυαλί - Μποζαΐτικα"},
    "400105": {"db_id": 1, "name": "Πλαστικό - Καστελλόκαμπος (Στάση Προαστιακού)"},
    "400106": {"db_id": 2, "name": "Χαρτί - Ρίο (Νοσοκομείο / Πανεπιστήμιο)"},
    "600101": {"db_id": 2, "name": "Χαρτί - Πλατεία Γεωργίου (Κάτω Μέρος)"},
    "600102": {"db_id": 1, "name": "Πλαστικό - Πλατεία Όλγας"},
    "600103": {"db_id": 3, "name": "Γυαλί - Πεζόδρομος Τριών Ναυάρχων"},
    "600104": {"db_id": 4, "name": "Αλουμίνιο - Πεζόδρομος Ρήγα Φεραίου"},
    "600105": {"db_id": 1, "name": "Πλαστικό - Πλατεία Πινδάρου (Κάστρο)"},
    "600106": {"db_id": 2, "name": "Χαρτί - Μώλος Αγίου Νικολάου"},
}


def evaluate_bin(citizen_id, bin_code, rating, comment):
    """
    UC7 — Submits a review for a recycling point.
    Parameters come from the GUI (no input() calls).
    Returns a dict with 'success' and a 'message'.
    """
    if bin_code not in BIN_MAP:
        return {"success": False, "message": "Αυτός ο κωδικός κάδου δεν υπάρχει στο σύστημα."}

    if not (1 <= rating <= 5):
        return {"success": False, "message": "Η βαθμολογία πρέπει να είναι από 1 έως 5."}

    if len(comment) > 200:
        return {"success": False, "message": "Το σχόλιο ξεπερνάει το όριο των 200 χαρακτήρων."}

    actual_db_id = BIN_MAP[bin_code]["db_id"]
    bin_name     = BIN_MAP[bin_code]["name"]

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Review (citizenID, binID, rating, comment) VALUES (%s, %s, %s, %s)",
            (citizen_id, actual_db_id, rating, comment),
        )
        conn.commit()
        cursor.close(); conn.close()

        notify = rating <= 2
        return {
            "success":          True,
            "bin_name":         bin_name,
            "message":          f"Η κριτική σου για «{bin_name}» δημοσιεύτηκε επιτυχώς!",
            "notify_municipality": notify,
            "notify_message":   "Αποστολή ειδοποίησης στον Δήμο Πατρέων λόγω χαμηλής βαθμολογίας." if notify else "",
        }

    except Exception as e:
        return {"success": False, "message": f"Σφάλμα βάσης δεδομένων: {e}"}


# ======================================================
# UC9 — Eco Routing  (defined before UC8 so LOCAL_PAIRS can reference it)
# ======================================================

_ROUTE_POINTS = {
    "Κέντρο": {
        "Πλαστικό (Μπλε)":    "Πλατεία Ψηλαλωνίων",
        "Χαρτί (Μπλε)":       "Σκαγιοπούλειο",
        "Γυαλί (Κίτρινος)":   "Τριών Ναυάρχων",
        "Αλουμίνιο (Μπλε)":   "Ρήγα Φεραίου",
    },
    "Ρίο": {
        "Πλαστικό (Μπλε)":    "Πλατεία Αγίας Σοφίας",
        "Χαρτί (Μπλε)":       "Νοσοκομείο Ρίου",
        "Γυαλί (Κίτρινος)":   "Μποζαΐτικα",
        "Αλουμίνιο (Μπλε)":   "Κέντρο Ρίου",
    },
}


def plan_eco_route(citizen_id, user_input, context):
    """
    UC9 — Plans or advances a multi-stop recycling route.
    'context' is a dict held by the GUI between messages.
    Returns a plain string suitable for display in the chat window.
    """
    # --- Continue an active navigation ---
    if context.get("active_route"):
        if re.search(r"(ξεκινα|εφτασα|επόμενη|επομενη|ναι)", user_input, re.IGNORECASE):
            route = context["active_route"]
            step  = context["route_step"]
            if step < len(route):
                stop = route[step]
                context["route_step"] += 1
                return (
                    f"GPS: Προχώρα προς {stop['location']} "
                    f"για να πετάξεις {stop['material']}.\n"
                    "(Γράψε 'έφτασα' για την επόμενη στάση.)"
                )
            else:
                context["active_route"] = None
                context["route_step"]   = 0
                return "ΜΠΡΑΒΟ! Ολοκλήρωσες την Πράσινη Διαδρομή! Κέρδισες +50 Bonus Πόντους!"

        if re.search(r"(ακυρωση|σταματα|κλεισε)", user_input, re.IGNORECASE):
            context["active_route"] = None
            return "Η πλοήγηση ακυρώθηκε."

    # --- Plan a new route ---
    materials_found = []
    if re.search(r"(πλαστικ|μπουκαλι)",  user_input, re.IGNORECASE): materials_found.append("Πλαστικό (Μπλε)")
    if re.search(r"(χαρτι|κουτι)",        user_input, re.IGNORECASE): materials_found.append("Χαρτί (Μπλε)")
    if re.search(r"(γυαλι|μπουκαλα)",     user_input, re.IGNORECASE): materials_found.append("Γυαλί (Κίτρινος)")
    if re.search(r"(αλουμινι|κουτακι)",   user_input, re.IGNORECASE): materials_found.append("Αλουμίνιο (Μπλε)")

    area = None
    if re.search(r"(κεντρο|ψηλαλωνια|ολγας|γεωργιου)", user_input, re.IGNORECASE): area = "Κέντρο"
    elif re.search(r"(ριο|νοσοκομειο|αγια σοφια)",      user_input, re.IGNORECASE): area = "Ρίο"

    if len(materials_found) > 1 and area:
        stops = [
            {"material": m, "location": _ROUTE_POINTS.get(area, {}).get(m, "Κοντινός Κάδος")}
            for m in materials_found
        ]
        context["active_route"] = stops
        context["route_step"]   = 0
        lines = [f"Βρήκα διαδρομή για {area}:"]
        for i, s in enumerate(stops, 1):
            lines.append(f"  Στάση {i}: {s['location']} (για {s['material']})")
        lines.append("Γράψε 'ξεκινάμε' για να αρχίσουμε!")
        return "\n".join(lines)

    if len(materials_found) > 1:
        return "Βλέπω πολλά υλικά! Σε ποια περιοχή βρίσκεσαι για να φτιάξω το δρομολόγιο;"

    return (
        "Για δρομολόγιο πες μου τουλάχιστον 2 υλικά και την περιοχή σου.\n"
        "Παράδειγμα: «δρομολόγιο για χαρτί και γυαλί στο κέντρο»"
    )


# ======================================================
# UC8 — BinGo AI Chatbot
# ======================================================

# --- Quiz data ---
QUIZ_EASY = [
    {
        "question": "Τι χρώμα κάδο χρησιμοποιούμε για την ανακύκλωση συσκευασιών;",
        "options":  ["1) Μπλε", "2) Πράσινο"],
        "answer":   "1",
        "explanation": "Ο Μπλε κάδος είναι για τις συσκευασίες!",
    },
    {
        "question": "Πού πετάμε τις παλιές μπαταρίες;",
        "options":  ["1) Στον Μπλε κάδο", "2) Ειδικούς κάδους ΑΦΗΣ"],
        "answer":   "2",
        "explanation": "Οι μπαταρίες ανακυκλώνονται μόνο στην ΑΦΗΣ.",
    },
    {
        "question": "Τι κάνουμε τα πλαστικά μπουκάλια πριν τα πετάξουμε;",
        "options":  ["1) Τα γεμίζουμε με νερό", "2) Τα συμπιέζουμε"],
        "answer":   "2",
        "explanation": "Η συμπίεση εξοικονομεί τεράστιο χώρο!",
    },
    {
        "question": "Επιτρέπονται οργανικά σκουπίδια (αποφάγια) στον Μπλε Κάδο;",
        "options":  ["1) Ναι", "2) Όχι"],
        "answer":   "2",
        "explanation": "Τα αποφάγια καταστρέφουν την ανακύκλωση.",
    },
]

QUIZ_HARD = [
    {
        "question": "Τι ανακυκλώνεται άπειρες φορές χωρίς να χάσει ΚΑΘΟΛΟΥ την ποιότητά του;",
        "options":  ["1) Χαρτί", "2) Πλαστικό", "3) Γυαλί"],
        "answer":   "3",
        "explanation": "Το γυαλί μπορεί να ανακυκλωθεί άπειρες φορές!",
    },
    {
        "question": "Πού πετάμε το λαδωμένο κουτί από πίτσα;",
        "options":  ["1) Μπλε κάδο", "2) Πράσινο κάδο (σύμμικτα)"],
        "answer":   "2",
        "explanation": "Τα λάδια καταστρέφουν το χαρτί. Πάει στα σύμμικτα!",
    },
    {
        "question": "Μπορούμε να πετάξουμε καθρέφτες στον Μπλε Κάδο;",
        "options":  ["1) Ναι", "2) Όχι"],
        "answer":   "2",
        "explanation": "Οι καθρέφτες έχουν άλλη θερμοκρασία τήξης από τα μπουκάλια.",
    },
    {
        "question": "Πώς πρέπει να ρίχνουμε τα υλικά στον Μπλε Κάδο;",
        "options":  ["1) Μέσα σε δεμένη σακούλα", "2) Χύμα και άδεια"],
        "answer":   "2",
        "explanation": "Πρέπει να πέφτουν χύμα για εύκολο διαχωρισμό.",
    },
    {
        "question": "Ποιο υλικό χρειάζεται την περισσότερη ενέργεια για να φτιαχτεί από την αρχή;",
        "options":  ["1) Αλουμίνιο", "2) Χαρτί", "3) Γυαλί"],
        "answer":   "1",
        "explanation": "Η ανακύκλωση αλουμινίου σώζει το 95% της ενέργειας παραγωγής του!",
    },
]


def check_quiz_answer(citizen_id, phase, index, answer, context):
    """
    UC8 Quiz — Checks a single quiz answer.
    phase: 'easy' or 'hard'
    index: 0-based question index
    Returns a dict with 'correct', 'explanation', 'finished', and optional 'coupon'.
    """
    questions = QUIZ_EASY if phase == "easy" else QUIZ_HARD
    if index >= len(questions):
        return {"correct": False, "explanation": "Άκυρο ερώτηση.", "finished": True}

    q       = questions[index]
    correct = answer.strip() == q["answer"]

    if not correct:
        pts = 100 if phase == "easy" else 0
        if pts > 0:
            _award_quiz_points(citizen_id, pts)
        return {
            "correct":     False,
            "explanation": q["explanation"],
            "finished":    True,
            "points_awarded": pts,
            "message": f"Λάθος! {q['explanation']} " + (f"Κέρδισες {pts} πόντους από το Επίπεδο 1." if pts else ""),
        }

    is_last = (index == len(questions) - 1)
    if is_last and phase == "hard":
        coupon = f"BINGO-{random.randint(10000, 99999)}"
        _award_quiz_points(citizen_id, 1200)
        return {
            "correct":        True,
            "explanation":    q["explanation"],
            "finished":       True,
            "coupon":         coupon,
            "points_awarded": 1200,
            "message":        f"Σωστά! Κέρδισες 1200 πόντους και κουπόνι 3€! Κωδικός: {coupon}",
        }

    if is_last and phase == "easy":
        _award_quiz_points(citizen_id, 100)
        return {
            "correct":        True,
            "explanation":    q["explanation"],
            "finished":       False,
            "advance_phase":  "hard",
            "points_awarded": 100,
            "message":        f"Σωστά! {q['explanation']} Προχωράς στο Επίπεδο 2!",
        }

    return {
        "correct":     True,
        "explanation": q["explanation"],
        "finished":    False,
        "message":     f"Σωστά! {q['explanation']}",
    }


def _award_quiz_points(citizen_id, points):
    """Internal helper — adds quiz points to the DB silently."""
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Citizen SET totalPoints = COALESCE(totalPoints, 0) + %s WHERE citizenID = %s",
            (points, citizen_id),
        )
        conn.commit()
        cursor.close(); conn.close()
    except Exception:
        pass


# --- Chatbot helpers ---
def _greeting(citizen_id, user_input, context):
    options = [
        "Γεια σου! Είμαι ο ψηφιακός σου βοηθός BinGo. Πώς μπορώ να σε βοηθήσω;",
        "Καλησπέρα! Είμαι γεμάτος πράσινη ενέργεια. Τι θα κάνουμε;",
    ]
    return random.choice(options)


def _get_live_eco_news(citizen_id, user_input, context):
    try:
        url = (
            "https://news.google.com/rss/search"
            "?q=%CE%B1%CE%BD%CE%B1%CE%BA%CF%8D%CE%BA%CE%BB%CF%89%CF%83%CE%B7"
            "&hl=el&gl=GR&ceid=GR:el"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
        root      = ET.fromstring(xml_data)
        news_list = []
        for item in root.findall(".//item")[:3]:
            title       = item.find("title").text
            clean_title = title.rsplit(" - ", 1)[0]
            news_list.append("• " + clean_title)
        news_list.append(
            "\n📅 ΔΡΑΣΗ ΔΗΜΟΥ ΠΑΤΡΕΩΝ: Αυτή την Κυριακή, εθελοντικός καθαρισμός στο Νότιο Πάρκο!"
        )
        return "LIVE ΔΡΑΣΕΙΣ:\n" + "\n".join(news_list)
    except Exception:
        return "Δεν έχω σύνδεση αυτή τη στιγμή για να φέρω τις τελευταίες δράσεις."


def _handle_bins_request(citizen_id, user_input, context):
    material = None
    area     = None

    if re.search(r"(πλαστικ|μπουκαλι|πλαστικό|μπουκάλι)", user_input, re.IGNORECASE):
        material = "Πλαστικό (Μπλε Κάδος)"
    elif re.search(r"(χαρτι|κουτι|χαρτί|κουτί)", user_input, re.IGNORECASE):
        material = "Χαρτί (Μπλε Κάδος)"
    elif re.search(r"(γυαλι|γυαλί|μπουκαλα|μπουκάλα)", user_input, re.IGNORECASE):
        material = "Γυαλί (Κίτρινος Κάδος)"
    elif re.search(r"(αλουμινι|αλουμίνιο|κουτακι|κουτάκι)", user_input, re.IGNORECASE):
        material = "Αλουμίνιο (Μπλε Κάδος)"

    if re.search(r"(κεντρο|κέντρο|ψηλαλωνια)", user_input, re.IGNORECASE):   area = "Κέντρο"
    elif re.search(r"(ριο|ρίο|νοσοκομειο)",    user_input, re.IGNORECASE):   area = "Ρίο"
    elif re.search(r"(τει|κουκουλι)",           user_input, re.IGNORECASE):   area = "ΤΕΙ"

    if material: context["last_material"] = material
    if area:     context["last_area"]     = area

    saved_mat  = context.get("last_material")
    saved_area = context.get("last_area")

    _bins_db = {
        "Πλαστικό (Μπλε Κάδος)": {
            "Κέντρο": "Πλατεία Ψηλαλωνίων",
            "Ρίο":    "Πλατεία Αγίας Σοφίας",
            "ΤΕΙ":   "Έξω από το ΤΕΙ (Κουκούλι)",
        },
        "Χαρτί (Μπλε Κάδος)": {
            "Κέντρο": "Σκαγιοπούλειο",
            "Ρίο":    "Νοσοκομείο Ρίου",
            "ΤΕΙ":   "Κεντρική Βιβλιοθήκη ΤΕΙ",
        },
        "Γυαλί (Κίτρινος Κάδος)": {
            "Κέντρο": "Πεζόδρομος Τριών Ναυάρχων",
            "Ρίο":    "Μποζαΐτικα",
            "ΤΕΙ":   "Κυλικείο ΤΕΙ",
        },
        "Αλουμίνιο (Μπλε Κάδος)": {
            "Κέντρο": "Ρήγα Φεραίου",
            "Ρίο":    "Κέντρο Ρίου",
            "ΤΕΙ":   "Κλειστό Γυμναστήριο (Ταρταράς)",
        },
    }

    if saved_mat and saved_area:
        location = _bins_db.get(saved_mat, {}).get(saved_area, None)
        context["last_material"] = None
        context["last_area"]     = None
        if location:
            return f"Για {saved_mat} στο {saved_area}: {location}"
        return f"Δεν βρήκα κάδο για {saved_mat} στο {saved_area}."

    if saved_mat:
        return f"Θέλεις να πετάξεις {saved_mat}. Σε ποια περιοχή βρίσκεσαι;"
    if saved_area:
        return f"Είσαι στο {saved_area}. Τι υλικό θέλεις να πετάξεις;"
    return "Τι υλικό θέλεις να πετάξεις και πού βρίσκεσαι;"


# LOCAL_PAIRS — ordered from most specific to most general
_LOCAL_PAIRS = [
    (r".*(γεια|καλημερα|καλημέρα|hello).*",                                              _greeting),
    (r".*(νεα|νέα|ειδησεις|ειδήσεις|δρασεις|δράσεις).*",                                _get_live_eco_news),
    (r".*(διαδρομη|διαδρομή|δρομολογιο|δρομολόγιο|πολλαπλα|ξεκινα|εφτασα|ακυρωση).*", plan_eco_route),
    (r".*(καδ|κάδ|πετα|πετά|γυαλι|γυαλί|χαρτι|χαρτί|πλαστικ|αλουμινι|κεντρο|ριο|τει).*", _handle_bins_request),
]


def get_bot_response(citizen_id, user_input, context):
    """
    UC8 — Returns the chatbot's text response for a single message.
    The GUI calls this once per message; 'context' is kept alive between calls.
    """
    for pattern, action in _LOCAL_PAIRS:
        if re.match(pattern, user_input, re.IGNORECASE):
            return action(citizen_id, user_input, context)
    return "Μπορείς να με ρωτήσεις για κάδους, δράσεις ή δρομολόγιο!"


# ======================================================
# UC10 — Green Challenges
# ======================================================

def join_green_challenge(citizen_id, goal_description, badge_reward, days_limit=7):
    """UC10 — Creates a new green challenge for a citizen."""
    time_limit = datetime.now() + timedelta(days=days_limit)
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO GreenChallenge (goal, timeLimit, badgeToUnlock, citizenID) VALUES (%s, %s, %s, %s)",
            (goal_description, time_limit, badge_reward, citizen_id),
        )
        conn.commit()
        generated_id = cursor.lastrowid
        cursor.close(); conn.close()
        return {
            "success":      True,
            "challenge_id": generated_id,
            "message":      f"Η πρόκληση δημιουργήθηκε με ID: {generated_id}",
        }
    except Exception as e:
        return {"success": False, "message": f"Σφάλμα: {e}"}


def complete_green_challenge(challenge_id):
    """UC10 — Marks a challenge as complete and awards 50 points."""
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM GreenChallenge WHERE challengeID = %s",
            (challenge_id,),
        )
        challenge = cursor.fetchone()
        if challenge is None:
            cursor.close(); conn.close()
            return {"success": False, "message": "Δεν βρέθηκε η πρόκληση."}

        cursor.execute(
            "UPDATE Citizen SET totalPoints = totalPoints + 50 WHERE citizenID = %s",
            (challenge["citizenID"],),
        )
        conn.commit()
        cursor.close(); conn.close()
        return {"success": True, "message": "Η πρόκληση ολοκληρώθηκε! +50 πόντοι προστέθηκαν."}
    except Exception as e:
        return {"success": False, "message": f"Σφάλμα: {e}"}


# ======================================================
# UC11 — Collection & Damage Reporting
# ======================================================

def complete_collection(employee_id, bin_id):
    """UC11 — Resets a bin's fill level to 0 after collection."""
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE RecyclingBin SET fillLevel = 0 WHERE binID = %s",
            (bin_id,),
        )
        conn.commit()
        cursor.close(); conn.close()
        return {"success": True, "message": f"Η αποκομιδή του κάδου {bin_id} ολοκληρώθηκε."}
    except Exception as e:
        return {"success": False, "message": f"Σφάλμα: {e}"}


def report_bin_damage(employee_id, bin_id):
    """UC11 — Marks a bin as out of service."""
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE RecyclingBin SET status = 'Εκτός Λειτουργίας' WHERE binID = %s",
            (bin_id,),
        )
        conn.commit()
        cursor.close(); conn.close()
        return {"success": True, "message": f"Ο κάδος {bin_id} δηλώθηκε εκτός λειτουργίας."}
    except Exception as e:
        return {"success": False, "message": f"Σφάλμα: {e}"}


# ======================================================
# UC12 — Environmental Actions
# ======================================================

def publish_environmental_action(employee_id, title):
    """UC12 — Publishes a new environmental action (stub; add DB table if needed)."""
    return {"success": True, "message": f"Δημοσιεύτηκε νέα δράση: «{title}»"}
