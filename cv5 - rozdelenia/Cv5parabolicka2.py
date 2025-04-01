#1. krok: vytvorenie fukncie paraboly f(x) = p(0,1) -> f(x) = a*x*(1-x)
#   -> integral od 0 po 1 z f(x) = a*x*(1-x) = 1 -> hladame a
#2. krok: vzorkovanie (x,y) patri (0,1) x (0,3/2) a y <= f(x) = a*x*(1-x) ... x patri do mnoziny
#3. krok: posuvanie a skalovanie mnoziny na interval od -3 po 7 -> f(x) = a*(7-x)*(7+x) = 1 -> a= 1100/3
#4. krok: vytvorenie histogramu

import random# Inicializácia prázdnych zoznamov pre xi a yimi_list = []ni_list = []# Pokračujeme, kým nezískame 1000 platných párovwhile len(mi_list) < 1000:    mi = random.uniform(-3, 7)  # Generovanie xi z [-3, 7]    ni = random.uniform(0, 147/1100)  # Generovanie yi z [0, 147/1100]    # Výpočet hodnoty 6 * xi * (1 - xi)    hodnota = 3/1100 * (7-mi)*(7+mi)    # Overenie, či yi je menšie ako vypočítaná hodnota    if ni < hodnota:        mi_list.append(mi)        ni_list.append(ni)# Výpis výsledkov – každé číslo na samostatnom riadkuprint("mi:")for mi in mi_list:    print(mi)print("\nni:")for ni in ni_list:    print(ni)
import random  # Import knižnice pre generovanie náhodných čísel

# Inicializácia prázdnych zoznamov pre mi a ni
mi_list = []
ni_list = []

# Pokračujeme, kým nezískame 1000 platných párov
while len(mi_list) < 1000:
    mi = random.uniform(-3, 7)  # Generovanie mi z [-3, 7]
    ni = random.uniform(0, 147 / 1100)  # Generovanie ni z [0, 147/1100]

    # Výpočet hodnoty 6 * mi * (1 - mi)
    hodnota = 3 / 1100 * (7 - mi) * (7 + mi)

    # Overenie, či ni je menšie ako vypočítaná hodnota
    if ni < hodnota:
        mi_list.append(mi)
        ni_list.append(ni)

# Výpis výsledkov – každé číslo na samostatnom riadku
print("mi:")
for mi in mi_list:
    print(mi)

print("\nni:")
for ni in ni_list:
    print(ni)
