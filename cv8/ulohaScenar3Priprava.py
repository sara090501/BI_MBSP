# Praktická Ambulancia ŽILINA
# fixnut celkovy pocet ludi v uzle - 100

import random
import matplotlib.pyplot as plt

# Hodiny od 9:00 (9) do 21:00 (21); posledná hodina je interval 20:00-21:00
hours = list(range(9, 22))  # 9, 10, ..., 21 (9 pm)

# Počty (alebo "váhy") príchodov v jednotlivých hodinách (sumár 100)
hour_counts = [14, 15, 13, 12, 11, 10,  5,  5,  4,  2,  2,  4,  3]

# Overíme, že súčet je skutočne 100
assert sum(hour_counts) == 100, "Súčet musí byť 100."

# Vytvoríme "váhovaný" zoznam hodín tak, aby sa v ňom každá hodina
# opakovala toľkokrát, koľko je v hour_counts.
arrival_hours = []
for h, count in zip(hours, hour_counts):
    arrival_hours.extend([h]*count)

# Teraz máme 100 hodnôt príchodov presne podľa našej tabuľky.
# Pre náhodné premiešanie poradia (aby nevychádzali v zoradenom tvare):
random.shuffle(arrival_hours)

# Môžete si pozrieť prvých pár hodnôt:
print("Náhodné príchody (ukážka 10):", arrival_hours[:10])

# Vykreslíme histogram. Pre krásny histogram môžeme použiť bins=range(9,23).
plt.figure()
plt.hist(arrival_hours, bins=range(9, 23), edgecolor='black', align='left')
plt.xlabel('Hodina dňa')
plt.ylabel('Počet príchodov')
plt.title('Histogram 100 príchodov (9:00 – 21:00)')
plt.xticks(range(9, 22))
plt.show()
