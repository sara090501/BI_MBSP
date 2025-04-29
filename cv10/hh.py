import numpy as np
import matplotlib.pyplot as plt

# Parametre
N = 20000 # celkový počet obyvateľov
I0 = 1 # počet infikovaných na začiatku
R0 = 0 # počet uzdravených na začiatku
S0 = N - I0 - R0 # počet zdravých na začiatku

D = 5  # infekčné obdobie
R_0 = 4  # pôvodné reprodukčné číslo

gamma = 1 / D # rýchlosť uzdravenia
beta = R_0 * gamma # rýchlosť infekcie

days = 60 # počet dní simulácie
t = np.linspace(0, days, days) # časová os

# ===================== REALITA 1 – Bez zásahu =====================
S1 = np.zeros(days) # počet zdravých
I1 = np.zeros(days) # počet infikovaných
R1 = np.zeros(days) # počet uzdravených

S1[0] = S0 # začiatok simulácie
I1[0] = I0 # počet infikovaných na začiatku
R1[0] = R0 # počet uzdravených na začiatku

for day in range(1, days):
    dS = -beta * S1[day - 1] * I1[day - 1] / N
    dI = beta * S1[day - 1] * I1[day - 1] / N - gamma * I1[day - 1]
    dR = gamma * I1[day - 1]

    S1[day] = S1[day - 1] + dS
    I1[day] = I1[day - 1] + dI
    R1[day] = R1[day - 1] + dR

# ===================== REALITA 2 – Zásah po 10 dňoch =====================
S2 = np.zeros(days)
I2 = np.zeros(days)
R2 = np.zeros(days)

S2[0] = S0
I2[0] = I0
R2[0] = R0

for day in range(1, days):
    if day < 11:
        current_beta = beta  # normálny stav
    else:
        current_beta = beta * 0.5  # obmedzenie kontaktov

    dS = -current_beta * S2[day - 1] * I2[day - 1] / N
    dI = current_beta * S2[day - 1] * I2[day - 1] / N - gamma * I2[day - 1]
    dR = gamma * I2[day - 1]

    S2[day] = S2[day - 1] + dS
    I2[day] = I2[day - 1] + dI
    R2[day] = R2[day - 1] + dR

# ===================== REALITA 3 – Zásah po 10 dňoch + izolácia pri symptómoch =====================
S3 = np.zeros(days)
I3 = np.zeros(days)
R3 = np.zeros(days)

S3[0] = S0
I3[0] = I0
R3[0] = R0

for day in range(1, days):
    if day < 11:
        current_beta = beta  # normálny stav
    else:
        current_beta = beta * 0.5  # obmedzenie kontaktov

    # Ľudia s príznakmi (napr. vypadávanie vlasov) sa izolujú
    isolation_factor = 0.7 if day >= 11 else 1.0  # 70% zníženie šírenia po izolácii

    dS = -current_beta * S3[day - 1] * I3[day - 1] / N * isolation_factor
    dI = current_beta * S3[day - 1] * I3[day - 1] / N * isolation_factor - gamma * I3[day - 1]
    dR = gamma * I3[day - 1]

    S3[day] = S3[day - 1] + dS
    I3[day] = I3[day - 1] + dI
    R3[day] = R3[day - 1] + dR

# ===================== GRAFICKÉ POROVNANIE =====================
plt.figure(figsize=(12, 6))
plt.plot(t, I1, label='Infikovaní – bez zásahu', color='red')
plt.plot(t, I2, label='Infikovaní – po zásahu (od dňa 10)', color='green', linestyle='--')
plt.plot(t, I3, label='Infikovaní – po zásahu + izolácia pri symptómoch', color='blue', linestyle=':')
plt.xlabel('Dni')
plt.ylabel('Počet infikovaných')
plt.title('Porovnanie vývoja epidémie – realita vs. zásah')
plt.legend()
plt.grid()
plt.show()

# ===================== ODPOVEDE =====================
print("== PÔVODNÁ REALITA ==")
celkovo_nakazenych_1 = round(N - S1[-1])
print(f"Celkový počet nakazených: {celkovo_nakazenych_1}")
print(f"Maximum infikovaných na deň: {np.argmax(I1)}")
print(f"Počet infikovaných v ten deň: {int(np.max(I1))}")

print("\n== PARALELNÁ REALITA č.1 – zásah po 10 dňoch ==")
celkovo_nakazenych_2 = round(N - S2[-1])
print(f"Celkový počet nakazených: {celkovo_nakazenych_2}")
print(f"Maximum infikovaných na deň: {np.argmax(I2)}")
print(f"Počet infikovaných v ten deň: {int(np.max(I2))}")

print("\n== PARALELNÁ REALITA č.2 – zásah po 10 dňoch + izolácia pri symptómoch ==")
celkovo_nakazenych_3 = round(N - S3[-1])
print(f"Celkový počet nakazených: {celkovo_nakazenych_3}")
print(f"Maximum infikovaných na deň: {np.argmax(I3)}")
print(f"Počet infikovaných v ten deň: {int(np.max(I3))}")