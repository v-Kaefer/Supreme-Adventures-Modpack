import collections

def check_repetitions(names):
    counter = collections.Counter(names)
    repetitions = [name for name, count in counter.items() if count > 1]
    return repetitions

names = [
    "JEI",
    "REI",
    "EMI",
    "NEI",
    "JourneyMap",
    "Voxel's Map",
    "Antique Atlas",
    "Map Atlases",
    "FTB Chunks",
]

repetitions = check_repetitions(names)

if repetitions:
    with open("repetitions.txt", "w") as file:
        file.write("Repetitions found:\n")
        for name in repetitions:
            file.write(name + "\n")
else:
    with open("repetitions.txt", "w") as file:
        file.write("No repetitions found.\n")