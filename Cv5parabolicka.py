import matplotlib.pyplot as plt
import numpy as np

# Funkcia f(x) = 6*x*(1-x)
def parabola_function(x):
    return 6 * x * (1 - x)

# Generovanie bodov pod parabolou metódou odmietania
def generate_parabola_points(n):
    points = []
    count = 0  # Počet vygenerovaných pokusov
    while len(points) < n:
        x = np.random.rand()
        y = np.random.rand() * 1.5  # Maximum f(x) = 1.5
        count += 1
        if y <= parabola_function(x):
            points.append(x)
    print(f"Celkový počet pokusov: {count}")
    return points

# Počet generovaných bodov
n = 1000
parabola_values = generate_parabola_points(n)

# Uistenie sa, že máme presne 1000 bodov
assert len(parabola_values) == n, "Generovaný zoznam nemá správny počet bodov."

# Vykreslenie histogramu
plt.hist(parabola_values, bins=20, edgecolor='black', alpha=0.75, density=True)
plt.xlabel("Hodnoty x")
plt.ylabel("Frekvencia")
plt.title("Histogram 1000 generovaných čísel pod parabolou f(x) = 6x(1-x)")
plt.show()

# Výpis hodnôt do konzoly pre kopírovanie
for value in parabola_values:
    print(f"{str(value).replace('.', ',')}")
