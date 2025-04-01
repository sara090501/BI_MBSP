import numpy as np
import matplotlib.pyplot as plt

N = 1000  # Počet simulácií
results = []

for _ in range(N):
    count = 0
    while np.random.rand() > 0.5:  # Simulujeme hádzanie, 50% šanca na číslo (T)
        count += 1
    results.append(count + 1)  # Počet čísiel pred prvým znakom

# Vykreslenie histogramu výsledkov
plt.hist(results, bins=range(1, max(results)+2), density=True, edgecolor='black', alpha=0.75)
plt.xlabel('Počet čísiel pred prvým znakom')
plt.ylabel('Pravdepodobnosť')
plt.title('Simulácia geometrického rozdelenia')
plt.xticks(range(1, max(results)+1))
plt.show()