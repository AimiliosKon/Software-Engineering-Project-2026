# =====================================
# BinGo Project
# Use Cases 1,2,3
# Τεχνολογία Λογισμικού
# =====================================


class User:

    def __init__(self, name, email):
        self.name = name
        self.email = email


class GreenChallenge:

    def __init__(self, title):
        self.title = title


class Citizen(User):

    def __init__(
            self,
            name,
            email,
            total_points,
            total_recycling,
            badges):

        super().__init__(name, email)

        self.total_points = total_points
        self.total_recycling = total_recycling
        self.badges = badges

        self.challenges = []
        self.transactions = []

        self.location_enabled = True
        self.current_location = "Πάτρα"

    
    # ΠΕΡΙΠΤΩΣΗ ΧΡΗΣΗΣ 1
    

    def green_profile(self):

        print("\n==========================")
        print("ΠΕΡΙΠΤΩΣΗ ΧΡΗΣΗΣ 1")
        print("==========================")

        print("\nGREEN DASHBOARD")
        print("Όνομα:", self.name)
        print("Email:", self.email)
        print("Πόντοι:", self.total_points)
        print("Ανακύκλωση:", self.total_recycling, "kg")
        print("Εμβλήματα:", self.badges)

        print("\nΕνεργές προκλήσεις:")

        if len(self.challenges) == 0:
            print("Καμία ενεργή πρόκληση")

        else:

            for challenge in self.challenges:
                print("-", challenge.title)

        if self.total_recycling == 0:

            print("\nΕναλλακτική Ροή")
            print("Ο χρήστης δεν έχει δραστηριότητα")
            print("Προτείνεται πρώτο Scan")

        else:

            print("\nΣτατιστικά")

            print("Πλαστικό: 5kg")
            print("Χαρτί: 10kg")

            trees = self.total_recycling // 5
            water = self.total_recycling * 10

            print("\nΠεριβαλλοντικό Κέρδος")

            print("Σώσατε", trees, "δέντρα")

            print(
                "Εξοικονομήσατε",
                water,
                "λίτρα νερού"
            )

        print("\nΣυναλλαγές")

        for transaction in self.transactions:
            print(transaction)


class RecyclingBin:

    def __init__(
            self,
            bin_id,
            material_type,
            location,
            distance,
            capacity,
            available_slots,
            real_time_available,
            last_update,
            photos,
            reviews,
            bonus_points):

        self.bin_id = bin_id
        self.material_type = material_type
        self.location = location
        self.distance = distance
        self.capacity = capacity
        self.available_slots = available_slots
        self.real_time_available = real_time_available
        self.last_update = last_update
        self.photos = photos
        self.reviews = reviews
        self.bonus_points = bonus_points


class BinMap:

    def __init__(self):

        self.bins = []

    def add_bin(self, recycling_bin):

        self.bins.append(recycling_bin)

    # ====================
    # ΠΕΡΙΠΤΩΣΗ ΧΡΗΣΗΣ2
    # ====================

    def show_bin_locations(self, user):

        print("\n==========================")
        print("ΠΕΡΙΠΤΩΣΗ ΧΡΗΣΗΣ 2")
        print("==========================")

        if not user.location_enabled:

            print(
                "Παρακαλώ ενεργοποιήστε GPS"
            )

            return None

        print(
            "\nΤοποθεσία:",
            user.current_location
        )

        print(
            "\nΚοντινοί κάδοι:"
        )

        for recycling_bin in self.bins:

            print(
                recycling_bin.material_type,
                "-",
                recycling_bin.location,
                "-",
                recycling_bin.distance,
                "m"
            )

        sorted_bins = sorted(
            self.bins,
            key=lambda x: x.distance
        )

        selected_bin = sorted_bins[0]

        print(
            "\nΕπιλέχθηκε:"
        )

        print(
            selected_bin.material_type,
            "-",
            selected_bin.location
        )

        return selected_bin


class BinDetailsSystem:

    # ====================
    # ΠΕΡΙΠΤΩΣΗ ΧΡΗΣΗΣ 3
    # ====================

    def show_bin_details(
            self,
            recycling_bin):

        print("\n==========================")
        print("ΠΕΡΙΠΤΩΣΗ ΧΡΗΣΗΣ 3")
        print("==========================")

        if recycling_bin is None:

            print("Δεν βρέθηκε κάδος")

            return

        print("\nΣτοιχεία Κάδου")

        print(
            "ID:",
            recycling_bin.bin_id
        )

        print(
            "Υλικό:",
            recycling_bin.material_type
        )

        print(
            "Τοποθεσία:",
            recycling_bin.location
        )

        print(
            "Χωρητικότητα:",
            recycling_bin.capacity
        )

        if recycling_bin.real_time_available:

            print(
                "Διαθέσιμες θέσεις:",
                recycling_bin.available_slots
            )

        else:

            print(
                "Τελευταία ενημέρωση:",
                recycling_bin.last_update
            )

        print("\nΚριτικές")

        for review in recycling_bin.reviews:

            print("-", review)

        print(
            "\nBonus:",
            recycling_bin.bonus_points,
            "πόντοι"
        )


# ====================
# MAIN
# ====================

user1 = Citizen(
    "Αριάδνη Σεχάι",
    "ariadne@gmail.com",
    1500,
    25,
    ["Eco Starter", "Green Hero"]
)

challenge1 = GreenChallenge(
    "Recycle 10 plastic bottles"
)

user1.challenges.append(
    challenge1
)

user1.transactions.append(
    "+200 πόντοι"
)

user1.transactions.append(
    "-100 πόντοι"
)


bin1 = RecyclingBin(
    1,
    "Πλαστικό",
    "Πλατεία Γεωργίου",
    250,
    "100 λίτρα",
    4,
    True,
    "12/05/2026",
    ["photo1.jpg"],
    ["Καθαρό σημείο"],
    20
)

bin2 = RecyclingBin(
    2,
    "Χαρτί",
    "Αγίου Ανδρέου",
    500,
    "120 λίτρα",
    3,
    True,
    "12/05/2026",
    ["photo2.jpg"],
    ["Καλή κατάσταση"],
    15
)

bin3 = RecyclingBin(
    3,
    "Γυαλί",
    "Ρήγα Φεραίου",
    800,
    "80 λίτρα",
    2,
    False,
    "12/05/2026",
    ["photo3.jpg"],
    ["Λίγο μακριά"],
    10
)

bin_map = BinMap()

bin_map.add_bin(bin1)
bin_map.add_bin(bin2)
bin_map.add_bin(bin3)

details_system = BinDetailsSystem()

user1.green_profile()

selected_bin = bin_map.show_bin_locations(
    user1
)

details_system.show_bin_details(
    selected_bin
)
