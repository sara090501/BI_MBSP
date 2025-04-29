import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Parametre pre vojakov
N_s0 = 1_500_000   # Počet vojakov na fronte
I_s0 = 1_000       # Začiatočný počet infikovaných vojakov
S_s0 = N_s0 - I_s0
R_s0 = 0
D_s0 = 0

gamma = 1/7            # Odchod z infikovaných (recovery + death)
beta_s = 2.0 * gamma   # Prenosová rýchlosť na fronte
CFR_s = 0.08           # Mortalita vojakov

days_soldiers = 30     # Počet dní simulácie pred koncom vojny

# Polia pre ukladanie výsledkov
t = np.arange(days_soldiers + 1)
S_s = np.zeros(days_soldiers + 1)
I_s = np.zeros(days_soldiers + 1)
R_s = np.zeros(days_soldiers + 1)
D_s = np.zeros(days_soldiers + 1)

# Začiatočné hodnoty
S_s[0], I_s[0], R_s[0], D_s[0] = S_s0, I_s0, R_s0, D_s0

# Simulačná slučka pre vojakov (len front)
for day in range(days_soldiers):
    N_s = S_s[day] + I_s[day] + R_s[day]

    # Nové prípady, uzdravenia a úmrtia
    new_inf_s = beta_s * S_s[day] * I_s[day] / N_s
    new_rec_s = gamma * (1 - CFR_s) * I_s[day]
    new_die_s = gamma * CFR_s * I_s[day]

    S_s[day+1] = S_s[day] - new_inf_s
    I_s[day+1] = I_s[day] + new_inf_s - new_rec_s - new_die_s
    R_s[day+1] = R_s[day] + new_rec_s
    D_s[day+1] = D_s[day] + new_die_s

# Vykreslenie priebehov S, I, R, D pre vojakov
plt.figure(figsize=(10,6))
plt.plot(t, S_s, label='Zdraví (S)')
plt.plot(t, I_s, label='Infikovaní (I)')
plt.plot(t, R_s, label='Uzdravení (R)')
plt.plot(t, D_s, label='Mŕtvi (D)')
plt.xlabel('Dni pred koncom vojny')
plt.ylabel('Počet vojakov')
plt.title('SIRD model: Vojaci na fronte (prvých 30 dní)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Vytvorenie tabuľky výsledkov pre 30. deň
df_30 = pd.DataFrame({
    'Stav': ['Zdraví (S)', 'Infikovaní (I)', 'Uzdravení (R)', 'Mŕtvi (D)'],
    'Počet na deň 30': [
        int(S_s[-1]),
        int(I_s[-1]),
        int(R_s[-1]),
        int(D_s[-1])
    ]
})
print(df_30.to_string(index=False))
