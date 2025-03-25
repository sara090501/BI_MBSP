import numpy as np
import matplotlib.pyplot as plt

# Parametre trojuholníkového rozdelenia (minimum, modus, maximum)
a, c, b = 0, 0.5, 1

# Počet generovaných čísel
num_samples = 10000

# Generovanie náhodných čísel z trojuholníkového rozdelenia
samples = np.random.triangular(a, c, b, num_samples)

# Výpis čísel do konzoly po jednom na riadok
for sample in samples:
    print(sample)

# Vizualizácia histogramu
plt.hist(samples, bins=10, density=True, alpha=0.75, color='blue', edgecolor='black')
plt.title("Histogram trojuholníkového rozdelenia")
plt.xlabel("Hodnota")
plt.ylabel("Hustota pravdepodobnosti")
plt.grid()
plt.show()
