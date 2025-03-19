import matplotlib.pyplot as plt

class LinearCongruentialGenerator:
    def __init__(self, seed=123, a=134775813, c=1, m=2 ** 32):
        self.a = a
        self.c = c
        self.m = m
        self.zn = seed

    def next(self):
        self.zn = (self.a * self.zn + self.c) % self.m
        return self.zn / (self.m - 1)

    def get_sequence(self, n):
        return [self.next() for _ in range(n)]

    def get_average(self, n):
        sequence = self.get_sequence(n)
        return sum(sequence) / n if n > 0 else 0

    def plot_histogram(self, n, bins=10):
        sequence = self.get_sequence(n)
        plt.hist(sequence, bins=bins, edgecolor='black', alpha=0.75)
        plt.xlabel("Hodnoty")
        plt.ylabel("Frekvencia")
        plt.title(f"Histogram {n} generovaných čísel")
        plt.show()

# Príklad použitia
generator = LinearCongruentialGenerator()
numbers = generator.get_sequence(500)
print(numbers)
print("Priemer:", generator.get_average(500))

generator.plot_histogram(1000)
