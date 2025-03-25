import numpy as np
import matplotlib.pyplot as plt

# Definícia funkcie
def f(x):
    return 6*x*(x - 1) + 2

# Generovanie náhodných čísel
num_samples = 1000  # Počet generovaných čísel
x_values = np.random.uniform(0, 1, num_samples)
y_values = f(x_values)

# Výpis hodnôt do konzoly
print("x hodnoty:")
for x in x_values:
    print(f"{x:.4f}".replace('.', ','))

print("\nf(x) hodnoty:")
for y in y_values:
    print(f"{y:.4f}".replace('.', ','))

# Zobrazenie výsledkov
plt.scatter(x_values, y_values, color='b', label='f(x) values')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.title('Hodnoty funkcie f(x) pre náhodné x')
plt.legend()
plt.grid()
plt.show()