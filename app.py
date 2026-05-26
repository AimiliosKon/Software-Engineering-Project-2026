# ============================================================
# BinGo — app.py  |  Τελική Έκδοση v3
# Εκτέλεση: py -3.12 app.py
# ============================================================

import customtkinter as ctk
from tkinter import messagebox
import webbrowser, random
from datetime import datetime, date

import logic
from logic import (
    Citizen, GreenChallenge, RecyclingBin, BinMap, BinDetailsSystem,
    scan_material, redeem_points, donate_points, add_reward_points,
    evaluate_bin, get_bot_response,
    join_green_challenge, complete_green_challenge,
    complete_collection, report_bin_damage, publish_environmental_action,
    plan_eco_route, BIN_MAP, qr_bin_reward,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

BG      = "#0F1117"
PANEL   = "#1A1D27"
CARD    = "#21253A"
ACCENT  = "#00E5A0"
ACCENT2 = "#0EA5E9"
DANGER  = "#FF4D6D"
WARNING = "#F59E0B"
TEXT    = "#F0F4FF"
SUBTEXT = "#8B92B3"
BORDER  = "#2D3154"

# ══════════════════════════════════════════════════════════
# SESSION — παρακολούθηση ενεργειών (αντί για DB)
# ══════════════════════════════════════════════════════════
SESSION = {
    "points":            1500,
    "daily_login_date":  None,   # date — μόνο 1 φορά/ημέρα
    "last_scan_time":    None,   # datetime
    "last_scan_bin":     None,   # κωδικός κάδου
    "last_scan_material":None,   # υλικό
    "last_qr_bins":      set(),  # κάδοι που σαρώθηκαν σήμερα
    "scans_today":       0,
}
CITIZEN_ID = 1

def session_add_points(amount, reason):
    SESSION["points"] += amount
    return SESSION["points"]

# ── Demo δεδομένα ─────────────────────────────────────────
CITIZEN = Citizen("Κατερίνα Πετροπούλου","katerina@gmail.com",1500,25,["Eco Starter 🥉","Green Hero 🥇"])
CITIZEN.challenges   = [GreenChallenge("Recycle 10 πλαστικά μπουκάλια")]
CITIZEN.transactions = [
    ("Σάρωση QR κάδου",       "+20"),
    ("Σωστή ανακύκλωση",      "+15"),
    ("Εξαργύρωση κουπονιού",  "-100"),
    ("Καθημερινή σύνδεση",    "+5"),
]

_BIN_MAP     = BinMap()
_BIN_DETAILS = BinDetailsSystem()
for _b in [
    RecyclingBin(1,"Πλαστικό",  "Πλ. Γεωργίου",    250,"100L",4,True, "22/05/2026",[],["Καθαρό","Εύκολη πρόσβαση"],20),
    RecyclingBin(2,"Χαρτί",     "Αγίου Ανδρέου",    500,"120L",3,True, "22/05/2026",[],["Καλή κατάσταση"],15),
    RecyclingBin(3,"Γυαλί",     "Ρήγα Φεραίου",     800,"80L", 2,False,"20/05/2026",[],["Λίγο μακριά"],10),
    RecyclingBin(4,"Αλουμίνιο","Πλ. Ψηλαλωνίων",   400,"90L", 5,True, "22/05/2026",[],["Πολύ καθαρό"],12),
]:
    _BIN_MAP.add_bin(_b)

LEADERBOARD = [
    {"rank":1, "name":"Νίκος Παπαδόπουλος","points":4850,"recycled":"62 kg","badge":"🏆"},
    {"rank":2, "name":"Μαρία Κωνσταντίνου", "points":4200,"recycled":"55 kg","badge":"🥈"},
    {"rank":3, "name":"Γιώργης Αντωνίου",   "points":3780,"recycled":"48 kg","badge":"🥉"},
    {"rank":4, "name":"Κατερίνα Πετροπούλου",       "points":1500,"recycled":"25 kg","badge":"🌿"},
    {"rank":5, "name":"Ελένη Δημητρίου",     "points":1380,"recycled":"22 kg","badge":"🌿"},
    {"rank":6, "name":"Κώστας Σταματίου",    "points":1150,"recycled":"18 kg","badge":"🌱"},
    {"rank":7, "name":"Σοφία Παπανικολάου",  "points":980, "recycled":"15 kg","badge":"🌱"},
    {"rank":8, "name":"Δημήτρης Καρράς",     "points":760, "recycled":"12 kg","badge":"🌱"},
    {"rank":9, "name":"Άννα Μιχαλοπούλου",  "points":540, "recycled":"8 kg", "badge":"🌱"},
    {"rank":10,"name":"Πέτρος Λαζαρίδης",   "points":320, "recycled":"5 kg", "badge":"🌱"},
]

BOT_CTX    = {}
QUIZ_STATE = {"active":False,"index":0}
ALL_QUIZ = [
    {"q":"Τι χρώμα κάδο χρησιμοποιούμε για συσκευασίες;","opts":["1) Μπλε","2) Πράσινο"],"a":"1","exp":"Ο Μπλε κάδος είναι για τις συσκευασίες!"},
    {"q":"Πού πετάμε τις παλιές μπαταρίες;","opts":["1) Μπλε κάδο","2) Ειδικούς κάδους ΑΦΗΣ"],"a":"2","exp":"Μόνο στην ΑΦΗΣ!"},
    {"q":"Τι κάνουμε τα πλαστικά μπουκάλια πριν τα πετάξουμε;","opts":["1) Τα γεμίζουμε","2) Τα συμπιέζουμε"],"a":"2","exp":"Η συμπίεση εξοικονομεί χώρο!"},
    {"q":"Επιτρέπονται αποφάγια στον Μπλε Κάδο;","opts":["1) Ναι","2) Όχι"],"a":"2","exp":"Καταστρέφουν την ανακύκλωση."},
    {"q":"Ποιο υλικό ανακυκλώνεται άπειρες φορές χωρίς απώλεια ποιότητας;","opts":["1) Χαρτί","2) Πλαστικό","3) Γυαλί"],"a":"3","exp":"Το γυαλί ανακυκλώνεται άπειρες φορές!"},
    {"q":"Πού πετάμε το λαδωμένο κουτί πίτσας;","opts":["1) Μπλε κάδο","2) Σύμμικτα"],"a":"2","exp":"Τα λάδια καταστρέφουν το χαρτί."},
    {"q":"Πόσα χρόνια χρειάζεται το πλαστικό να αποσυντεθεί;","opts":["1) 10","2) 50","3) 450"],"a":"3","exp":"Έως 450 χρόνια!"},
    {"q":"Πόσο εξοικονομεί η ανακύκλωση αλουμινίου σε ενέργεια;","opts":["1) 30%","2) 60%","3) 95%"],"a":"3","exp":"95% εξοικονόμηση ενέργειας!"},
    {"q":"Τι κάνουμε με τα σκουπίδια τροφίμων;","opts":["1) Μπλε κάδος","2) Καφέ κάδος κομπόστ"],"a":"2","exp":"Στον κάδο οργανικών!"},
    {"q":"Πόσα λίτρα νερό σώζει η ανακύκλωση 1kg χαρτιού;","opts":["1) 10","2) 30","3) 100"],"a":"3","exp":"~100 λίτρα νερό!"},
    {"q":"Πώς ρίχνουμε τα υλικά στον Μπλε Κάδο;","opts":["1) Σε δεμένη σακούλα","2) Χύμα και άδεια"],"a":"2","exp":"Χύμα για εύκολο διαχωρισμό."},
    {"q":"Μπορούμε να πετάξουμε καθρέφτες στον Μπλε Κάδο;","opts":["1) Ναι","2) Όχι"],"a":"2","exp":"Διαφορετική θερμοκρασία τήξης."},
    {"q":"Ποιο υλικό χρειάζεται τη μεγαλύτερη ενέργεια να παραχθεί από την αρχή;","opts":["1) Αλουμίνιο","2) Χαρτί","3) Γυαλί"],"a":"1","exp":"Το αλουμίνιο χρειάζεται τεράστια ενέργεια!"},
]

ECO_TIPS = [
    "💡 Η ανακύκλωση ενός αλουμινίου εξοικονομεί αρκετή ενέργεια για 3 ώρες τηλεόρασης!",
    "🌊 Κάθε χρόνο 8 εκατ. τόνοι πλαστικού καταλήγουν στους ωκεανούς. Ανακύκλωσε!",
    "🌳 Η ανακύκλωση 1 τόνου χαρτιού σώζει 17 δέντρα και 26.000 λίτρα νερού.",
    "⚡ Ένα ανακυκλωμένο γυάλινο μπουκάλι εξοικονομεί αρκετή ενέργεια για 4 ώρες φωτισμού.",
    "🐢 Το πλαστικό χρειάζεται 450 χρόνια για να αποσυντεθεί. Κάθε σου επιλογή μετράει!",
]

PATRAS_BINS = [
    {"mat":"♻️ Πλαστικό","loc":"Πλατεία Γεωργίου","area":"Κέντρο","code":"600101","dist":"250m"},
    {"mat":"📄 Χαρτί",   "loc":"Αγίου Ανδρέου 45","area":"Κέντρο","code":"600102","dist":"480m"},
    {"mat":"🍶 Γυαλί",   "loc":"Ρήγα Φεραίου",    "area":"Κέντρο","code":"600103","dist":"800m"},
    {"mat":"🥫 Αλουμίνιο","loc":"Πλ. Ψηλαλωνίων", "area":"Κέντρο","code":"600104","dist":"400m"},
    {"mat":"♻️ Πλαστικό","loc":"Πλ. Αγίας Σοφίας", "area":"Ρίο",   "code":"400101","dist":"2.1km"},
    {"mat":"📄 Χαρτί",   "loc":"Νοσοκομείο Ρίου",  "area":"Ρίο",   "code":"400102","dist":"2.4km"},
]

# ── Widget helpers ────────────────────────────────────────
def _dk(h):
    h=h.lstrip("#"); r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    return f"#{max(0,r-30):02x}{max(0,g-30):02x}{max(0,b-30):02x}"

def card(parent,**kw):
    return ctk.CTkFrame(parent,fg_color=CARD,corner_radius=14,
                        border_width=1,border_color=BORDER,**kw)

def lbl(parent,text,size=13,weight="normal",color=TEXT,**kw):
    return ctk.CTkLabel(parent,text=text,
                        font=ctk.CTkFont(size=size,weight=weight),
                        text_color=color,**kw)

def btn(parent,text,command,color=ACCENT,tc="#0F1117",h=38,**kw):
    return ctk.CTkButton(parent,text=text,command=command,
                         fg_color=color,hover_color=_dk(color),
                         text_color=tc,height=h,corner_radius=10,
                         font=ctk.CTkFont(size=13,weight="bold"),**kw)

def inp(parent,ph,**kw):
    return ctk.CTkEntry(parent,placeholder_text=ph,
                        fg_color=BG,border_color=BORDER,
                        text_color=TEXT,placeholder_text_color=SUBTEXT,
                        font=ctk.CTkFont(size=13),**kw)

def sec(parent,text):
    lbl(parent,text,size=11,color=SUBTEXT).pack(anchor="w",padx=2,pady=(18,6))

def stat_card(parent,value,label_text,color=ACCENT):
    f=card(parent); f.pack(side="left",expand=True,fill="x",padx=5)
    lbl(f,value,size=26,weight="bold",color=color).pack(pady=(18,2))
    lbl(f,label_text,size=11,color=SUBTEXT).pack(pady=(0,16))
    return f


# ╔══════════════════════════════════════════════════════════╗
# ║                   MAIN APP                               ║
# ╚══════════════════════════════════════════════════════════╝

class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.title("BinGo — Σύνδεση")
        self.geometry("440x680")
        self.configure(fg_color=PANEL)
        self.resizable(False, False)
        # self.grab_set()  # Not needed for CTk
        self.on_success = on_success
        self._mode = "login"  # "login" ή "register"
        self._build()

    def _build(self):
        for w in self.winfo_children(): w.destroy()

        lbl(self, "🌿", size=44).pack(pady=(32, 4))
        lbl(self, "BinGo", size=26, weight="bold", color=ACCENT).pack()
        lbl(self, "Έξυπνη Ανακύκλωση · Πάτρα",
            size=11, color=SUBTEXT).pack(pady=(2, 24))

        # Tabs
        tab_f = ctk.CTkFrame(self, fg_color=CARD, corner_radius=10)
        tab_f.pack(fill="x", padx=40, pady=(0, 20))
        tab_r = ctk.CTkFrame(tab_f, fg_color="transparent")
        tab_r.pack(fill="x", padx=6, pady=6)

        def set_mode(m):
            self._mode = m
            self._build()

        login_color  = ACCENT  if self._mode == "login"    else CARD
        login_tc     = "#0F1117" if self._mode == "login"  else SUBTEXT
        reg_color    = ACCENT  if self._mode == "register" else CARD
        reg_tc       = "#0F1117" if self._mode == "register" else SUBTEXT

        ctk.CTkButton(tab_r, text="Σύνδεση", fg_color=login_color,
                      text_color=login_tc, hover_color=_dk(login_color),
                      height=34, corner_radius=8,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=lambda: set_mode("login")).pack(side="left", expand=True, fill="x", padx=2)
        ctk.CTkButton(tab_r, text="Εγγραφή", fg_color=reg_color,
                      text_color=reg_tc, hover_color=_dk(reg_color),
                      height=34, corner_radius=8,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=lambda: set_mode("register")).pack(side="left", expand=True, fill="x", padx=2)

        p = ctk.CTkFrame(self, fg_color="transparent")
        p.pack(fill="x", padx=40)

        self.err_lbl = lbl(p, "", size=12, color=DANGER)

        if self._mode == "login":
            lbl(p, "Email", size=12, color=SUBTEXT).pack(anchor="w", pady=(0,4))
            self.email_e = inp(p, "katerina@gmail.com", height=42)
            self.email_e.pack(fill="x", pady=(0,12))
            self.email_e.insert(0, "katerina@gmail.com")

            lbl(p, "Κωδικός", size=12, color=SUBTEXT).pack(anchor="w", pady=(0,4))
            self.pass_e = inp(p, "••••••••", height=42, show="•")
            self.pass_e.pack(fill="x", pady=(0,6))
            self.pass_e.insert(0, "bingo2026")

            self.err_lbl.pack(anchor="w", pady=(0,12))

            btn(p, "Σύνδεση →", self._login,
                color=ACCENT, tc="#0F1117", h=44).pack(fill="x")

            # Διαχωριστής
            div = ctk.CTkFrame(p, fg_color="transparent")
            div.pack(fill="x", pady=(16, 0))
            ctk.CTkFrame(div, fg_color=BORDER, height=1).pack(
                side="left", fill="x", expand=True, pady=8)
            lbl(div, "  ή  ", size=11, color=SUBTEXT).pack(side="left")
            ctk.CTkFrame(div, fg_color=BORDER, height=1).pack(
                side="left", fill="x", expand=True, pady=8)

            btn(p, "🚀 Δοκιμαστική Είσοδος (Guest)",
                self._guest_login,
                color=CARD, tc=ACCENT, h=42).pack(fill="x", pady=(12, 0))

            lbl(p, "Demo: katerina@gmail.com / bingo2026",
                size=10, color=SUBTEXT).pack(pady=(12, 0))

            self.pass_e.bind("<Return>", lambda e: self._login())

        else:  # register
            for ph, attr in [
                ("Ονοματεπώνυμο", "name_e"),
                ("Email",         "reg_email_e"),
            ]:
                lbl(p, ph, size=12, color=SUBTEXT).pack(anchor="w", pady=(0,4))
                e = inp(p, ph, height=42)
                e.pack(fill="x", pady=(0,12))
                setattr(self, attr, e)

            lbl(p, "Κωδικός", size=12, color=SUBTEXT).pack(anchor="w", pady=(0,4))
            self.reg_pass_e = inp(p, "Τουλάχιστον 6 χαρακτήρες",
                                  height=42, show="•")
            self.reg_pass_e.pack(fill="x", pady=(0,12))

            lbl(p, "Επανάληψη Κωδικού", size=12, color=SUBTEXT).pack(anchor="w", pady=(0,4))
            self.reg_pass2_e = inp(p, "Επανάληψη", height=42, show="•")
            self.reg_pass2_e.pack(fill="x", pady=(0,6))

            self.err_lbl.pack(anchor="w", pady=(0,12))

            btn(p, "Δημιουργία Λογαριασμού →", self._show_register,
                color=ACCENT, tc="#0F1117", h=44).pack(fill="x")

    def _login(self):
        email = self.email_e.get().strip()
        pwd   = self.pass_e.get().strip()
        if email == "katerina@gmail.com" and pwd == "bingo2026":
            self.destroy()
            self.on_success("Κατερίνα")
        else:
            self.err_lbl.configure(text="❌ Λάθος email ή κωδικός.")

    def _guest_login(self):
        self.destroy()
        self.on_success("Guest")

    def _show_register(self):
        name  = self.name_e.get().strip()
        email = self.reg_email_e.get().strip()
        pwd   = self.reg_pass_e.get().strip()
        pwd2  = self.reg_pass2_e.get().strip()

        if not name or not email:
            self.err_lbl.configure(text="❌ Συμπλήρωσε όλα τα πεδία."); return
        if "@" not in email:
            self.err_lbl.configure(text="❌ Μη έγκυρο email."); return
        if len(pwd) < 6:
            self.err_lbl.configure(text="❌ Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες."); return
        if pwd != pwd2:
            self.err_lbl.configure(text="❌ Οι κωδικοί δεν ταιριάζουν."); return

        self.destroy()
        self.on_success(name.split()[0])
class BinGoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BinGo")
        self.geometry("1100x700")
        self.minsize(900,600)
        self.configure(fg_color=BG)
        self._nav_btns = {}
        self._pts_labels = []   # labels που δείχνουν πόντους — ενημερώνονται live
        self._build_layout()
        self._nav("dashboard")

    # ── Sidebar ──────────────────────────────────────────────
    def _build_layout(self):
        rail=ctk.CTkFrame(self,width=220,fg_color=PANEL,corner_radius=0)
        rail.pack(side="left",fill="y"); rail.pack_propagate(False)

        logo=ctk.CTkFrame(rail,fg_color="transparent")
        logo.pack(fill="x",padx=24,pady=(32,28))
        lbl(logo,"🌿",size=28).pack(side="left")
        lbl(logo,"BinGo",size=20,weight="bold",color=ACCENT).pack(side="left",padx=8)

        items=[
            ("🏠","Αρχική",          "dashboard"),
            ("👤","Προφίλ",          "profile"),
            ("🗺️","Χάρτης Κάδων",    "map"),
            ("📦","Σάρωση Υλικού",   "scan"),
            ("🎁","Πόντοι & Δωρεά",  "rewards"),
            ("⭐","Αξιολόγηση",      "evaluate"),
            ("🤖","BinGo AI",         "chat"),
            ("🏆","Προκλήσεις",      "challenges"),
            ("🏅","Leaderboard",     "leaderboard"),
            ("🚛","Υπάλληλος",       "employee"),
        ]
        for icon,name,key in items:
            f=ctk.CTkFrame(rail,fg_color="transparent",corner_radius=10)
            f.pack(fill="x",padx=12,pady=2)
            inner=ctk.CTkFrame(f,fg_color="transparent",corner_radius=10)
            inner.pack(fill="x")
            ic=lbl(inner,icon,size=15); ic.pack(side="left",padx=(14,8),pady=11)
            nm=lbl(inner,name,size=13,color=SUBTEXT); nm.pack(side="left")
            self._nav_btns[key]=(inner,nm,ic)
            for w in [f,inner,ic,nm]:
                w.bind("<Button-1>",lambda e,k=key:self._nav(k))

        ctk.CTkFrame(rail,fg_color=BORDER,height=1).pack(fill="x",padx=16,pady=(20,16))

        # User badge με live πόντοι
        ub=ctk.CTkFrame(rail,fg_color="transparent"); ub.pack(fill="x",padx=16,pady=(0,20))
        av=ctk.CTkFrame(ub,fg_color=ACCENT,width=36,height=36,corner_radius=18)
        av.pack(side="left"); av.pack_propagate(False)
        lbl(av,"Α",size=14,weight="bold",color="#0F1117").place(relx=.5,rely=.5,anchor="center")
        info=ctk.CTkFrame(ub,fg_color="transparent"); info.pack(side="left",padx=10)
        lbl(info,"Κατερίνα",size=12,weight="bold").pack(anchor="w")
        pts_lbl=lbl(info,f"{SESSION['points']} π. · Green Hero",size=10,color=ACCENT)
        pts_lbl.pack(anchor="w")
        self._pts_labels.append(pts_lbl)

        self.content=ctk.CTkScrollableFrame(self,fg_color=BG,scrollbar_button_color=BORDER)
        self.content.pack(side="left",fill="both",expand=True)

    def _nav(self,key):
        for k,(inner,nm,ic) in self._nav_btns.items():
            if k==key: inner.configure(fg_color=CARD);  nm.configure(text_color=ACCENT);  ic.configure(text_color=ACCENT)
            else:      inner.configure(fg_color="transparent"); nm.configure(text_color=SUBTEXT); ic.configure(text_color=SUBTEXT)
        self._clear()
        {"dashboard":self._dashboard,"profile":self._profile,"map":self._map,
         "scan":self._scan,"rewards":self._rewards,"evaluate":self._evaluate,
         "chat":self._chat,"challenges":self._challenges,
         "leaderboard":self._leaderboard,"employee":self._employee}[key]()

    def _clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def _header(self,title,sub):
        f=ctk.CTkFrame(self.content,fg_color="transparent"); f.pack(fill="x",padx=32,pady=(28,4))
        lbl(f,title,size=24,weight="bold").pack(anchor="w")
        lbl(f,sub,size=12,color=SUBTEXT).pack(anchor="w",pady=(2,0))
        ctk.CTkFrame(self.content,fg_color=BORDER,height=1).pack(fill="x",padx=32,pady=(12,0))

    def _refresh_pts(self):
        """Ανανεώνει όλα τα labels που δείχνουν πόντους."""
        for l in self._pts_labels:
            try: l.configure(text=f"{SESSION['points']} π. · Green Hero")
            except Exception: pass

    # ══════════════════════════════════════════════════════════
    # ΑΡΧΙΚΗ — Dashboard
    # ══════════════════════════════════════════════════════════
    def _dashboard(self):
        self._clear()
        now = datetime.now()

        # Χαιρετισμός
        hour = now.hour
        greet = "Καλημέρα" if hour<12 else ("Καλησπέρα" if hour<18 else "Καληνύχτα")
        f=ctk.CTkFrame(self.content,fg_color="transparent"); f.pack(fill="x",padx=32,pady=(28,0))
        lbl(f,f"{greet}, Κατερίνα! 🌿",size=24,weight="bold").pack(anchor="w")
        months = ["","Ιανουαρίου","Φεβρουαρίου","Μαρτίου","Απριλίου",
                  "Μαΐου","Ιουνίου","Ιουλίου","Αυγούστου","Σεπτεμβρίου",
                  "Οκτωβρίου","Νοεμβρίου","Δεκεμβρίου"]
        date_str = f"{now.day} {months[now.month]} {now.year}  ·  Πάτρα, Ελλάδα"
        lbl(f, date_str, size=12, color=SUBTEXT).pack(anchor="w", pady=(2,0))

        # Mini stats
        sf=ctk.CTkFrame(self.content,fg_color="transparent"); sf.pack(fill="x",padx=32,pady=(20,0))
        for val,label,col in [
            (f"{SESSION['points']}","Πράσινοι Πόντοι",ACCENT),
            ("25 kg","Ανακύκλωση",TEXT),
            ("5","Δέντρα σώθηκαν","#4ADE80"),
            (f"{SESSION['scans_today']}","Σαρώσεις σήμερα",ACCENT2),
        ]:
            c=card(sf); c.pack(side="left",expand=True,fill="x",padx=5)
            lbl(c,val,size=22,weight="bold",color=col).pack(pady=(16,2))
            lbl(c,label,size=11,color=SUBTEXT).pack(pady=(0,14))

        cols=ctk.CTkFrame(self.content,fg_color="transparent"); cols.pack(fill="x",padx=32,pady=(20,0))

        # Αριστερά: Eco tip + τελευταία σάρωση
        left=ctk.CTkFrame(cols,fg_color="transparent"); left.pack(side="left",fill="both",expand=True,padx=(0,10))

        sec(left,"ΗΜΕΡΗΣΙΟ ECO TIP")
        tip_card=card(left); tip_card.pack(fill="x")
        tp=ctk.CTkFrame(tip_card,fg_color="transparent"); tp.pack(fill="x",padx=16,pady=16)
        tip=random.choice(ECO_TIPS)
        lbl(tp,tip,size=13,color=TEXT,wraplength=340).pack(anchor="w")

        sec(left,"ΤΕΛΕΥΤΑΙΑ ΣΑΡΩΣΗ")
        scan_card=card(left); scan_card.pack(fill="x")
        sp=ctk.CTkFrame(scan_card,fg_color="transparent"); sp.pack(fill="x",padx=16,pady=16)
        if SESSION["last_scan_time"]:
            t=SESSION["last_scan_time"].strftime("%d/%m/%Y  %H:%M")
            lbl(sp,f"🕐 {t}",size=13,color=ACCENT).pack(anchor="w")
            lbl(sp,f"📦 Υλικό: {SESSION['last_scan_material']}",size=12,color=TEXT).pack(anchor="w",pady=2)
            lbl(sp,f"📍 Κάδος: {SESSION['last_scan_bin']}",size=12,color=TEXT).pack(anchor="w")
        else:
            lbl(sp,"Δεν έχεις κάνει σάρωση ακόμα.",size=13,color=SUBTEXT).pack(anchor="w")
            btn(sp,"▶ Πήγαινε στη Σάρωση",lambda:self._nav("scan"),
                color=ACCENT,tc="#0F1117",h=34).pack(anchor="w",pady=(10,0))

        # Δεξιά: Κάδοι Πάτρας
        right=ctk.CTkFrame(cols,fg_color="transparent"); right.pack(side="left",fill="both",expand=True,padx=(10,0))
        sec(right,"ΚΑΔΟΙ ΑΝΑΚΥΚΛΩΣΗΣ — ΠΑΤΡΑ")
        map_card=card(right); map_card.pack(fill="x")
        mp=ctk.CTkFrame(map_card,fg_color="transparent"); mp.pack(fill="x",padx=4,pady=8)

        for b in PATRAS_BINS:
            row=ctk.CTkFrame(mp,fg_color="transparent"); row.pack(fill="x",padx=12,pady=4)
            ic_f=ctk.CTkFrame(row,fg_color="#1A3D32",width=32,height=32,corner_radius=16)
            ic_f.pack(side="left"); ic_f.pack_propagate(False)
            lbl(ic_f,b["mat"].split()[0],size=13).place(relx=.5,rely=.5,anchor="center")
            info=ctk.CTkFrame(row,fg_color="transparent"); info.pack(side="left",padx=10,fill="x",expand=True)
            lbl(info,b["loc"],size=12,weight="bold").pack(anchor="w")
            lbl(info,f"{b['area']}  ·  Κωδ: {b['code']}",size=10,color=SUBTEXT).pack(anchor="w")
            lbl(row,b["dist"],size=11,color=ACCENT).pack(side="right",padx=4)
            ctk.CTkFrame(mp,fg_color=BORDER,height=1).pack(fill="x",padx=12)

        btn(map_card,"🗺️ Άνοιξε στο Google Maps",
            lambda:webbrowser.open("https://www.google.com/maps/search/κάδοι+ανακύκλωσης+Πάτρα/@38.2466,21.7346,14z"),
            color=ACCENT2,tc=TEXT,h=34).pack(padx=16,pady=(8,14),fill="x")

    # ══════════════════════════════════════════════════════════
    # UC1 — Προφίλ
    # ══════════════════════════════════════════════════════════
    def _profile(self):
        self._header("Πράσινο Προφίλ","Περίπτωση Χρήσης 1")
        data=CITIZEN.get_profile_data()

        sf=ctk.CTkFrame(self.content,fg_color="transparent"); sf.pack(fill="x",padx=32,pady=(20,0))
        for val,label,col in [
            (str(SESSION["points"]),"Πράσινοι Πόντοι",ACCENT),
            (f"{data['total_recycling']} kg","Ανακύκλωση",TEXT),
            (str(data["trees_saved"]),"Δέντρα σώθηκαν","#4ADE80"),
            (f"{data['water_saved']} L","Εξοικ. Νερό",ACCENT2),
        ]:
            c=card(sf); c.pack(side="left",expand=True,fill="x",padx=5)
            lbl(c,val,size=22,weight="bold",color=col).pack(pady=(18,2))
            lbl(c,label,size=11,color=SUBTEXT).pack(pady=(0,16))

        cols=ctk.CTkFrame(self.content,fg_color="transparent"); cols.pack(fill="x",padx=32,pady=(20,0))
        left=ctk.CTkFrame(cols,fg_color="transparent"); left.pack(side="left",fill="both",expand=True,padx=(0,10))

        sec(left,"ΕΜΒΛΗΜΑΤΑ")
        bc=card(left); bc.pack(fill="x")
        bf=ctk.CTkFrame(bc,fg_color="transparent"); bf.pack(anchor="w",padx=16,pady=14)
        for b in data["badges"]:
            pill=ctk.CTkFrame(bf,fg_color=CARD,corner_radius=20,border_width=1,border_color=ACCENT)
            pill.pack(side="left",padx=4)
            lbl(pill,b,size=12,weight="bold",color=ACCENT).pack(padx=14,pady=6)

        sec(left,"ΕΝΕΡΓΕΣ ΠΡΟΚΛΗΣΕΙΣ")
        cc=card(left); cc.pack(fill="x")
        for ch in data["challenges"] or ["Καμία ενεργή πρόκληση."]:
            r=ctk.CTkFrame(cc,fg_color="transparent"); r.pack(fill="x",padx=16,pady=8)
            ctk.CTkFrame(r,fg_color=ACCENT,width=4,corner_radius=2).pack(side="left",fill="y",padx=(0,10))
            lbl(r,ch,size=13).pack(side="left")

        right=ctk.CTkFrame(cols,fg_color="transparent"); right.pack(side="left",fill="both",expand=True,padx=(10,0))
        sec(right,"ΠΡΟΣΦΑΤΕΣ ΣΥΝΑΛΛΑΓΕΣ")
        tc=card(right); tc.pack(fill="x")
        for desc,pts in CITIZEN.transactions:
            r=ctk.CTkFrame(tc,fg_color="transparent"); r.pack(fill="x",padx=16,pady=10)
            lbl(r,desc,size=13).pack(side="left")
            lbl(r,f"{pts} π.",size=13,weight="bold",color=ACCENT if "+" in pts else DANGER).pack(side="right")
            ctk.CTkFrame(tc,fg_color=BORDER,height=1).pack(fill="x",padx=16)

    # ══════════════════════════════════════════════════════════
    # UC2/3 — Χάρτης
    # ══════════════════════════════════════════════════════════
    def _map(self):
        self._header("Χάρτης Κάδων Ανακύκλωσης","Περιπτώσεις Χρήσης 2 & 3")
        gps=ctk.CTkFrame(self.content,fg_color=CARD,corner_radius=12,border_width=1,border_color=ACCENT)
        gps.pack(fill="x",padx=32,pady=(20,0))
        gr=ctk.CTkFrame(gps,fg_color="transparent"); gr.pack(fill="x",padx=18,pady=14)
        lbl(gr,"📡  GPS Ενεργό  ·  Πάτρα, Ελλάδα",size=13,color=ACCENT).pack(side="left")
        btn(gr,"🗺️ Google Maps",
            lambda:webbrowser.open("https://www.google.com/maps/search/κάδοι+ανακύκλωσης+Πάτρα/@38.2466,21.7346,14z"),
            color=ACCENT2,tc=TEXT,h=34).pack(side="right")

        result=_BIN_MAP.get_nearby_bins(CITIZEN)
        sec(self.content,f"  {len(result['bins'])} ΚΟΝΤΙΝΟΙ ΚΑΔΟΙ")
        for b in result["bins"]:
            c=card(self.content); c.pack(fill="x",padx=32,pady=6)
            row=ctk.CTkFrame(c,fg_color="transparent"); row.pack(fill="x",padx=18,pady=14)
            ic=ctk.CTkFrame(row,fg_color="#1A3D35",width=48,height=48,corner_radius=24)
            ic.pack(side="left"); ic.pack_propagate(False)
            lbl(ic,{"Πλαστικό":"🔵","Χαρτί":"📄","Γυαλί":"🍶","Αλουμίνιο":"🥫"}.get(b.material_type,"♻️"),size=20).place(relx=.5,rely=.5,anchor="center")
            info=ctk.CTkFrame(row,fg_color="transparent"); info.pack(side="left",padx=16,fill="x",expand=True)
            lbl(info,b.material_type,size=15,weight="bold").pack(anchor="w")
            lbl(info,f"📍 {b.location}",size=12,color=SUBTEXT).pack(anchor="w")
            rr=ctk.CTkFrame(row,fg_color="transparent"); rr.pack(side="right")
            lbl(rr,f"{b.distance} m",size=18,weight="bold",color=ACCENT).pack(anchor="e")
            if b.real_time_available: lbl(rr,f"✅ {b.available_slots} θέσεις",size=11,color="#4ADE80").pack(anchor="e")
            lbl(rr,f"+{b.bonus_points} π.",size=11,color=ACCENT).pack(anchor="e",pady=(4,0))
            btn(c,"Λεπτομέρειες →",lambda rb=b:self._bin_popup(rb),color=PANEL,tc=ACCENT,h=32).pack(anchor="e",padx=18,pady=(0,14))

    def _bin_popup(self,rb):
        d=_BIN_DETAILS.get_bin_details(rb)
        win=ctk.CTkToplevel(self); win.title(f"Κάδος — {d['material_type']}")
        win.geometry("460x420"); win.configure(fg_color=PANEL); win.grab_set()
        lbl(win,f"Κάδος {d['material_type']}",size=18,weight="bold").pack(padx=28,pady=(24,4),anchor="w")
        lbl(win,d["location"],size=12,color=SUBTEXT).pack(padx=28,anchor="w")
        ctk.CTkFrame(win,fg_color=BORDER,height=1).pack(fill="x",padx=24,pady=16)
        for lb,val,col in [("Χωρητικότητα",d["capacity"],TEXT),("Bonus Πόντοι",f"+{d['bonus_points']} π.",ACCENT),("Real-time","Ναι" if d["real_time"] else "Όχι",ACCENT2)]:
            r=ctk.CTkFrame(win,fg_color=CARD,corner_radius=10); r.pack(fill="x",padx=24,pady=4)
            rr=ctk.CTkFrame(r,fg_color="transparent"); rr.pack(fill="x",padx=14,pady=10)
            lbl(rr,lb,size=13,color=SUBTEXT).pack(side="left"); lbl(rr,val,size=13,weight="bold",color=col).pack(side="right")
        lbl(win,"Κριτικές",size=12,color=SUBTEXT).pack(padx=28,pady=(16,4),anchor="w")
        for rev in (d["reviews"] or ["Καμία κριτική ακόμα."]):
            lbl(win,f"★ {rev}",size=12).pack(anchor="w",padx=28,pady=2)
        btn(win,"Κλείσιμο",win.destroy,color=CARD,tc=SUBTEXT,h=36).pack(padx=24,pady=20,fill="x")

    # ══════════════════════════════════════════════════════════
    # UC4 — Σάρωση + Κάμερα  (με πλήρη καταγραφή)
    # ══════════════════════════════════════════════════════════
    def _scan(self):
        self._header("Σάρωση & Αναγνώριση Υλικού","Περίπτωση Χρήσης 4")

        c=card(self.content); c.pack(fill="x",padx=32,pady=(20,0))
        p=ctk.CTkFrame(c,fg_color="transparent"); p.pack(fill="x",padx=20,pady=20)

        # Κωδικός κάδου — ΥΠΟΧΡΕΩΤΙΚΟ
        lbl(p,"Κωδικός Κάδου (υποχρεωτικό)",size=12,color=SUBTEXT).pack(anchor="w",pady=(0,6))
        bin_codes = list(BIN_MAP.keys())
        bin_var = ctk.StringVar(value=bin_codes[0])
        ctk.CTkOptionMenu(p,values=bin_codes,variable=bin_var,
                          fg_color=CARD,button_color=ACCENT,
                          button_hover_color=_dk(ACCENT),text_color=TEXT,
                          dropdown_fg_color=PANEL,
                          font=ctk.CTkFont(size=12)).pack(fill="x",pady=(0,14))

        lbl(p,"Υλικό προς ανακύκλωση",size=12,color=SUBTEXT).pack(anchor="w",pady=(0,6))
        mat_var=ctk.StringVar(value="πλαστικό")
        ctk.CTkOptionMenu(p,values=["πλαστικό","χαρτί","γυαλί","αλουμίνιο","μπαταρία","άγνωστο"],
                          variable=mat_var,fg_color=CARD,button_color=ACCENT,
                          button_hover_color=_dk(ACCENT),text_color=TEXT,
                          dropdown_fg_color=PANEL,
                          font=ctk.CTkFont(size=13)).pack(fill="x",pady=(0,16))

        br=ctk.CTkFrame(p,fg_color="transparent"); br.pack(fill="x")
        rf=ctk.CTkFrame(self.content,fg_color="transparent"); rf.pack(fill="x",padx=32)

        # Τελευταία σάρωση (live)
        last_c=card(self.content); last_c.pack(fill="x",padx=32,pady=(12,0))
        lp=ctk.CTkFrame(last_c,fg_color="transparent"); lp.pack(fill="x",padx=16,pady=12)
        lbl(lp,"ΤΕΛΕΥΤΑΙΑ ΣΑΡΩΣΗ",size=11,color=SUBTEXT).pack(anchor="w",pady=(0,6))
        last_lbl=lbl(lp,"Καμία σάρωση ακόμα.",size=13,color=SUBTEXT)
        last_lbl.pack(anchor="w")

        def _update_last(mat,code):
            SESSION["last_scan_time"]    = datetime.now()
            SESSION["last_scan_material"]= mat
            SESSION["last_scan_bin"]     = code
            SESSION["scans_today"]      += 1
            t=SESSION["last_scan_time"].strftime("%d/%m/%Y  %H:%M")
            last_lbl.configure(
                text=f"🕐 {t}   📦 {mat}   📍 Κάδος {code}",
                text_color=ACCENT)

        def do_scan():
            for w in rf.winfo_children(): w.destroy()
            code=bin_var.get(); mat=mat_var.get()
            res=scan_material(CITIZEN_ID,mat)
            c2=card(rf); c2.pack(fill="x",pady=(12,0))
            inner=ctk.CTkFrame(c2,fg_color="transparent"); inner.pack(fill="x",padx=20,pady=16)

            if res["status"]=="recyclable":
                lbl(inner,"✅  Ανακυκλώσιμο υλικό",size=15,weight="bold",color=ACCENT).pack(anchor="w",pady=(0,12))
                for lt,val in [("Υλικό",res["material"]),("Κάδος",res["bin_color"]),
                               ("Οδηγίες",res["instructions"]),("Πόντοι",f"+{res['points']} π.")]:
                    r=ctk.CTkFrame(inner,fg_color=BG,corner_radius=8); r.pack(fill="x",pady=3)
                    rr=ctk.CTkFrame(r,fg_color="transparent"); rr.pack(fill="x",padx=12,pady=8)
                    lbl(rr,lt,size=12,color=SUBTEXT).pack(side="left")
                    lbl(rr,val,size=12,weight="bold",color=ACCENT if lt=="Πόντοι" else TEXT).pack(side="right")
                # Πιστώνω πόντους + καταγραφή
                new_total=session_add_points(res["points"],"scan")
                _update_last(mat,code)
                self._refresh_pts()
                lbl(inner,f"✅ Πιστώθηκαν +{res['points']} π.  |  Σύνολο: {new_total} π.",
                    size=13,weight="bold",color=ACCENT).pack(anchor="w",pady=(12,0))

            elif res["status"]=="special":
                lbl(inner,"⚠️  Ειδική Ανακύκλωση",size=15,weight="bold",color=WARNING).pack(anchor="w",pady=(0,8))
                lbl(inner,res["message"],size=13,wraplength=600).pack(anchor="w")
                _update_last(mat,code)

            else:
                lbl(inner,"🚫  Μη Ανακυκλώσιμο",size=15,weight="bold",color=DANGER).pack(anchor="w",pady=(0,8))
                lbl(inner,res["message"],size=13).pack(anchor="w")
                _update_last(mat,code)

        def open_camera():
            try:
                import cv2
                from PIL import Image,ImageTk
                cw=ctk.CTkToplevel(self); cw.title("BinGo · Σάρωση με Κάμερα")
                cw.geometry("700x580"); cw.configure(fg_color=PANEL)
                cw.grab_set(); cw.resizable(False,False)
                lbl(cw,"📷  Σάρωση Υλικού",size=16,weight="bold").pack(pady=(20,4))
                lbl(cw,f"Κάδος: {bin_var.get()}  ·  Υλικό: {mat_var.get()}",
                    size=12,color=ACCENT).pack(pady=(0,8))
                vid=ctk.CTkLabel(cw,text=""); vid.pack()
                status=lbl(cw,"🟢 Κάμερα ενεργή — πάτα 📸 για αναγνώριση",size=12,color=ACCENT)
                status.pack(pady=6)
                cap=cv2.VideoCapture(0); running=[True]
                def upd():
                    if not running[0]: return
                    ok,frame=cap.read()
                    if ok:
                        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                        img=Image.fromarray(rgb).resize((660,400))
                        imgtk=ImageTk.PhotoImage(image=img)
                        vid.imgtk=imgtk; vid.configure(image=imgtk)
                    cw.after(30,upd)
                def capture():
                    mat=mat_var.get(); code=bin_var.get()
                    res=scan_material(CITIZEN_ID,mat)
                    if res["status"]=="recyclable":
                        new_total=session_add_points(res["points"],"camera_scan")
                        _update_last(mat,code)
                        self._refresh_pts()
                        status.configure(
                            text=f"✅ {mat} → {res['bin_color']}  |  +{res['points']} π.  |  Σύνολο: {new_total} π.",
                            text_color=ACCENT)
                    else:
                        status.configure(text=f"⚠️ {res.get('message','Δοκίμασε ξανά.')}",text_color=WARNING)
                def on_close():
                    running[0]=False; cap.release(); cw.destroy()
                bf=ctk.CTkFrame(cw,fg_color="transparent"); bf.pack(pady=8)
                btn(bf,"📸 Αναγνώριση & Πίστωση",capture,color=ACCENT,tc="#0F1117",h=36).pack(side="left",padx=8)
                btn(bf,"Κλείσιμο",on_close,color=DANGER,tc=TEXT,h=36).pack(side="left",padx=8)
                cw.protocol("WM_DELETE_WINDOW",on_close); upd()
            except ImportError:
                messagebox.showerror("Λείπει βιβλιοθήκη","Τρέξε:\npy -3.12 -m pip install opencv-python")
            except Exception as e:
                messagebox.showerror("Σφάλμα κάμερας",str(e))

        btn(br,"▶  Αναγνώριση & Πίστωση",do_scan,color=ACCENT,tc="#0F1117",h=40).pack(side="left",expand=True,padx=(0,8))
        btn(br,"📷  Άνοιγμα Κάμερας",open_camera,color=ACCENT2,tc=TEXT,h=40).pack(side="left",expand=True,padx=(8,0))

    # ══════════════════════════════════════════════════════════
    # UC5/6 — Πόντοι (με σωστή επαλήθευση)
    # ══════════════════════════════════════════════════════════
    def _rewards(self):
        self._header("Πόντοι, Εξαργύρωση & Δωρεά","Περιπτώσεις Χρήσης 5 & 6")

        # Live πόντοι banner
        pb=ctk.CTkFrame(self.content,fg_color=CARD,corner_radius=12,
                         border_width=1,border_color=ACCENT)
        pb.pack(fill="x",padx=32,pady=(20,0))
        pbr=ctk.CTkFrame(pb,fg_color="transparent"); pbr.pack(fill="x",padx=20,pady=16)
        lbl(pbr,"💰 Τρέχον Υπόλοιπο",size=12,color=SUBTEXT).pack(side="left")
        pts_live=lbl(pbr,f"{SESSION['points']} π.",size=20,weight="bold",color=ACCENT)
        pts_live.pack(side="right")
        self._pts_labels.append(pts_live)

        # Ενημερωτικό
        info=ctk.CTkFrame(self.content,fg_color=CARD,corner_radius=12,
                           border_width=1,border_color=ACCENT2)
        info.pack(fill="x",padx=32,pady=(12,0))
        ip=ctk.CTkFrame(info,fg_color="transparent"); ip.pack(fill="x",padx=16,pady=12)
        lbl(ip,"ℹ️  Πώς κερδίζεις πόντους",size=13,weight="bold",color=ACCENT2).pack(anchor="w")
        for t in ["🔵 Καθημερινή σύνδεση → +5 π. (1 φορά/ημέρα, μόνο εδώ)",
                  "📦 Σάρωση υλικού → +15 π. (μόνο μέσω οθόνης Σάρωσης)",
                  "📷 QR Κάδου → +20 π. (χρειάζεται κωδικός + GPS)",
                  "🏆 Ολοκλήρωση πρόκλησης → +30 π. (μέσω Προκλήσεις)"]:
            lbl(ip,t,size=12,color=SUBTEXT).pack(anchor="w",pady=1)

        cols=ctk.CTkFrame(self.content,fg_color="transparent"); cols.pack(fill="x",padx=32,pady=(16,0))

        # Αριστερά
        lc=ctk.CTkFrame(cols,fg_color="transparent"); lc.pack(side="left",fill="both",expand=True,padx=(0,8))

        # Daily login
        sec(lc,"ΚΑΘΗΜΕΡΙΝΗ ΣΥΝΔΕΣΗ  (ΠΧ6)")
        c1=card(lc); c1.pack(fill="x")
        p1=ctk.CTkFrame(c1,fg_color="transparent"); p1.pack(fill="x",padx=16,pady=16)
        lbl(p1,"1 φορά ημερησίως · +5 πόντοι",size=12,color=SUBTEXT).pack(anchor="w",pady=(0,10))
        dl=lbl(p1,"",size=12); dl.pack(anchor="w",pady=(0,8))
        def do_daily():
            today=date.today()
            if SESSION["daily_login_date"]==today:
                dl.configure(text="⚠️ Έχεις ήδη κάνει σύνδεση σήμερα.",text_color=WARNING); return
            SESSION["daily_login_date"]=today
            new_total=session_add_points(5,"daily_login")
            self._refresh_pts()
            dl.configure(text=f"✅ +5 π. πιστώθηκαν!  Νέο σύνολο: {new_total} π.",text_color=ACCENT)
        btn(p1,"✅ Καθημερινή Σύνδεση",do_daily,h=38).pack(fill="x")

        # QR Scan
        sec(lc,"ΣΑΡΩΣΗ QR ΚΑΔΟΥ  (ΠΧ6)")
        c2=card(lc); c2.pack(fill="x")
        p2=ctk.CTkFrame(c2,fg_color="transparent"); p2.pack(fill="x",padx=16,pady=16)
        lbl(p2,"Επίλεξε κωδικό κάδου + GPS επιβεβαίωση → +20 π.",size=12,color=SUBTEXT,wraplength=280).pack(anchor="w",pady=(0,8))
        qr_codes=list(BIN_MAP.keys())
        qr_var=ctk.StringVar(value=qr_codes[0])
        ctk.CTkOptionMenu(p2,values=qr_codes,variable=qr_var,
                          fg_color=CARD,button_color=ACCENT,text_color=TEXT,
                          dropdown_fg_color=PANEL,
                          font=ctk.CTkFont(size=12)).pack(fill="x",pady=(0,8))
        gps_v=ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(p2,text="✅ GPS: Επιβεβαίωση τοποθεσίας",variable=gps_v,
                        text_color=TEXT,fg_color=ACCENT,hover_color=_dk(ACCENT),
                        font=ctk.CTkFont(size=12)).pack(anchor="w",pady=(0,10))
        ql=lbl(p2,"",size=12); ql.pack(anchor="w",pady=(0,8))
        def do_qr():
            code=qr_var.get()
            if not gps_v.get():
                ql.configure(text="❌ Ενεργοποίησε πρώτα το GPS.",text_color=DANGER); return
            if code in SESSION["last_qr_bins"]:
                ql.configure(text=f"⚠️ Έχεις ήδη σαρώσει τον κάδο {code} σήμερα.",text_color=WARNING); return
            SESSION["last_qr_bins"].add(code)
            new_total=session_add_points(20,"qr_scan")
            self._refresh_pts()
            ql.configure(text=f"✅ QR επιβεβαιώθηκε! +20 π.  |  Σύνολο: {new_total} π.",text_color=ACCENT)
        btn(p2,"📷 Επιβεβαίωση QR",do_qr,h=38).pack(fill="x")

        # Δεξιά — εξαργύρωση
        rc=ctk.CTkFrame(cols,fg_color="transparent"); rc.pack(side="left",fill="both",expand=True,padx=(8,0))
        sec(rc,"ΕΞΑΡΓΥΡΩΣΗ ΑΝΤΑΜΟΙΒΗΣ  (ΠΧ5)")
        c3=card(rc); c3.pack(fill="x")
        p3=ctk.CTkFrame(c3,fg_color="transparent"); p3.pack(fill="x",padx=16,pady=16)
        lbl(p3,"ID Ανταμοιβής",size=12,color=SUBTEXT).pack(anchor="w",pady=(0,6))
        re_e=inp(p3,"πχ. 1"); re_e.pack(fill="x",pady=(0,10))
        rel=lbl(p3,"",size=12,wraplength=280); rel.pack(anchor="w",pady=(0,8))
        def do_redeem():
            try: rid=int(re_e.get())
            except ValueError:
                rel.configure(text="❌ Βάλε αριθμό.",text_color=DANGER); return
            r=redeem_points(CITIZEN_ID,rid)
            if r["success"]:
                cost=r.get("reward_description","")
                rel.configure(text=f"✅ {r['message']}\nΝέο υπόλοιπο: {r.get('new_total','')} π.",text_color=ACCENT)
            else:
                rel.configure(text=f"❌ {r['message']}",text_color=DANGER)
        btn(p3,"Εξαργύρωση",do_redeem,h=38).pack(fill="x")

        # Δωρεά
        sec(self.content,"  ΔΩΡΕΑ ΠΟΝΤΩΝ  (ΠΧ5)")
        dc=card(self.content); dc.pack(fill="x",padx=32)
        dp=ctk.CTkFrame(dc,fg_color="transparent"); dp.pack(fill="x",padx=16,pady=16)
        dr=ctk.CTkFrame(dp,fg_color="transparent"); dr.pack(fill="x")
        org_e=inp(dr,"Όνομα οργανισμού"); org_e.pack(side="left",fill="x",expand=True,padx=(0,10))
        pts_e=inp(dr,"Αριθμός πόντων",width=160); pts_e.pack(side="left")
        don_l=lbl(dp,"",size=12); don_l.pack(anchor="w",pady=(10,8))
        def do_donate():
            try: pts=int(pts_e.get())
            except ValueError:
                don_l.configure(text="❌ Βάλε αριθμό.",text_color=DANGER); return
            if pts<=0:
                don_l.configure(text="❌ Οι πόντοι πρέπει να είναι θετικοί.",text_color=DANGER); return
            if pts>SESSION["points"]:
                don_l.configure(text=f"❌ Δεν έχεις αρκετούς πόντους. Διαθέσιμοι: {SESSION['points']} π.",text_color=DANGER); return
            org=org_e.get().strip() or "Περιβαλλοντική Δράση"
            session_add_points(-pts,"donate")
            self._refresh_pts()
            don_l.configure(text=f"✅ Δώρισες {pts} π. στην «{org}»!  Νέο σύνολο: {SESSION['points']} π.",text_color=ACCENT)
        btn(dp,"Αποστολή Δωρεάς",do_donate,h=38).pack(fill="x")

    # ══════════════════════════════════════════════════════════
    # UC7 — Αξιολόγηση
    # ══════════════════════════════════════════════════════════
    def _evaluate(self):
        self._header("Αξιολόγηση Κάδου","Περίπτωση Χρήσης 7")
        c=card(self.content); c.pack(fill="x",padx=32,pady=(20,0))
        p=ctk.CTkFrame(c,fg_color="transparent"); p.pack(fill="x",padx=20,pady=20)
        lbl(p,"Κωδικός Κάδου",size=12,color=SUBTEXT).pack(anchor="w",pady=(0,6))
        bv=ctk.StringVar(value=list(BIN_MAP.keys())[0])
        ctk.CTkOptionMenu(p,values=list(BIN_MAP.keys()),variable=bv,
                          fg_color=CARD,button_color=ACCENT,text_color=TEXT,
                          dropdown_fg_color=PANEL,font=ctk.CTkFont(size=12)).pack(fill="x",pady=(0,14))
        lbl(p,"Βαθμολογία",size=12,color=SUBTEXT).pack(anchor="w",pady=(0,4))
        sf=ctk.CTkFrame(p,fg_color="transparent"); sf.pack(anchor="w",pady=(0,14))
        rv=ctk.IntVar(value=5); sbs=[]
        def set_r(n):
            rv.set(n)
            for i,sb in enumerate(sbs): sb.configure(text_color=WARNING if i<n else SUBTEXT)
        for i in range(1,6):
            sb=lbl(sf,"★",size=24,color=WARNING); sb.pack(side="left",padx=2)
            sb.bind("<Button-1>",lambda e,n=i:set_r(n)); sbs.append(sb)
        lbl(p,"Σχόλιο (έως 200 χαρ.)",size=12,color=SUBTEXT).pack(anchor="w",pady=(0,6))
        cb=ctk.CTkTextbox(p,height=80,fg_color=BG,border_color=BORDER,text_color=TEXT,font=ctk.CTkFont(size=13))
        cb.pack(fill="x",pady=(0,14))
        rl=lbl(p,"",size=13,wraplength=700); rl.pack(anchor="w",pady=(0,10))
        def do_ev():
            r=evaluate_bin(CITIZEN_ID,bv.get(),rv.get(),cb.get("1.0","end").strip())
            msg=(f"✅ {r['message']}"+(f"\n⚠️ {r['notify_message']}" if r.get("notify_municipality") else "")) if r["success"] else f"❌ {r['message']}"
            rl.configure(text=msg,text_color=ACCENT if r["success"] else DANGER)
        btn(p,"Υποβολή Αξιολόγησης",do_ev,h=40).pack(fill="x")

    # ══════════════════════════════════════════════════════════
    # UC8/9 — BinGo AI
    # ══════════════════════════════════════════════════════════
    def _chat(self):
        self._header("BinGo AI — Ψηφιακός Βοηθός","Περιπτώσεις Χρήσης 8 & 9")
        self._chat_box=ctk.CTkTextbox(self.content,height=340,fg_color=CARD,text_color=TEXT,
                                       font=ctk.CTkFont(size=13),state="disabled",wrap="word",
                                       border_width=1,border_color=BORDER,corner_radius=14)
        self._chat_box.pack(fill="x",padx=32,pady=(20,0))
        self._bot_say("Γεια! Είμαι ο BinGo AI 🌱\n"
                      "• «κάδοι γυαλιού κέντρο» → βρίσκω κοντινούς κάδους\n"
                      "• «δράσεις» → τελευταία νέα ανακύκλωσης\n"
                      "• «gps» ή «δρομολόγιο για χαρτί και γυαλί στο κέντρο» → GPS πλοήγηση\n"
                      "• «κουίζ» → παιχνίδι γνώσεων με 13 ερωτήσεις")
        qf=ctk.CTkFrame(self.content,fg_color="transparent"); qf.pack(fill="x",padx=32,pady=(10,0))
        for chip in ["κάδοι γυαλιού κέντρο","δράσεις","gps","κουίζ"]:
            ctk.CTkButton(qf,text=chip,height=30,fg_color=CARD,text_color=ACCENT,
                          hover_color=BORDER,corner_radius=20,border_width=1,border_color=ACCENT,
                          font=ctk.CTkFont(size=11),command=lambda t=chip:self._send(t)).pack(side="left",padx=4)
        inf=ctk.CTkFrame(self.content,fg_color="transparent"); inf.pack(fill="x",padx=32,pady=(10,0))
        self._chat_e=ctk.CTkEntry(inf,placeholder_text="Γράψε μήνυμα…",fg_color=CARD,
                                   border_color=BORDER,text_color=TEXT,placeholder_text_color=SUBTEXT,
                                   font=ctk.CTkFont(size=13),height=44,corner_radius=12)
        self._chat_e.pack(side="left",fill="x",expand=True,padx=(0,10))
        self._chat_e.bind("<Return>",lambda e:self._send())
        btn(inf,"➤",self._send,color=ACCENT,tc="#0F1117",h=44,width=60).pack(side="left")

    def _bot_say(self,t):
        self._chat_box.configure(state="normal")
        self._chat_box.insert("end",f"🤖  {t}\n\n")
        self._chat_box.configure(state="disabled")
        self._chat_box.see("end")

    def _user_say(self,t):
        self._chat_box.configure(state="normal")
        self._chat_box.insert("end",f"👤  {t}\n")
        self._chat_box.configure(state="disabled")
        self._chat_box.see("end")

    def _send(self,forced=None):
        import re
        text=forced or self._chat_e.get().strip()
        if not text: return
        self._chat_e.delete(0,"end"); self._user_say(text)
        if QUIZ_STATE["active"]: self._quiz_ans(text); return
        if re.search(r"(κουιζ|κουίζ|quiz)",text,re.IGNORECASE):
            QUIZ_STATE.update({"active":True,"index":0})
            q=ALL_QUIZ[0]
            self._bot_say(f"🎮 Ερώτηση 1/{len(ALL_QUIZ)}:\n{q['q']}\n"+"\n".join(q["opts"])); return
        if re.search(r"(gps|διαδρομη|διαδρομή|δρομολογιο|δρομολόγιο|χαρτη|πλοηγηση)",text,re.IGNORECASE):
            self._bot_say("📡 GPS: Εντοπισμός τοποθεσίας…")
            self.after(600,lambda:self._do_gps(text)); return
        self._bot_say(get_bot_response(CITIZEN_ID,text,BOT_CTX))

    def _do_gps(self,text):
        webbrowser.open("https://www.google.com/maps/search/κάδοι+ανακύκλωσης+Πάτρα/@38.2466,21.7346,14z")
        self._bot_say("✅ Άνοιξε ο χάρτης στον browser!\n\n🗺️ "+plan_eco_route(CITIZEN_ID,text,BOT_CTX))

    def _quiz_ans(self,answer):
        idx=QUIZ_STATE["index"]; q=ALL_QUIZ[idx]
        self._bot_say(f"✅ Σωστά! {q['exp']}" if answer.strip()==q["a"] else f"❌ Λάθος. Σωστή: {q['a']}. {q['exp']}")
        QUIZ_STATE["index"]+=1
        if QUIZ_STATE["index"]>=len(ALL_QUIZ):
            QUIZ_STATE.update({"active":False,"index":0})
            self._bot_say(f"🏆 Τέλος! Απάντησες και στις {len(ALL_QUIZ)} ερωτήσεις!"); return
        nq=ALL_QUIZ[QUIZ_STATE["index"]]
        self._bot_say(f"🎮 Ερώτηση {QUIZ_STATE['index']+1}/{len(ALL_QUIZ)}:\n{nq['q']}\n"+"\n".join(nq["opts"]))

    # ══════════════════════════════════════════════════════════
    # UC10 — Προκλήσεις
    # ══════════════════════════════════════════════════════════
    def _challenges(self):
        self._header("Πράσινες Προκλήσεις","Περίπτωση Χρήσης 10")
        cols=ctk.CTkFrame(self.content,fg_color="transparent"); cols.pack(fill="x",padx=32,pady=(20,0))
        lc=ctk.CTkFrame(cols,fg_color="transparent"); lc.pack(side="left",fill="both",expand=True,padx=(0,10))
        sec(lc,"ΔΗΜΙΟΥΡΓΙΑ ΝΕΑΣ ΠΡΟΚΛΗΣΗΣ")
        c1=card(lc); c1.pack(fill="x")
        p1=ctk.CTkFrame(c1,fg_color="transparent"); p1.pack(fill="x",padx=16,pady=16)
        g=inp(p1,"Στόχος πρόκλησης"); g.pack(fill="x",pady=(0,10))
        b=inp(p1,"Έμβλημα"); b.pack(fill="x",pady=(0,10))
        jl=lbl(p1,"",size=12); jl.pack(anchor="w",pady=(0,8))
        cv=ctk.StringVar()
        def do_join():
            if not g.get().strip(): jl.configure(text="❌ Βάλε στόχο.",text_color=DANGER); return
            r=join_green_challenge(CITIZEN_ID,g.get(),b.get())
            jl.configure(text=f"✅ {r['message']}" if r["success"] else f"❌ {r['message']}",
                         text_color=ACCENT if r["success"] else DANGER)
            if r["success"]: cv.set(str(r["challenge_id"]))
        btn(p1,"Εγγραφή",do_join,h=38).pack(fill="x")

        rc=ctk.CTkFrame(cols,fg_color="transparent"); rc.pack(side="left",fill="both",expand=True,padx=(10,0))
        sec(rc,"ΟΛΟΚΛΗΡΩΣΗ  (+30 π.)")
        c2=card(rc); c2.pack(fill="x")
        p2=ctk.CTkFrame(c2,fg_color="transparent"); p2.pack(fill="x",padx=16,pady=16)
        lbl(p2,"Εισάγαι το ID που πήρες κατά την εγγραφή.",size=12,color=SUBTEXT,wraplength=260).pack(anchor="w",pady=(0,8))
        ie=inp(p2,"ID Πρόκλησης"); ie.pack(fill="x",pady=(0,10))
        cl=lbl(p2,"",size=12); cl.pack(anchor="w",pady=(0,8))
        def do_complete():
            try: cid=int(ie.get())
            except ValueError: cl.configure(text="❌ Βάλε αριθμό.",text_color=DANGER); return
            r=complete_green_challenge(cid)
            if r["success"]:
                new_total=session_add_points(30,"challenge")
                self._refresh_pts()
                cl.configure(text=f"✅ {r['message']}  |  +30 π.  |  Σύνολο: {new_total} π.",text_color=ACCENT)
            else:
                cl.configure(text=f"❌ {r['message']}",text_color=DANGER)
        btn(p2,"Ολοκλήρωση +30 π.",do_complete,h=38).pack(fill="x")

    # ══════════════════════════════════════════════════════════
    # Leaderboard
    # ══════════════════════════════════════════════════════════
    def _leaderboard(self):
        self._header("Leaderboard — Πίνακας Κατάταξης","Κατάταξη πολιτών βάσει πράσινων πόντων")

        # Update current user's score
        LEADERBOARD[3]["points"] = SESSION["points"]

        podium=ctk.CTkFrame(self.content,fg_color="transparent"); podium.pack(fill="x",padx=32,pady=(20,0))
        for medal,entry,color in [("🥈",LEADERBOARD[1],"#C0C0C0"),("🥇",LEADERBOARD[0],WARNING),("🥉",LEADERBOARD[2],"#CD7F32")]:
            f=card(podium); f.pack(side="left",expand=True,fill="x",padx=6)
            ctk.CTkFrame(f,fg_color=color,height=3,corner_radius=2).pack(fill="x",padx=0)
            lbl(f,medal,size=28).pack(pady=(14,4))
            lbl(f,entry["name"].split()[0],size=13,weight="bold").pack()
            lbl(f,f"{entry['points']:,} π.",size=18,weight="bold",color=color).pack(pady=4)
            lbl(f,f"♻️ {entry['recycled']}",size=11,color=SUBTEXT).pack(pady=(0,16))

        sec(self.content,"  ΠΛΗΡΗΣ ΚΑΤΑΤΑΞΗ")
        tc=card(self.content); tc.pack(fill="x",padx=32,pady=(0,20))
        hr=ctk.CTkFrame(tc,fg_color=BG,corner_radius=0); hr.pack(fill="x")
        hrr=ctk.CTkFrame(hr,fg_color="transparent"); hrr.pack(fill="x",padx=16,pady=8)
        for t,w in [("#",40),("Όνομα",280),("Πόντοι",110),("Ανακύκλωση",110),("",40)]:
            lbl(hrr,t,size=11,weight="bold",color=SUBTEXT,width=w,anchor="w").pack(side="left",padx=4)

        sorted_lb = sorted(LEADERBOARD, key=lambda x: x["points"], reverse=True)
        for i,e in enumerate(sorted_lb):
            is_me=e["name"]=="Κατερίνα Πετροπούλου"
            row=ctk.CTkFrame(tc,fg_color="#1A3D32" if is_me else "transparent",corner_radius=0)
            row.pack(fill="x")
            rr=ctk.CTkFrame(row,fg_color="transparent"); rr.pack(fill="x",padx=16,pady=10)
            rank_col=WARNING if i==0 else TEXT
            lbl(rr,str(i+1),size=13,weight="bold",color=rank_col,width=40,anchor="w").pack(side="left",padx=4)
            nm=f"{e['name']}  ← Εσύ" if is_me else e["name"]
            lbl(rr,nm,size=13,weight="bold" if is_me else "normal",
                color=ACCENT if is_me else TEXT,width=280,anchor="w").pack(side="left",padx=4)
            lbl(rr,f"{e['points']:,} π.",size=13,color=ACCENT,width=110,anchor="w").pack(side="left",padx=4)
            lbl(rr,e["recycled"],size=13,color=SUBTEXT,width=110,anchor="w").pack(side="left",padx=4)
            lbl(rr,e["badge"],size=16,width=40,anchor="w").pack(side="left",padx=4)
            ctk.CTkFrame(tc,fg_color=BORDER,height=1).pack(fill="x",padx=16)

    # ══════════════════════════════════════════════════════════
    # UC11/12 — Υπάλληλος
    # ══════════════════════════════════════════════════════════
    def _employee(self):
        self._header("Πίνακας Υπαλλήλου","Περιπτώσεις Χρήσης 11 & 12")
        cols=ctk.CTkFrame(self.content,fg_color="transparent"); cols.pack(fill="x",padx=32,pady=(20,0))
        def emp_col(parent,title,hint,ph,bt,fn,col=ACCENT):
            f=ctk.CTkFrame(parent,fg_color="transparent"); f.pack(side="left",fill="both",expand=True,padx=6)
            sec(f,title); c=card(f); c.pack(fill="x")
            p=ctk.CTkFrame(c,fg_color="transparent"); p.pack(fill="x",padx=16,pady=16)
            lbl(p,hint,size=12,color=SUBTEXT,wraplength=260).pack(anchor="w",pady=(0,8))
            e=inp(p,ph); e.pack(fill="x",pady=(0,10))
            l=lbl(p,"",size=12); l.pack(anchor="w",pady=(0,8))
            def do(e=e,l=l,f=fn):
                try: v=int(e.get())
                except ValueError: l.configure(text="❌ Βάλε αριθμό.",text_color=DANGER); return
                r=f(v); l.configure(text=("✅ " if r.get("success") else "❌ ")+r.get("message",""),
                                    text_color=ACCENT if r.get("success") else DANGER)
            btn(p,bt,do,color=col,tc="#0F1117" if col==ACCENT else TEXT,h=38).pack(fill="x")
        emp_col(cols,"ΑΠΟΚΟΜΙΔΗ  (ΠΧ11)","ID κάδου που αποκομίστηκε.","ID Κάδου","✓ Αποκομιδή",lambda bid:complete_collection(101,bid))
        emp_col(cols,"ΒΛΑΒΗ  (ΠΧ11)","ID κάδου με βλάβη.","ID Κάδου","⚠️ Δήλωση Βλάβης",lambda bid:report_bin_damage(101,bid),DANGER)
        sec(self.content,"  ΔΗΜΟΣΙΕΥΣΗ ΔΡΑΣΗΣ  (ΠΧ12)")
        dc=card(self.content); dc.pack(fill="x",padx=32)
        dp=ctk.CTkFrame(dc,fg_color="transparent"); dp.pack(fill="x",padx=16,pady=16)
        dr=ctk.CTkFrame(dp,fg_color="transparent"); dr.pack(fill="x")
        te=inp(dr,"Τίτλος δράσης"); te.pack(side="left",fill="x",expand=True,padx=(0,12))
        pl=lbl(dp,"",size=12); pl.pack(anchor="w",pady=(10,0))
        def do_pub():
            t=te.get().strip()
            if not t: pl.configure(text="❌ Βάλε τίτλο.",text_color=DANGER); return
            r=publish_environmental_action(101,t)
            pl.configure(text=f"✅ {r['message']}",text_color=ACCENT)
        btn(dr,"Δημοσίευση",do_pub,h=38).pack(side="left")

if __name__ == "__main__":
    def launch_main(username):
        app = BinGoApp()
        app.mainloop()

    login = LoginWindow(on_success=launch_main)
    login.mainloop()
