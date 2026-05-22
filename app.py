# ======================================================
# BinGo — app.py
# Desktop GUI using CustomTkinter.
# Run with:  python app.py
# ======================================================

import customtkinter as ctk
from tkinter import messagebox

import logic
from logic import (
    Citizen, GreenChallenge, RecyclingBin, BinMap, BinDetailsSystem,
    scan_material, redeem_points, donate_points, add_reward_points,
    qr_bin_reward, evaluate_bin, get_bot_response, check_quiz_answer,
    join_green_challenge, complete_green_challenge,
    complete_collection, report_bin_damage, publish_environmental_action,
    BIN_MAP, QUIZ_EASY, QUIZ_HARD,
)

# ── appearance ───────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

GREEN  = "#1D9E75"
LGREY  = "#F5F5F5"
DKTEXT = "#1A1A1A"
GREY   = "#6B6B6B"

# ── demo citizen (UC1) ───────────────────────────────
CITIZEN = Citizen(
    name="Αριάδνη Σεχάι",
    email="ariadne@gmail.com",
    total_points=1500,
    total_recycling=25,
    badges=["Eco Starter 🥉", "Green Hero 🥇"],
)
CITIZEN.challenges  = [GreenChallenge("Recycle 10 πλαστικά μπουκάλια")]
CITIZEN.transactions = [
    "Σάρωση QR κάδου  →  +20 π.",
    "Σωστή ανακύκλωση →  +15 π.",
    "Εξαργύρωση κουπονιού → −100 π.",
    "Καθημερινή σύνδεση → +5 π.",
]
CITIZEN_ID = 1

# ── demo bins (UC2 / UC3) ────────────────────────────
_BIN_MAP   = BinMap()
_BIN_DETAILS = BinDetailsSystem()

for _b in [
    RecyclingBin(1, "Πλαστικό",   "Πλατεία Γεωργίου",   250, "100 L", 4, True,  "12/05/2026", [], ["Καθαρό σημείο", "Εύκολη πρόσβαση"], 20),
    RecyclingBin(2, "Χαρτί",      "Αγίου Ανδρέου",       500, "120 L", 3, True,  "12/05/2026", [], ["Καλή κατάσταση"],                    15),
    RecyclingBin(3, "Γυαλί",      "Ρήγα Φεραίου",        800, "80 L",  2, False, "12/05/2026", [], ["Λίγο μακριά"],                        10),
    RecyclingBin(4, "Αλουμίνιο",  "Πλατεία Ψηλαλωνίων", 400, "90 L",  5, True,  "12/05/2026", [], ["Πολύ καθαρό"],                        12),
]:
    _BIN_MAP.add_bin(_b)

# ── chatbot context (UC8 / UC9) ──────────────────────
BOT_CONTEXT = {}

# ── quiz state (UC8 quiz) ────────────────────────────
QUIZ_STATE = {"active": False, "phase": "easy", "index": 0}


# ╔══════════════════════════════════════════════════╗
# ║                  MAIN WINDOW                     ║
# ╚══════════════════════════════════════════════════╝

class BinGoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BinGo — Έξυπνη Ανακύκλωση")
        self.geometry("1020x680")
        self.resizable(False, False)
        self._build_sidebar()
        self._build_content()
        self.show_profile()

    # ── sidebar ──────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color=GREEN)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        ctk.CTkLabel(
            sb, text="🌿  BinGo",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white",
        ).pack(pady=(30, 24))

        self._nav_buttons = {}
        nav = [
            ("👤  Προφίλ",             "profile",     self.show_profile),
            ("🗺️   Χάρτης Κάδων",       "map",         self.show_map),
            ("📦  Σάρωση Υλικού",       "scan",        self.show_scan),
            ("🎁  Πόντοι & Δωρεά",      "rewards",     self.show_rewards),
            ("⭐  Αξιολόγηση Κάδου",    "evaluate",    self.show_evaluate),
            ("🤖  BinGo AI",            "chat",        self.show_chat),
            ("🏆  Προκλήσεις",          "challenges",  self.show_challenges),
            ("🚛  Υπάλληλος",           "employee",    self.show_employee),
        ]
        for label, key, cmd in nav:
            btn = ctk.CTkButton(
                sb, text=label, anchor="w",
                command=lambda c=cmd, k=key: self._nav_click(c, k),
                fg_color="transparent", text_color="white",
                hover_color="#158A62",
                height=42, corner_radius=0,
                font=ctk.CTkFont(size=13),
            )
            btn.pack(fill="x", padx=0)
            self._nav_buttons[key] = btn

        ctk.CTkLabel(
            sb, text="BinGo v2 · Ομάδα Αριάδνη",
            font=ctk.CTkFont(size=10), text_color="#B2DFCF",
        ).pack(side="bottom", pady=12)

    def _nav_click(self, cmd, key):
        for k, b in self._nav_buttons.items():
            b.configure(fg_color="#158A62" if k == key else "transparent")
        cmd()

    # ── content area ─────────────────────────────────
    def _build_content(self):
        self.content = ctk.CTkScrollableFrame(
            self, corner_radius=0, fg_color=LGREY,
        )
        self.content.pack(side="left", fill="both", expand=True)

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _title(self, text):
        ctk.CTkLabel(
            self.content, text=text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=DKTEXT,
        ).pack(anchor="w", padx=24, pady=(20, 4))

    def _subtitle(self, text):
        ctk.CTkLabel(
            self.content, text=text,
            font=ctk.CTkFont(size=12), text_color=GREY,
        ).pack(anchor="w", padx=24, pady=(0, 14))

    def _card(self, parent=None):
        parent = parent or self.content
        f = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        f.pack(fill="x", padx=24, pady=6)
        return f

    def _row(self, parent, label, value, value_color=DKTEXT):
        r = ctk.CTkFrame(parent, fg_color="transparent")
        r.pack(fill="x", padx=14, pady=3)
        ctk.CTkLabel(r, text=label, text_color=GREY,   font=ctk.CTkFont(size=13)).pack(side="left")
        ctk.CTkLabel(r, text=value, text_color=value_color, font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")

    def _result_label(self, text, color=DKTEXT):
        """Shows a result message inside a card."""
        card = self._card()
        ctk.CTkLabel(
            card, text=text, text_color=color,
            font=ctk.CTkFont(size=13), wraplength=680,
        ).pack(padx=14, pady=10)

    # ══════════════════════════════════════════════════
    # UC1 — Green Profile
    # ══════════════════════════════════════════════════
    def show_profile(self):
        self._clear()
        data = CITIZEN.get_profile_data()
        self._title("Πράσινο Προφίλ")
        self._subtitle("Περίπτωση Χρήσης 1")

        # Stats row
        stats_f = ctk.CTkFrame(self.content, fg_color="transparent")
        stats_f.pack(fill="x", padx=24, pady=(0, 8))
        for label, val, col in [
            ("Πράσινοι Πόντοι",  str(data["total_points"]),    GREEN),
            ("Ανακύκλωση",       f"{data['total_recycling']} kg", DKTEXT),
            ("Δέντρα σώθηκαν",   str(data["trees_saved"]),     "#2E7D32"),
            ("Εξοικ. Νερό",      f"{data['water_saved']} L",   "#0077B6"),
        ]:
            c = ctk.CTkFrame(stats_f, fg_color="white", corner_radius=10)
            c.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(c, text=val,   font=ctk.CTkFont(size=22, weight="bold"), text_color=col).pack(pady=(12, 2))
            ctk.CTkLabel(c, text=label, font=ctk.CTkFont(size=11), text_color=GREY).pack(pady=(0, 12))

        # Badges
        card = self._card()
        ctk.CTkLabel(card, text="Εμβλήματα", font=ctk.CTkFont(size=13, weight="bold"), text_color=DKTEXT).pack(anchor="w", padx=14, pady=(10, 4))
        bf = ctk.CTkFrame(card, fg_color="transparent")
        bf.pack(anchor="w", padx=14, pady=(0, 10))
        for b in data["badges"]:
            ctk.CTkLabel(bf, text=b, fg_color="#D1FAE5", text_color="#065F46",
                         corner_radius=20, padx=12, pady=4,
                         font=ctk.CTkFont(size=12)).pack(side="left", padx=4)

        # Active challenges
        card2 = self._card()
        ctk.CTkLabel(card2, text="Ενεργές Προκλήσεις", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(10, 4))
        if data["challenges"]:
            for ch in data["challenges"]:
                ctk.CTkLabel(card2, text=f"  •  {ch}", text_color=DKTEXT, font=ctk.CTkFont(size=13)).pack(anchor="w", padx=14)
        else:
            ctk.CTkLabel(card2, text="  Καμία ενεργή πρόκληση.", text_color=GREY, font=ctk.CTkFont(size=13)).pack(anchor="w", padx=14)
        ctk.CTkLabel(card2, text="").pack(pady=2)

        # Transactions
        card3 = self._card()
        ctk.CTkLabel(card3, text="Πρόσφατες Συναλλαγές", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(10, 4))
        for tx in data["transactions"]:
            col = GREEN if "+" in tx else "#C0392B"
            ctk.CTkLabel(card3, text=f"  {tx}", text_color=col, font=ctk.CTkFont(size=13)).pack(anchor="w", padx=14)
        ctk.CTkLabel(card3, text="").pack(pady=2)

    # ══════════════════════════════════════════════════
    # UC2 — Bin Map  /  UC3 — Bin Details
    # ══════════════════════════════════════════════════
    def show_map(self):
        self._clear()
        self._title("Χάρτης Κάδων")
        self._subtitle("Περιπτώσεις Χρήσης 2 & 3")

        result = _BIN_MAP.get_nearby_bins(CITIZEN)
        if "error" in result:
            self._result_label(result["error"], "#C0392B")
            return

        ctk.CTkLabel(
            self.content,
            text=f"📍 Τοποθεσία: {result['location']}  —  {len(result['bins'])} κοντινοί κάδοι",
            font=ctk.CTkFont(size=13), text_color=GREY,
        ).pack(anchor="w", padx=24, pady=(0, 8))

        for b in result["bins"]:
            card = self._card()
            top  = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=14, pady=(10, 4))

            ctk.CTkLabel(top, text=b.material_type,
                         font=ctk.CTkFont(size=14, weight="bold"), text_color=DKTEXT).pack(side="left")
            ctk.CTkLabel(top, text=f"{b.distance} m",
                         font=ctk.CTkFont(size=12), text_color=GREY).pack(side="right")

            self._row(card, "Τοποθεσία",   b.location)
            self._row(card, "Χωρητικότητα", b.capacity)
            if b.real_time_available:
                self._row(card, "Διαθέσιμες θέσεις", str(b.available_slots), GREEN)
            else:
                self._row(card, "Τελευταία ενημέρωση", b.last_update)
            self._row(card, "Bonus πόντοι", f"+{b.bonus_points} π.", GREEN)

            # UC3 — details button
            def _show_details(rb=b):
                self._show_bin_details(rb)
            ctk.CTkButton(
                card, text="Λεπτομέρειες →", command=_show_details,
                fg_color=GREEN, hover_color="#158A62",
                height=30, font=ctk.CTkFont(size=12),
            ).pack(anchor="e", padx=14, pady=(4, 10))

    def _show_bin_details(self, rb):
        """UC3 — Opens a popup with full bin details."""
        d   = _BIN_DETAILS.get_bin_details(rb)
        win = ctk.CTkToplevel(self)
        win.title(f"Στοιχεία Κάδου — {d['material_type']}")
        win.geometry("420x380")
        win.grab_set()

        ctk.CTkLabel(win, text=f"Κάδος: {d['material_type']}",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 6))

        for label, val in [
            ("Τοποθεσία",    d["location"]),
            ("Χωρητικότητα", d["capacity"]),
            ("Bonus πόντοι", f"+{d['bonus_points']} π."),
            ("Real-time",    "Ναι" if d["real_time"] else "Όχι"),
        ]:
            r = ctk.CTkFrame(win, fg_color="transparent")
            r.pack(fill="x", padx=24, pady=2)
            ctk.CTkLabel(r, text=label, text_color=GREY, font=ctk.CTkFont(size=13)).pack(side="left")
            ctk.CTkLabel(r, text=val,   text_color=DKTEXT, font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")

        ctk.CTkLabel(win, text="Κριτικές", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=24, pady=(12, 2))
        for rev in (d["reviews"] or ["Καμία κριτική ακόμα."]):
            ctk.CTkLabel(win, text=f"  •  {rev}", text_color=DKTEXT, font=ctk.CTkFont(size=13)).pack(anchor="w", padx=24)

        ctk.CTkButton(win, text="Κλείσιμο", command=win.destroy, fg_color=GREEN).pack(pady=18)

    # ══════════════════════════════════════════════════
    # UC4 — Material Scan
    # ══════════════════════════════════════════════════
    def show_scan(self):
        self._clear()
        self._title("Σάρωση & Αναγνώριση Υλικού")
        self._subtitle("Περίπτωση Χρήσης 4")

        card = self._card()
        ctk.CTkLabel(card, text="Επίλεξε υλικό:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(12, 6))

        mat_var = ctk.StringVar(value="πλαστικό")
        options = ["πλαστικό", "χαρτί", "γυαλί", "αλουμίνιο", "μπαταρία", "άγνωστο"]
        ctk.CTkOptionMenu(card, values=options, variable=mat_var,
                          fg_color=GREEN, button_color="#158A62",
                          font=ctk.CTkFont(size=13)).pack(padx=14, pady=(0, 10), fill="x")

        result_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        result_frame.pack(fill="x", padx=0)

        def do_scan():
            for w in result_frame.winfo_children():
                w.destroy()
            res = scan_material(CITIZEN_ID, mat_var.get())

            card2 = ctk.CTkFrame(result_frame, fg_color="white", corner_radius=10)
            card2.pack(fill="x", padx=24, pady=6)

            if res["status"] == "recyclable":
                ctk.CTkLabel(card2, text="✅  Ανακυκλώσιμο υλικό",
                             font=ctk.CTkFont(size=14, weight="bold"), text_color=GREEN).pack(anchor="w", padx=14, pady=(12, 4))
                for lbl, val in [
                    ("Υλικό",       res["material"]),
                    ("Κάδος",       res["bin_color"]),
                    ("Οδηγίες",     res["instructions"]),
                    ("Πόντοι",      f"+{res['points']} π."),
                ]:
                    r = ctk.CTkFrame(card2, fg_color="transparent")
                    r.pack(fill="x", padx=14, pady=1)
                    ctk.CTkLabel(r, text=lbl, text_color=GREY, font=ctk.CTkFont(size=12)).pack(side="left")
                    ctk.CTkLabel(r, text=val, text_color=DKTEXT, font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")
                if res["nearby_bins"]:
                    ctk.CTkLabel(card2, text="Κοντινοί κάδοι:", text_color=GREY, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14, pady=(6, 0))
                    for b in res["nearby_bins"]:
                        ctk.CTkLabel(card2, text=f"  •  Κάδος {b['binID']} — {b['location']}", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14)

            elif res["status"] == "special":
                ctk.CTkLabel(card2, text="⚠️  Ειδική Ανακύκλωση",
                             font=ctk.CTkFont(size=14, weight="bold"), text_color="#B45309").pack(anchor="w", padx=14, pady=(12, 4))
                ctk.CTkLabel(card2, text=res["message"],  font=ctk.CTkFont(size=13), wraplength=560).pack(anchor="w", padx=14)
                ctk.CTkLabel(card2, text=res["extra"],    font=ctk.CTkFont(size=12), text_color=GREY, wraplength=560).pack(anchor="w", padx=14, pady=(2, 10))

            else:
                ctk.CTkLabel(card2, text="🚫  Μη Ανακυκλώσιμο",
                             font=ctk.CTkFont(size=14, weight="bold"), text_color="#C0392B").pack(anchor="w", padx=14, pady=(12, 4))
                ctk.CTkLabel(card2, text=res["message"], font=ctk.CTkFont(size=13)).pack(anchor="w", padx=14, pady=(0, 10))

        ctk.CTkButton(card, text="Αναγνώριση ▶", command=do_scan,
                      fg_color=GREEN, hover_color="#158A62",
                      height=36, font=ctk.CTkFont(size=13)).pack(padx=14, pady=(0, 12), fill="x")

    # ══════════════════════════════════════════════════
    # UC5 — Points Redemption & Donation  /  UC6 — Reward Activities
    # ══════════════════════════════════════════════════
    def show_rewards(self):
        self._clear()
        self._title("Πόντοι, Εξαργύρωση & Δωρεά")
        self._subtitle("Περιπτώσεις Χρήσης 5 & 6")

        # UC6 — earn points
        card = self._card()
        ctk.CTkLabel(card, text="Κέρδισε Πόντους (ΠΧ6)", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(12, 4))
        act_var = ctk.StringVar(value="daily_login")
        ctk.CTkOptionMenu(card, values=["daily_login", "correct_recycling", "qr_scan", "green_challenge"],
                          variable=act_var, fg_color=GREEN, button_color="#158A62",
                          font=ctk.CTkFont(size=13)).pack(fill="x", padx=14)
        result_earn = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=13))
        result_earn.pack(anchor="w", padx=14, pady=4)

        def do_earn():
            r = add_reward_points(CITIZEN_ID, act_var.get())
            if r["success"]:
                result_earn.configure(text=f"✅ +{r['earned']} πόντοι! Νέο σύνολο: {r['new_total']}", text_color=GREEN)
            else:
                result_earn.configure(text=f"❌ {r['message']}", text_color="#C0392B")
        ctk.CTkButton(card, text="Πίστωση Πόντων", command=do_earn,
                      fg_color=GREEN, hover_color="#158A62", height=34).pack(padx=14, pady=(0, 12), fill="x")

        # UC5 — redeem
        card2 = self._card()
        ctk.CTkLabel(card2, text="Εξαργύρωση Ανταμοιβής (ΠΧ5)", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(12, 4))
        ctk.CTkLabel(card2, text="ID Ανταμοιβής (1, 2, …):", text_color=GREY, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14)
        reward_entry = ctk.CTkEntry(card2, placeholder_text="πχ. 1", font=ctk.CTkFont(size=13))
        reward_entry.pack(fill="x", padx=14, pady=4)
        result_redeem = ctk.CTkLabel(card2, text="", font=ctk.CTkFont(size=13), wraplength=580)
        result_redeem.pack(anchor="w", padx=14, pady=2)

        def do_redeem():
            try:
                rid = int(reward_entry.get())
            except ValueError:
                result_redeem.configure(text="❌ Βάλε έναν αριθμό.", text_color="#C0392B")
                return
            r = redeem_points(CITIZEN_ID, rid)
            if r["success"]:
                result_redeem.configure(
                    text=f"✅ {r['message']}  |  Νέο υπόλοιπο: {r['new_total']} π.",
                    text_color=GREEN,
                )
            else:
                result_redeem.configure(text=f"❌ {r['message']}", text_color="#C0392B")
        ctk.CTkButton(card2, text="Εξαργύρωση", command=do_redeem,
                      fg_color=GREEN, hover_color="#158A62", height=34).pack(padx=14, pady=(0, 12), fill="x")

        # UC5 — donate
        card3 = self._card()
        ctk.CTkLabel(card3, text="Δωρεά Πόντων σε Οργανισμό (ΠΧ5)", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(12, 4))
        org_entry = ctk.CTkEntry(card3, placeholder_text="Όνομα οργανισμού", font=ctk.CTkFont(size=13))
        org_entry.pack(fill="x", padx=14, pady=4)
        pts_entry = ctk.CTkEntry(card3, placeholder_text="Αριθμός πόντων", font=ctk.CTkFont(size=13))
        pts_entry.pack(fill="x", padx=14, pady=4)
        result_donate = ctk.CTkLabel(card3, text="", font=ctk.CTkFont(size=13), wraplength=580)
        result_donate.pack(anchor="w", padx=14, pady=2)

        def do_donate():
            try:
                pts = int(pts_entry.get())
            except ValueError:
                result_donate.configure(text="❌ Βάλε έναν αριθμό.", text_color="#C0392B")
                return
            org = org_entry.get().strip() or "Περιβαλλοντική Δράση"
            r   = donate_points(CITIZEN_ID, pts, org)
            col = GREEN if r["success"] else "#C0392B"
            msg = f"✅ {r['message']}" if r["success"] else f"❌ {r['message']}"
            result_donate.configure(text=msg, text_color=col)
        ctk.CTkButton(card3, text="Δωρεά", command=do_donate,
                      fg_color=GREEN, hover_color="#158A62", height=34).pack(padx=14, pady=(0, 12), fill="x")

    # ══════════════════════════════════════════════════
    # UC7 — Bin Evaluation
    # ══════════════════════════════════════════════════
    def show_evaluate(self):
        self._clear()
        self._title("Αξιολόγηση Κάδου Ανακύκλωσης")
        self._subtitle("Περίπτωση Χρήσης 7")

        card = self._card()
        ctk.CTkLabel(card, text="Κωδικός Κάδου:", text_color=GREY, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14, pady=(12, 0))
        bin_var = ctk.StringVar(value=list(BIN_MAP.keys())[0])
        ctk.CTkOptionMenu(card, values=list(BIN_MAP.keys()), variable=bin_var,
                          fg_color=GREEN, button_color="#158A62",
                          font=ctk.CTkFont(size=12)).pack(fill="x", padx=14, pady=4)

        ctk.CTkLabel(card, text="Βαθμολογία (1–5):", text_color=GREY, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14, pady=(6, 0))
        rating_var = ctk.IntVar(value=5)
        ctk.CTkSlider(card, from_=1, to=5, number_of_steps=4, variable=rating_var).pack(fill="x", padx=14, pady=2)
        rating_lbl = ctk.CTkLabel(card, text="5 ⭐", font=ctk.CTkFont(size=13))
        rating_lbl.pack(anchor="e", padx=14)
        rating_var.trace_add("write", lambda *_: rating_lbl.configure(text=f"{rating_var.get()} ⭐"))

        ctk.CTkLabel(card, text="Σχόλιο (έως 200 χαρ.):", text_color=GREY, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14, pady=(6, 0))
        comment_box = ctk.CTkTextbox(card, height=70, font=ctk.CTkFont(size=13))
        comment_box.pack(fill="x", padx=14, pady=4)

        result_lbl = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=13), wraplength=580)
        result_lbl.pack(anchor="w", padx=14, pady=4)

        def do_evaluate():
            comment = comment_box.get("1.0", "end").strip()
            r = evaluate_bin(CITIZEN_ID, bin_var.get(), rating_var.get(), comment)
            if r["success"]:
                msg = f"✅ {r['message']}"
                if r.get("notify_municipality"):
                    msg += f"\n⚠️ {r['notify_message']}"
                result_lbl.configure(text=msg, text_color=GREEN)
            else:
                result_lbl.configure(text=f"❌ {r['message']}", text_color="#C0392B")

        ctk.CTkButton(card, text="Υποβολή Αξιολόγησης", command=do_evaluate,
                      fg_color=GREEN, hover_color="#158A62", height=36).pack(padx=14, pady=(0, 12), fill="x")

    # ══════════════════════════════════════════════════
    # UC8 — BinGo AI Chatbot  (incl. UC9 routing & quiz)
    # ══════════════════════════════════════════════════
    def show_chat(self):
        self._clear()
        self._title("BinGo AI — Ψηφιακός Βοηθός")
        self._subtitle("Περιπτώσεις Χρήσης 8 & 9")

        # Chat log
        self._chat_log = ctk.CTkTextbox(
            self.content, height=320,
            font=ctk.CTkFont(size=13),
            state="disabled", wrap="word",
        )
        self._chat_log.pack(fill="x", padx=24, pady=(0, 6))
        self._bot_say("Γεια! Είμαι ο BinGo AI. Ρώτα με για κάδους, δράσεις, δρομολόγιο ή γράψε «κουίζ» για να ξεκινήσουμε! 🌱")

        # Quick buttons
        qf = ctk.CTkFrame(self.content, fg_color="transparent")
        qf.pack(fill="x", padx=24, pady=(0, 6))
        for txt in ["Κάδοι γυαλιού Κέντρο", "Τελευταίες δράσεις", "κουίζ",
                    "δρομολόγιο για χαρτί και γυαλί στο κέντρο"]:
            ctk.CTkButton(
                qf, text=txt, height=28,
                fg_color="#E8F5E9", text_color="#1B5E20",
                hover_color="#C8E6C9", corner_radius=20,
                font=ctk.CTkFont(size=11),
                command=lambda t=txt: self._send_chat(t),
            ).pack(side="left", padx=4)

        # Input row
        inp_f = ctk.CTkFrame(self.content, fg_color="transparent")
        inp_f.pack(fill="x", padx=24, pady=(0, 10))
        self._chat_entry = ctk.CTkEntry(inp_f, placeholder_text="Γράψε μήνυμα…", font=ctk.CTkFont(size=13))
        self._chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._chat_entry.bind("<Return>", lambda e: self._send_chat())
        ctk.CTkButton(inp_f, text="➤", width=50, fg_color=GREEN, hover_color="#158A62",
                      command=self._send_chat).pack(side="left")

    def _bot_say(self, text):
        self._chat_log.configure(state="normal")
        self._chat_log.insert("end", f"🤖  {text}\n\n")
        self._chat_log.configure(state="disabled")
        self._chat_log.see("end")

    def _user_say(self, text):
        self._chat_log.configure(state="normal")
        self._chat_log.insert("end", f"👤  {text}\n")
        self._chat_log.configure(state="disabled")
        self._chat_log.see("end")

    def _send_chat(self, forced_text=None):
        text = forced_text or self._chat_entry.get().strip()
        if not text:
            return
        self._chat_entry.delete(0, "end")
        self._user_say(text)

        # --- Quiz mode ---
        if QUIZ_STATE["active"]:
            self._handle_quiz_answer(text)
            return

        # --- Trigger quiz ---
        if "κουιζ" in text.lower() or "κουίζ" in text.lower():
            QUIZ_STATE.update({"active": True, "phase": "easy", "index": 0})
            q = QUIZ_EASY[0]
            self._bot_say(f"🎮 Επίπεδο 1 — Ερώτηση 1:\n{q['question']}\n" + "\n".join(q["options"]))
            return

        # --- Normal chatbot ---
        response = get_bot_response(CITIZEN_ID, text, BOT_CONTEXT)
        self._bot_say(response)

    def _handle_quiz_answer(self, answer):
        result = check_quiz_answer(
            CITIZEN_ID,
            QUIZ_STATE["phase"],
            QUIZ_STATE["index"],
            answer,
            BOT_CONTEXT,
        )
        self._bot_say(result.get("message", ""))

        if result.get("advance_phase") == "hard":
            QUIZ_STATE["phase"] = "hard"
            QUIZ_STATE["index"] = 0
            q = QUIZ_HARD[0]
            self._bot_say(f"🎮 Επίπεδο 2 — Ερώτηση 1:\n{q['question']}\n" + "\n".join(q["options"]))
            return

        if result.get("finished"):
            QUIZ_STATE.update({"active": False, "phase": "easy", "index": 0})
            return

        QUIZ_STATE["index"] += 1
        qs = QUIZ_EASY if QUIZ_STATE["phase"] == "easy" else QUIZ_HARD
        if QUIZ_STATE["index"] < len(qs):
            q = qs[QUIZ_STATE["index"]]
            phase_num = 1 if QUIZ_STATE["phase"] == "easy" else 2
            self._bot_say(
                f"🎮 Επίπεδο {phase_num} — Ερώτηση {QUIZ_STATE['index']+1}:\n"
                f"{q['question']}\n" + "\n".join(q["options"])
            )

    # ══════════════════════════════════════════════════
    # UC10 — Green Challenges
    # ══════════════════════════════════════════════════
    def show_challenges(self):
        self._clear()
        self._title("Πράσινες Προκλήσεις")
        self._subtitle("Περίπτωση Χρήσης 10")

        # Join
        card = self._card()
        ctk.CTkLabel(card, text="Δημιουργία Νέας Πρόκλησης", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(12, 4))
        goal_entry  = ctk.CTkEntry(card, placeholder_text="Στόχος (πχ. Recycle 10 bottles)", font=ctk.CTkFont(size=13))
        goal_entry.pack(fill="x", padx=14, pady=4)
        badge_entry = ctk.CTkEntry(card, placeholder_text="Έμβλημα (πχ. Eco Badge)", font=ctk.CTkFont(size=13))
        badge_entry.pack(fill="x", padx=14, pady=4)
        join_result = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=13))
        join_result.pack(anchor="w", padx=14, pady=2)

        def do_join():
            r = join_green_challenge(CITIZEN_ID, goal_entry.get(), badge_entry.get())
            if r["success"]:
                join_result.configure(text=f"✅ {r['message']}", text_color=GREEN)
                challenge_id_var.set(str(r["challenge_id"]))
            else:
                join_result.configure(text=f"❌ {r['message']}", text_color="#C0392B")
        ctk.CTkButton(card, text="Εγγραφή", command=do_join,
                      fg_color=GREEN, hover_color="#158A62", height=34).pack(padx=14, pady=(0, 12), fill="x")

        # Complete
        card2 = self._card()
        ctk.CTkLabel(card2, text="Ολοκλήρωση Πρόκλησης", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(12, 4))
        challenge_id_var = ctk.StringVar()
        id_entry = ctk.CTkEntry(card2, placeholder_text="ID Πρόκλησης", font=ctk.CTkFont(size=13), textvariable=challenge_id_var)
        id_entry.pack(fill="x", padx=14, pady=4)
        complete_result = ctk.CTkLabel(card2, text="", font=ctk.CTkFont(size=13))
        complete_result.pack(anchor="w", padx=14, pady=2)

        def do_complete():
            try:
                cid = int(id_entry.get())
            except ValueError:
                complete_result.configure(text="❌ Βάλε έναν αριθμό.", text_color="#C0392B")
                return
            r = complete_green_challenge(cid)
            col = GREEN if r["success"] else "#C0392B"
            complete_result.configure(text=("✅ " if r["success"] else "❌ ") + r["message"], text_color=col)
        ctk.CTkButton(card2, text="Ολοκλήρωση +50π.", command=do_complete,
                      fg_color=GREEN, hover_color="#158A62", height=34).pack(padx=14, pady=(0, 12), fill="x")

    # ══════════════════════════════════════════════════
    # UC11 & UC12 — Employee Panel
    # ══════════════════════════════════════════════════
    def show_employee(self):
        self._clear()
        self._title("Πίνακας Υπαλλήλου")
        self._subtitle("Περιπτώσεις Χρήσης 11 & 12")

        def _emp_card(title, placeholder, btn_text, action_fn):
            card = self._card()
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(12, 4))
            entry  = ctk.CTkEntry(card, placeholder_text=placeholder, font=ctk.CTkFont(size=13))
            entry.pack(fill="x", padx=14, pady=4)
            result = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=13), wraplength=580)
            result.pack(anchor="w", padx=14, pady=2)
            def do_action(e=entry, r=result, fn=action_fn):
                val = e.get().strip()
                try: val = int(val)
                except ValueError:
                    r.configure(text="❌ Βάλε αριθμό.", text_color="#C0392B"); return
                res = fn(val)
                col = GREEN if res.get("success") else "#C0392B"
                r.configure(text=("✅ " if res.get("success") else "❌ ") + res.get("message", ""), text_color=col)
            ctk.CTkButton(card, text=btn_text, command=do_action,
                          fg_color=GREEN, hover_color="#158A62", height=34).pack(padx=14, pady=(0, 12), fill="x")

        _emp_card("Αποκομιδή Κάδου (ΠΧ11)", "ID Κάδου", "Αποκομιδή ✓", lambda bid: complete_collection(101, bid))
        _emp_card("Δήλωση Βλάβης (ΠΧ11)",   "ID Κάδου", "Δήλωση Βλάβης ⚠️", lambda bid: report_bin_damage(101, bid))

        # UC12 — publish action
        card3 = self._card()
        ctk.CTkLabel(card3, text="Δημοσίευση Δράσης (ΠΧ12)", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(12, 4))
        action_entry = ctk.CTkEntry(card3, placeholder_text="Τίτλος δράσης", font=ctk.CTkFont(size=13))
        action_entry.pack(fill="x", padx=14, pady=4)
        pub_result = ctk.CTkLabel(card3, text="", font=ctk.CTkFont(size=13))
        pub_result.pack(anchor="w", padx=14, pady=2)

        def do_publish():
            title = action_entry.get().strip()
            if not title:
                pub_result.configure(text="❌ Βάλε τίτλο.", text_color="#C0392B"); return
            r = publish_environmental_action(101, title)
            pub_result.configure(text=f"✅ {r['message']}", text_color=GREEN)
        ctk.CTkButton(card3, text="Δημοσίευση", command=do_publish,
                      fg_color=GREEN, hover_color="#158A62", height=34).pack(padx=14, pady=(0, 12), fill="x")


# ── entry point ──────────────────────────────────────
if __name__ == "__main__":
    app = BinGoApp()
    app.mainloop()
