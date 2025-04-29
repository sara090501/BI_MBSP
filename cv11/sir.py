import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Parametre
N_s0 = 1_500_000   # Počet vojakov na fronte
N_c0 = 100_000_000 # Počet civilistov v Európe
I_s0 = 1_000       # Začiatočný počet infikovaných vojakov
S_s0 = N_s0 - I_s0
R_s0 = 0
D_s0 = 0
S_c0 = N_c0
I_c0 = 0
R_c0 = 0
D_c0 = 0

gamma = 1/7            # Odchod z infikovaných (recovery + death)
beta_s = 2.0 * gamma   # Prenosová rýchlosť na fronte
beta_c = 1.6 * gamma   # Prenosová rýchlosť medzi civilistami
CFR_s = 0.08           # Mortalita vojakov
CFR_c = 0.025          # Mortalita civilistov

days = 200             # Celkový počet dní simulácie
migrate_start = 30     # Deň, kedy začína presun vojakov domov
m = 0.05               # Podiel vojakov presúvaných denne po migrate_start

# Polia pre ukladanie výsledkov
t = np.arange(days + 1)
S_s = np.zeros(days + 1)
I_s = np.zeros(days + 1)
R_s = np.zeros(days + 1)
D_s = np.zeros(days + 1)
S_c = np.zeros(days + 1)
I_c = np.zeros(days + 1)
R_c = np.zeros(days + 1)
D_c = np.zeros(days + 1)

# Začiatočné hodnoty
S_s[0], I_s[0], R_s[0], D_s[0] = S_s0, I_s0, R_s0, D_s0
S_c[0], I_c[0], R_c[0], D_c[0] = S_c0, I_c0, R_c0, D_c0

# Simulačná slučka
for day in range(days):
    # Aktuálne populácie
    N_s = S_s[day] + I_s[day] + R_s[day]
    N_c = S_c[day] + I_c[day] + R_c[day]

    # Nové infekcie, uzdravenia a úmrtia u vojakov
    new_inf_s = beta_s * S_s[day] * I_s[day] / N_s
    new_rec_s = gamma * (1 - CFR_s) * I_s[day]
    new_die_s = gamma * CFR_s * I_s[day]

    S_s[day+1] = S_s[day] - new_inf_s
    I_s[day+1] = I_s[day] + new_inf_s - new_rec_s - new_die_s
    R_s[day+1] = R_s[day] + new_rec_s
    D_s[day+1] = D_s[day] + new_die_s

    # Nové infekcie, uzdravenia a úmrtia u civilistov
    new_inf_c = beta_c * S_c[day] * I_c[day] / N_c if N_c > 0 else 0
    new_rec_c = gamma * (1 - CFR_c) * I_c[day]
    new_die_c = gamma * CFR_c * I_c[day]

    S_c[day+1] = S_c[day] - new_inf_c
    I_c[day+1] = I_c[day] + new_inf_c - new_rec_c - new_die_c
    R_c[day+1] = R_c[day] + new_rec_c
    D_c[day+1] = D_c[day] + new_die_c

    # Migrácia vojakov domov (po day >= migrate_start)
    if day >= migrate_start:
        mig_S = m * S_s[day+1]
        mig_I = m * I_s[day+1]
        mig_R = m * R_s[day+1]

        S_s[day+1] -= mig_S
        I_s[day+1] -= mig_I
        R_s[day+1] -= mig_R
        S_c[day+1] += mig_S
        I_c[day+1] += mig_I
        R_c[day+1] += mig_R

# Vykreslenie aktívnych infekcií s dvoma osami
g = plt.figure(figsize=(10,6))
ax1 = g.add_subplot(111)
ax2 = ax1.twinx()

ax1.plot(t, I_c, label='Civilisti')
ax2.plot(t, I_s, label='Vojaci', linestyle='--')

ax1.set_xlabel('Dni od začiatku epidémie')
ax1.set_ylabel('Aktívne infekcie civilistov')
ax2.set_ylabel('Aktívne infekcie vojakov')
ax1.set_title('SIRD model: Aktívne infekcie vojakov a civilistov')

# Kombinovaná legenda
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')
ax1.grid(True)
plt.show()

# Vytvorenie zhrnutia výsledkov
df_summary = pd.DataFrame({
    'Skupina': ['Vojaci', 'Civilisti'],
    'Celkové nakazení (R + D)': [R_s[-1] + D_s[-1], R_c[-1] + D_c[-1]],
    'Úmrtia (D)': [D_s[-1], D_c[-1]],
    'Vrchol infekcií (deň)': [int(t[np.argmax(I_s)]), int(t[np.argmax(I_c)])],
    'Max aktívne infekcie': [int(np.max(I_s)), int(np.max(I_c))]
})

print(df_summary.to_string(index=False))
