import numpy as np
import matplotlib.pyplot as plt
import random

# =========================
# Parametre simulácie
# =========================
num_doctors = 4  # Počet doktorov
shift_duration = 4 * 60  # Dĺžka zmeny v minútach (4 hodiny = 240 minút)
BN = float('inf')  # Veľká hodnota – predstavuje "nekonečno"

# Parametre rozdelení
# Medzi príchodmi pacientov: trojuholníkové rozdelenie T(2,4,10) (min, mod, max)
arr_min = 2
arr_mode = 4
arr_max = 10

# Dĺžka vyšetrenia: exponenciálne rozdelenie Exp(20) (stupnica = 20 minút)
service_scale = 20

# Priorita pacientov:
# - s pravdepodobnosťou 50% (0.5) má prioritu 1 (mierny prípad)
# - s pravdepodobnosťou 33,33% (1/3) má prioritu 2 (závažný prípad)
# - s pravdepodobnosťou 16,67% (1/6) má prioritu 3 (urgentný prípad)
# POZN.: Vo výsledku sa pacienť s prioritou 3 vybavuje ako prvý.
priority_probabilities = [0.5, 1 / 3, 1 / 6]
priority_levels = [1, 2, 3]  # 3 = urgentný (najvyššia priorita)

# Upgrade: Requeue – pravdepodobnosť, že po vyšetrení sa pacient "zhorší" (0.1 = 10%)
requeue_prob = 0.1

# =========================
# Inicializácia stavov simulácie
# =========================

# Pre každého doktora:
# - doctor_finish_times: čas, kedy skončí jeho aktuálne vyšetrenie (inak BN = voľný)
# - doctor_busy_time: akumulovaný čas strávený vyšetrením
# - doctor_served_count: počet vykonaných vyšetrení
doctor_finish_times = [BN] * num_doctors
doctor_busy_time = [0.0] * num_doctors
doctor_served_count = [0] * num_doctors

# Prvá udalosť – príchod pacienta, vygenerovaný pomocou trojuholníkového rozdelenia
next_arrival = np.random.triangular(arr_min, arr_mode, arr_max)
if next_arrival > shift_duration:
    next_arrival = BN

# Čakáreň – pacienti sú rozdelení podľa priority (kľúče: 3, 2, 1)
# Vo vnútri jednotlivých zoznamov sa uchováva čas príchodu (FIFO)
waiting = {3: [], 2: [], 1: []}

# Pre grafy – zaznamenávanie vývoja v čase
# Graf 1: Počet pacientov v čakárni v čase
time_queue = [0]
queue_length_timeline = [0]

# Graf 2: Kumulatívny počet pacientov na urgentnom príjme v čase
time_cumulative = [0]
cumulative_arrivals = [0]
cumulative_total = 0  # celkový počet príchodov (včetně requeue)

# Aktuálny čas simulácie
current_time = 0

# =========================
# Hlavná slučka simulácie
# =========================
# Simulácia prebieha, kým neprídu žiadne nové udalosti (nové príchody, prebiehajúce vyšetrenia či čakajúci pacienti)
while not (next_arrival == BN and all(ft == BN for ft in doctor_finish_times)
           and (len(waiting[3]) + len(waiting[2]) + len(waiting[1]) == 0)):

    # Zistíme najbližší čas udalosti zo všetkých (príchod alebo dokončenie vyšetrenia)
    next_service = min(doctor_finish_times)

    # Udalosť príchodu má prioritu v prípade rovnosti
    if next_arrival <= next_service:
        # ----- UDALOSŤ: Príchod pacienta -----
        current_time = next_arrival

        # Vygenerujeme prioritu pacienta
        r = random.random()
        if r < priority_probabilities[0]:
            patient_priority = 1
        elif r < priority_probabilities[0] + priority_probabilities[1]:
            patient_priority = 2
        else:
            patient_priority = 3

        # Zvýšime počet príchodov a zaznamenáme kumulatívne údaje
        cumulative_total += 1
        time_cumulative.append(current_time)
        cumulative_arrivals.append(cumulative_total)

        # Skontrolujeme, či je niektorý doktor voľný.
        # Ak je viacero voľných doktorov, vyberieme toho, ktorý strávil vyšetrením najmenej času.
        free_doctors = [i for i, ft in enumerate(doctor_finish_times) if ft == BN]
        if free_doctors:
            chosen = min(free_doctors, key=lambda i: doctor_busy_time[i])
            service_time = np.random.exponential(scale=service_scale)
            doctor_finish_times[chosen] = current_time + service_time
            doctor_busy_time[chosen] += service_time
        else:
            # Všetci doktori sú zaneprázdnení – pacient ide do čakárne
            waiting[patient_priority].append(current_time)

        # Naplánujeme ďalší príchod, ak sa uskutoční do konca zmeny
        next_arrival_candidate = current_time + np.random.triangular(arr_min, arr_mode, arr_max)
        if next_arrival_candidate <= shift_duration:
            next_arrival = next_arrival_candidate
        else:
            next_arrival = BN

        # Aktualizujeme záznam o počte pacientov v čakárni
        total_wait = len(waiting[3]) + len(waiting[2]) + len(waiting[1])
        time_queue.append(current_time)
        queue_length_timeline.append(total_wait)

    else:
        # ----- UDALOSŤ: Dokončenie vyšetrenia -----
        # Zistíme, ktorý doktor má najbližšiu udalosť
        i = doctor_finish_times.index(next_service)
        current_time = doctor_finish_times[i]
        doctor_served_count[i] += 1  # vyšetrenie sa započíta

        # Upgrade: S pravdepodobnosťou 0.1 sa pacient zhorší a bude potrebovať opätovné vyšetrenie.
        if random.random() < requeue_prob:
            # Pacient, ktorý sa zhoršil, sa zaradí do čakárne s prioritou 3
            waiting[3].append(current_time)
            cumulative_total += 1
            time_cumulative.append(current_time)
            cumulative_arrivals.append(cumulative_total)

        # Ak čaká niekto v čakárni, vyberieme pacientov podľa najvyššej priority.
        if waiting[3]:
            arrival_time = waiting[3].pop(0)
        elif waiting[2]:
            arrival_time = waiting[2].pop(0)
        elif waiting[1]:
            arrival_time = waiting[1].pop(0)
        else:
            arrival_time = None

        if arrival_time is not None:
            # Priradíme čakajúceho pacienta doktorovi, ktorý práve uvoľnil ordináciu.
            service_time = np.random.exponential(scale=service_scale)
            doctor_finish_times[i] = current_time + service_time
            doctor_busy_time[i] += service_time
        else:
            # Ak nikto čaká, doktor sa stáva voľným.
            doctor_finish_times[i] = BN

        # Aktualizujeme záznam o počte pacientov v čakárni
        total_wait = len(waiting[3]) + len(waiting[2]) + len(waiting[1])
        time_queue.append(current_time)
        queue_length_timeline.append(total_wait)

# =========================
# Výpis výsledkov
# =========================
print("Štatistiky pre jednotlivých doktorov:")
for i in range(num_doctors):
    print(f"Doktor {i + 1}:")
    print(f"  Celkový čas vyšetrení (min): {doctor_busy_time[i]:.2f}")
    print(f"  Počet vykonaných vyšetrení: {doctor_served_count[i]}")
    utilization = doctor_busy_time[i] / shift_duration
    print(f"  Vyťaženosť: {utilization:.2%}")
    print("-" * 40)

# =========================
# Vykreslenie grafov
# =========================

# Graf 1: Počet pacientov v čakárni vs Čas
plt.figure(figsize=(10, 6))
plt.step(time_queue, queue_length_timeline, where='post')
plt.xlabel("Čas (min)")
plt.ylabel("Počet pacientov v čakárni")
plt.title("Vývoj počtu pacientov v čakárni")
plt.grid(True)
plt.tight_layout()
plt.show()

# Graf 2: Kumulatívny počet pacientov na urgentnom príjme vs Čas
plt.figure(figsize=(10, 6))
plt.step(time_cumulative, cumulative_arrivals, where='post')
plt.xlabel("Čas (min)")
plt.ylabel("Celkový počet pacientov")
plt.title("Kumulatívny počet pacientov na urgentnom príjme")
plt.grid(True)
plt.tight_layout()
plt.show()
