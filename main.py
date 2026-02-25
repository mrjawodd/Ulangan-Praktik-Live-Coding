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


class Equipment:
    LEVELS = ["Basic", "Advanced", "Pro"]

    def __init__(self):
        self.level = 0

    @property
    def name(self):
        return self.LEVELS[self.level]

    def upgrade(self):
        if self.level < len(self.LEVELS) - 1:
            self.level += 1
            print(f"Peralatan ditingkatkan menjadi {self.name}!")
        else:
            print("Peralatan sudah paling tinggi.")


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
        for fish in self.fishes:
            base = {"common": 60, "rare": 30, "legendary": 10}[fish.rarity]
            # equipment bonus: higher level increases chance for rare/legendary
            bonus = player.equipment.level * 5
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
        lambda p: p.equipment.upgrade(),
    ),
]

# --- Game loop ---

def show_main_menu():
    print("\n=== Petualangan Mancing Nusantara ===")
    print("1. Berangkat memancing")
    print("2. Lihat inventaris")
    print("3. Periksa peralatan")
    print("4. Periksa misi")
    print("5. Keluar")


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
            print(f"Peralatan saat ini: {player.equipment.name}")
        elif choice == "4":
            check_missions(player)
        elif choice == "5":
            print("Terima kasih telah bermain!")
            break
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()
