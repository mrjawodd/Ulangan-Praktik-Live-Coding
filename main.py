import random
import sys

# --- Game data classes ---
class Fish:
    def __init__(self, name, rarity, location):
        self.name = name
        self.rarity = rarity  # common, rare, legendary
        self.location = location

    def __str__(self):
        return f"{self.name} ({self.rarity})"


class Component:
    LEVELS = ["Basic", "Advanced", "Pro"]

    def __init__(self, kind: str):
        self.kind = kind
        self.level = 0

    @property
    def name(self):
        return self.LEVELS[self.level]

    def upgrade(self):
        if self.level < len(self.LEVELS) - 1:
            self.level += 1
            print(f"{self.kind} ditingkatkan menjadi {self.name}!")
        else:
            print(f"{self.kind} sudah pada level tertinggi.")


class Equipment:
    def __init__(self):
        self.rod = Component("Joran")
        self.hook = Component("Kail")
        self.line = Component("Senar")

    def upgrade(self, part: str):
        if part == "1":
            self.rod.upgrade()
        elif part == "2":
            self.hook.upgrade()
        elif part == "3":
            self.line.upgrade()
        else:
            print("Pilihan tidak valid.")

    def status(self):
        return (f"Joran: {self.rod.name}, Kail: {self.hook.name}, "
                f"Senar: {self.line.name}")

    def total_level(self):
        # used for fishing bonus
        return self.rod.level + self.hook.level + self.line.level


class Player:
    def __init__(self):
        self.equipment = Equipment()
        self.inventory = []
        self.missions = []
        self.unlocked_locations = ["Sungai"]

    def add_fish(self, fish):
        self.inventory.append(fish)
        print(f"Menangkap {fish}!")

    def show_inventory(self):
        if not self.inventory:
            print("Inventaris kosong.")
            return
        print("Inventaris ikan:")
        counts = {}
        for f in self.inventory:
            counts[str(f)] = counts.get(str(f), 0) + 1
        for name, qty in counts.items():
            print(f" - {name} x{qty}")

    def complete_mission(self, mission):
        if mission not in self.missions:
            return
        if mission.check(self):
            print(f"Misi '{mission.description}' selesai!")
            self.missions.remove(mission)
            mission.reward(self)


class Location:
    def __init__(self, name, fishes):
        self.name = name
        self.fishes = fishes  # list of Fish

    def fish(self, player):
        # determine caught fish based on equipment
        weights = []
        bonus_level = player.equipment.total_level()
        for fish in self.fishes:
            base = {"common": 60, "rare": 30, "legendary": 10}[fish.rarity]
            # equipment bonus: higher combined level increases chance for rare/legendary
            bonus = bonus_level * 3
            if fish.rarity == "rare":
                base += bonus
            elif fish.rarity == "legendary":
                base += bonus // 2
            weights.append(base)
        caught = random.choices(self.fishes, weights=weights, k=1)[0]
        player.add_fish(caught)


class Mission:
    def __init__(self, description, condition, reward_func):
        self.description = description
        self.condition = condition
        self.reward_func = reward_func

    def check(self, player):
        return self.condition(player)

    def reward(self, player):
        self.reward_func(player)


# Setup game data
locations = {
    "Sungai": Location("Sungai", [
        Fish("Ikan Mas", "common", "Sungai"),
        Fish("Lele", "common", "Sungai"),
        Fish("Toman", "rare", "Sungai"),
        Fish("Arwana", "legendary", "Sungai"),
    ]),
    "Danau": Location("Danau", [
        Fish("Ikan Mujair", "common", "Danau"),
        Fish("Nila", "common", "Danau"),
        Fish("Bawal", "rare", "Danau"),
        Fish("Gabus", "legendary", "Danau"),
    ]),
    "Laut": Location("Laut", [
        Fish("Kakap", "common", "Laut"),
        Fish("Kerapu", "common", "Laut"),
        Fish("Tuna", "rare", "Laut"),
        Fish("Marlin", "legendary", "Laut"),
    ]),
}

# define missions
missions_list = [
    Mission(
        "Tangkap 3 ikan rare",
        lambda p: len([f for f in p.inventory if f.rarity == "rare"]) >= 3,
        lambda p: p.unlocked_locations.append("Danau") if "Danau" not in p.unlocked_locations else None,
    ),
    Mission(
        "Tangkap ikan legendary",
        lambda p: any(f.rarity == "legendary" for f in p.inventory),
        lambda p: p.equipment.upgrade("1"),  # upgrade joran by default
    ),
]

# --- Game loop ---

def add_new_location(player):
    print("Masukkan nama lokasi baru:")
    name = input("> ").strip()
    if not name:
        print("Nama tidak boleh kosong.")
        return
    if name in locations:
        print("Lokasi sudah ada.")
        return
    # create simple default fish set for new location
    default_fish = [
        Fish(f"Ikan A-{i+1}", "common", name) for i in range(3)
    ]
    locations[name] = Location(name, default_fish)
    player.unlocked_locations.append(name)
    print(f"Lokasi '{name}' ditambahkan dan dibuka!")


def show_main_menu():
    print("\n=== Petualangan Mancing Nusantara ===")
    print("1. Berangkat memancing")
    print("2. Lihat inventaris")
    print("3. Periksa & tingkatkan peralatan")
    print("4. Periksa misi")
    print("5. Tambah lokasi baru")
    print("6. Keluar")


def show_equipment_menu(player):
    print("\nPeralatan saat ini:")
    print(player.equipment.status())
    print("Pilih bagian untuk ditingkatkan:")
    print("1. Joran")
    print("2. Kail")
    print("3. Senar")
    print("4. Kembali")
    choice = input("> ")
    if choice in ["1", "2", "3"]:
        player.equipment.upgrade(choice)
    elif choice == "4":
        return
    else:
        print("Pilihan tidak valid.")


def choose_location(player):
    print("Pilih lokasi:")
    for idx, name in enumerate(player.unlocked_locations, start=1):
        print(f"{idx}. {name}")
    print(f"{len(player.unlocked_locations)+1}. Batal")
    choice = input("> ")
    try:
        choice = int(choice)
    except ValueError:
        return None
    if 1 <= choice <= len(player.unlocked_locations):
        return locations[player.unlocked_locations[choice-1]]
    return None


def check_missions(player):
    if not player.missions:
        print("Tidak ada misi aktif.")
        return
    print("Misi aktif:")
    for m in player.missions:
        print(f" - {m.description}")
    # attempt to complete
    for m in list(player.missions):
        player.complete_mission(m)


def main():
    player = Player()
    player.missions.extend(missions_list)

    while True:
        show_main_menu()
        choice = input("Pilih aksi: ")
        if choice == "1":
            loc = choose_location(player)
            if loc:
                loc.fish(player)
                check_missions(player)
        elif choice == "2":
            player.show_inventory()
        elif choice == "3":
            show_equipment_menu(player)
        elif choice == "4":
            check_missions(player)
        elif choice == "5":
            add_new_location(player)
        elif choice == "6":
            print("Terima kasih telah bermain!")
            break
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()
