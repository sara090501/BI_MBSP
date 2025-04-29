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
S_c0 = N_c0
I_c0 = 0
R_c0 = 0
D_c0 = 0

gamma = 1/7          # Recovery + death rate
beta_s = 2.0 * gamma # Prenosová rýchlosť na fronte
CFR_s = 0.08         # Mortalita vojakov
CFR_c = 0.025        # Mortalita civilistov

# Simulačné nastavenie
days_front = 30      # Dni na fronte
days_civ = 150       # Dni šírenia v civilnom obyvateľstve po migrácii
m = 0.05             # Percento vojakov presúvaných denne
beta_c_base = 1.6 * gamma  # Základné beta medzi civilistami
intervention_delay = 5      # Dni od začiatku migrácie do zavedenia opatrení

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

# 2) Príprava polí pre civilné prostredie
T = days_front + days_civ
t = np.arange(T + 1)
S_c_no = np.zeros(T + 1)
I_c_no = np.zeros(T + 1)
R_c_no = np.zeros(T + 1)
D_c_no = np.zeros(T + 1)
S_c_int = np.zeros(T + 1)
I_c_int = np.zeros(T + 1)
R_c_int = np.zeros(T + 1)
D_c_int = np.zeros(T + 1)

# Začiatočné hodnoty po migrácii prvých vojakov
S_c_no[0] = S_c0 + m * S_s[-1]
I_c_no[0] = I_c0 + m * I_s[-1]
R_c_no[0] = R_c0 + m * R_s[-1]
D_c_no[0] = D_c0 + m * D_s[-1]
S_c_int[0], I_c_int[0], R_c_int[0], D_c_int[0] = S_c_no[0], I_c_no[0], R_c_no[0], D_c_no[0]

# Migrácia a šírenie v civilnom prostredí
for day in range(1, T+1):
    if day <= days_front:
        mig_S = m * S_s[day]
        mig_I = m * I_s[day]
        mig_R = m * R_s[day]
    else:
        mig_S = mig_I = mig_R = 0
    # Scenár bez opatrení
    N_c = S_c_no[day-1] + I_c_no[day-1] + R_c_no[day-1]
    new_inf_no = beta_c_base * S_c_no[day-1] * I_c_no[day-1] / N_c
    new_rec_no = gamma * (1 - CFR_c) * I_c_no[day-1]
    new_die_no = gamma * CFR_c * I_c_no[day-1]
    S_c_no[day] = S_c_no[day-1] - new_inf_no + mig_S
    I_c_no[day] = I_c_no[day-1] + new_inf_no - new_rec_no - new_die_no + mig_I
    R_c_no[day] = R_c_no[day-1] + new_rec_no + mig_R
    D_c_no[day] = D_c_no[day-1] + new_die_no
    # Scenár s opatreniami
    days_since_return = day - 1
    beta_eff = beta_c_base * 0.5 if days_since_return >= intervention_delay else beta_c_base
    N_ci = S_c_int[day-1] + I_c_int[day-1] + R_c_int[day-1]
    new_inf_i = beta_eff * S_c_int[day-1] * I_c_int[day-1] / N_ci
    new_rec_i = gamma * (1 - CFR_c) * I_c_int[day-1]
    new_die_i = gamma * CFR_c * I_c_int[day-1]
    S_c_int[day] = S_c_int[day-1] - new_inf_i + mig_S
    I_c_int[day] = I_c_int[day-1] + new_inf_i - new_rec_i - new_die_i + mig_I
    R_c_int[day] = R_c_int[day-1] + new_rec_i + mig_R
    D_c_int[day] = D_c_int[day-1] + new_die_i

# Vrchol infekcií u vojakov
npeak = np.argmax(I_s)
peak_count = I_s[npeak]
print(f"Vrchol aktívnych infekcií vojakov nastal v dni {npeak} s počtom {int(peak_count)} vojakov.")

# Analýza výsledkov
# Celkové úmrtia
total_deaths_no = D_c_no[-1]
total_deaths_int = D_c_int[-1]
diff_deaths = total_deaths_no - total_deaths_int
percent_diff = diff_deaths / total_deaths_no * 100
# Vrchol pandémie
day_peak_no = np.argmax(I_c_no)
day_peak_int = np.argmax(I_c_int)

print(f"Úmrtia bez opatrení: {int(total_deaths_no):,}")
print(f"Úmrtia s opatreniami: {int(total_deaths_int):,}")
print(f"Rozdiel v úmrtiach: {int(diff_deaths):,} ({percent_diff:.2f} % zníženie)")
print(f"Vrchol pandémie bez opatrení nastal v dni {day_peak_no}")
print(f"Vrchol pandémie s opatreniami nastal v dni {day_peak_int}")

# Vykreslenie porovnávacích grafov
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.plot(t, I_c_no, label='Bez opatrení')
plt.plot(t, I_c_int, label='S opatreniami', linestyle='--')
plt.xlabel('Dni od začiatku návratu')
plt.ylabel('Aktívne infekcie (I)')
plt.title('Civilné infekcie: bez vs. s opatreniami')
plt.legend()
plt.grid(True)

plt.subplot(1,2,2)
plt.plot(t, D_c_no, label='Bez opatrení')
plt.plot(t, D_c_int, label='S opatreniami', linestyle='--')
plt.xlabel('Dni od začiatku návratu')
plt.ylabel('Kumulatívne úmrtia (D)')
plt.title('Civilné úmrtia: bez vs. s opatreniami')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
