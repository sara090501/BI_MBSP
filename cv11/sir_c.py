import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Parametre
N_s0 = 1_500_000    # Počet vojakov na fronte
I_s0 = 1_000        # Počiatočný počet infikovaných vojakov
S_s0 = N_s0 - I_s0
R_s0 = 0
D_s0 = 0

N_c0 = 100_000_000  # Počet civilistov v Európe

gamma = 1/7          # Recovery + death rate
beta_s = 2.0 * gamma # Prenosová rýchlosť na fronte
beta_c_base = 1.6 * gamma  # Základné beta medzi civilistami
CFR_s = 0.08         # Mortalita vojakov
CFR_c = 0.025        # Mortalita civilistov

# Simulačné nastavenie
days_front = 30      # Dni na fronte
days_civ = 150       # Dni šírenia v civilnom obyvateľstve po migrácii
m = 0.05             # Percento vojakov presúvaných denne
intervention_delay = 5  # Dni od začiatku migrácie do zavedenia opatrení

# 1) Simulácia SIRD pre vojakov počas days_front
t_front = np.arange(days_front + 1)
S_s = np.zeros(days_front + 1)
I_s = np.zeros(days_front + 1)
R_s = np.zeros(days_front + 1)
D_s = np.zeros(days_front + 1)
S_s[0], I_s[0], R_s[0], D_s[0] = S_s0, I_s0, R_s0, D_s0
for day in range(days_front):
    N_s = S_s[day] + I_s[day] + R_s[day]
    new_inf = beta_s * S_s[day] * I_s[day] / N_s
    new_rec = gamma * (1 - CFR_s) * I_s[day]
    new_die = gamma * CFR_s * I_s[day]
    S_s[day+1] = S_s[day] - new_inf
    I_s[day+1] = I_s[day] + new_inf - new_rec - new_die
    R_s[day+1] = R_s[day] + new_rec
    D_s[day+1] = D_s[day] + new_die

# 2) Rozdelenie civilistov na dve skupiny: polovica s opatreniami, polovica bez
T = days_front + days_civ
t = np.arange(T + 1)
# Skupina A: bez opatrení
S_A = np.zeros(T + 1)
I_A = np.zeros(T + 1)
R_A = np.zeros(T + 1)
D_A = np.zeros(T + 1)
# Skupina B: s opatreniami
S_B = np.zeros(T + 1)
I_B = np.zeros(T + 1)
R_B = np.zeros(T + 1)
D_B = np.zeros(T + 1)

# Počiatočné hodnoty pred migráciou: polovica civilistov
S_A[0] = N_c0 / 2
S_B[0] = N_c0 / 2

# Počiatočná migrácia vojakov po dni_front
mig_S0 = m * S_s[-1]
mig_I0 = m * I_s[-1]
mig_R0 = m * R_s[-1]
# Rozdeľ migrantov polovica do A, polovica do B
delta_S = mig_S0 / 2
delta_I = mig_I0 / 2
delta_R = mig_R0 / 2
S_A[0] += delta_S
I_A[0] += delta_I
R_A[0] += delta_R
S_B[0] += delta_S
I_B[0] += delta_I
R_B[0] += delta_R

# 3) Simulácia šírenia v oboch skupinách s postupnou migráciou
for day in range(1, T+1):
    # denná migrácia vojakov k civilistom až do days_front
    if day <= days_front:
        mig_S = m * S_s[day]
        mig_I = m * I_s[day]
        mig_R = m * R_s[day]
    else:
        mig_S = mig_I = mig_R = 0
    # Pridanie migrantov rozdelených do dvoch skupín
    S_A[day-1] += mig_S/2
    I_A[day-1] += mig_I/2
    R_A[day-1] += mig_R/2
    S_B[day-1] += mig_S/2
    I_B[day-1] += mig_I/2
    R_B[day-1] += mig_R/2
    # Výpočet pre skupinu A (bez opatrení)
    N_A = S_A[day-1] + I_A[day-1] + R_A[day-1]
    new_inf_A = beta_c_base * S_A[day-1] * I_A[day-1] / N_A
    new_rec_A = gamma * (1 - CFR_c) * I_A[day-1]
    new_die_A = gamma * CFR_c * I_A[day-1]
    S_A[day] = S_A[day-1] - new_inf_A
    I_A[day] = I_A[day-1] + new_inf_A - new_rec_A - new_die_A
    R_A[day] = R_A[day-1] + new_rec_A
    D_A[day] = D_A[day-1] + new_die_A
    # Výpočet pre skupinu B (s opatreniami po intervention_delay)
    days_since_return = day - 1
    beta_eff = beta_c_base * 0.5 if days_since_return >= intervention_delay else beta_c_base
    N_B = S_B[day-1] + I_B[day-1] + R_B[day-1]
    new_inf_B = beta_eff * S_B[day-1] * I_B[day-1] / N_B
    new_rec_B = gamma * (1 - CFR_c) * I_B[day-1]
    new_die_B = gamma * CFR_c * I_B[day-1]
    S_B[day] = S_B[day-1] - new_inf_B
    I_B[day] = I_B[day-1] + new_inf_B - new_rec_B - new_die_B
    R_B[day] = R_B[day-1] + new_rec_B
    D_B[day] = D_B[day-1] + new_die_B

# 4) Analýza pre civilistov (rozdelené skupiny)
# Celkové úmrtia v oboch skupinách
total_deaths_A = D_A[-1]
total_deaths_B = D_B[-1]
# Vrchol pandémie (I) v oboch skupinách - len po začiatku migrácie (dni ≥ 1)
peak_day_A = np.argmax(I_A[1:]) + 1
peak_day_B = np.argmax(I_B[1:]) + 1
peak_count_A = int(I_A[peak_day_A])
peak_count_B = int(I_B[peak_day_B])

# Výpis len pre skupinu A a skupinu B (civilisti)
print(f"Skupina A (bez opatrení): úmrtia = {int(total_deaths_A):,}, vrchol I nastal v dni {peak_day_A} s {peak_count_A} aktívnymi infekciami")
print(f"Skupina B (s opatreniami): úmrtia = {int(total_deaths_B):,}, vrchol I nastal v dni {peak_day_B} s {peak_count_B} aktívnymi infekciami")

# Vykreslenie porovnania I a D pre civilistov
plt.figure(figsize=(12,6))
plt.subplot(2,1,1)
plt.plot(t, I_A, label='Bez opatrení')
plt.plot(t, I_B, label='S opatreniami', linestyle='--')
plt.ylabel('Aktívne infekcie (I)')
plt.legend()
plt.grid(True)

plt.subplot(2,1,2)
plt.plot(t, D_A, label='Bez opatrení')
plt.plot(t, D_B, label='S opatreniami', linestyle='--')
plt.xlabel('Dni od návratu')
plt.ylabel('Kumulatívne úmrtia (D)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
