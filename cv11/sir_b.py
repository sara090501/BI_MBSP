import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Parametre pre vojakov\
N_s0 = 1_500_000   # Počet vojakov na fronte
I_s0 = 1_000       # Začiatočný počet infikovaných vojakov
S_s0 = N_s0 - I_s0
R_s0 = 0
D_s0 = 0

gamma = 1/7            # Odchod z infikovaných (recovery + death)
beta_s = 2.0 * gamma   # Prenosová rýchlosť na fronte
CFR_s = 0.08           # Mortalita vojakov

# Parametre pre migráciu a civilistov
days_front = 30        # Dĺžka simulácie na fronte (dní)
m = 0.05               # Podiel vojakov presúvaných denne po skončení frontu
beta_c = 1.6 * gamma   # Prenosová rýchlosť medzi civilistami

# Polia pre výsledky vojakov na fronte
t_front = np.arange(days_front + 1)
S_s = np.zeros(days_front + 1)
I_s = np.zeros(days_front + 1)
R_s = np.zeros(days_front + 1)
D_s = np.zeros(days_front + 1)

# Začiatočné hodnoty pre vojakov
S_s[0], I_s[0], R_s[0], D_s[0] = S_s0, I_s0, R_s0, D_s0

# Simulácia na fronte (SIRD pre vojakov)
for day in range(days_front):
    N_s = S_s[day] + I_s[day] + R_s[day]
    new_inf_s = beta_s * S_s[day] * I_s[day] / N_s
    new_rec_s = gamma * (1 - CFR_s) * I_s[day]
    new_die_s = gamma * CFR_s * I_s[day]

    S_s[day+1] = S_s[day] - new_inf_s
    I_s[day+1] = I_s[day] + new_inf_s - new_rec_s - new_die_s
    R_s[day+1] = R_s[day] + new_rec_s
    D_s[day+1] = D_s[day] + new_die_s

# Aktívni infikovaní vojaci po 30 dňoch
daily_migrants_inf = m * I_s  # Počet infikovaných presúvaných denne

# Vykreslenie S, I, R, D na fronte
g = plt.figure(figsize=(12, 5))
ax1 = g.add_subplot(121)
ax1.plot(t_front, S_s, label='Zdraví (S)')
ax1.plot(t_front, I_s, label='Infikovaní (I)')
ax1.plot(t_front, R_s, label='Uzdravení (R)')
ax1.plot(t_front, D_s, label='Mŕtvi (D)')
ax1.set_xlabel('Dni na fronte')
ax1.set_ylabel('Počet vojakov')
ax1.set_title('SIRD: Vojaci na fronte (30 dní)')
ax1.legend()
ax1.grid(True)

# Vykreslenie migrácie infikovaných vojakov
t_mig = t_front
ax2 = g.add_subplot(122)
ax2.bar(t_mig, daily_migrants_inf)
ax2.set_xlabel('Dni po fronte')
ax2.set_ylabel('Infikovaní migranti')
ax2.set_title('Migrácia infikovaných vojakov (5% denne)')
ax2.grid(True)

plt.tight_layout()
plt.show()

# Zhrnutie: Koľko infikovaných sa pripojí k civilistom každý deň
migration_summary = pd.DataFrame({
    'Deň': t_mig,
    'Infikovaní migranti': daily_migrants_inf.astype(int)
})

print(migration_summary.to_string(index=False))

# Poznámka: Tieto infikované osoby môžu začať šíriť nákazu medzi civilistami s beta_c = {:.3f}'.format(beta_c)
