import random
import matplotlib.pyplot as plt


def generate_points(n):
    points = []
    for _ in range(n):
        x = random.uniform(0, 1)  # x v rozsahu [0, 1]
        y = random.uniform(0, 2)  # y v rozsahu [0, 2]

        if y <= 2 * x:  # Podmienka pre zaradenie bodu
            points.append((x, y))

    return points


# Generujeme 100 bodov
valid_points = generate_points(1000)

# Výpis výsledných bodov
for point in valid_points:
    print(point)

# Vykreslenie bodového grafu
x_values, y_values = zip(*valid_points)
plt.scatter(x_values, y_values, color='blue', marker='o', alpha=0.6)
plt.xlabel('Hodnoty x')
plt.ylabel('Hodnoty y')
plt.title('Bodový graf platných bodov')
plt.show()
