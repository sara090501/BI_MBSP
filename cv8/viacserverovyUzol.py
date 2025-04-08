import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt

# ====================
# Časť 1: Simulácie pre c = 4 a grafy pre jednotlivé behy
# ====================

c = 4  # počet lekárov
tau = 480  # dĺžka simulácie
BN = 1_000_000  # veľká hodnota pre ukončenie udalostí

# Parametre rozdelení (príchod a služba)
arr_low, arr_high = 3, 7
srv_low, srv_high = 15, 25

# Počet simulovaných behov
n_runs = 20

# Zoznamy pre celkové štatistiky zo všetkých behov
global_pvp_list = []  # počet vyšetrených pacientov (pvp)
global_px_list = []  # priemerná vyťaženosť (px)
global_pcd_list = []  # priemerná čakacia doba (pcd)
global_x_list = []  # zoznam vyťaženosti každého lekára pre každý beh

for run in range(n_runs):
    # Inicializácia stavov pre jeden beh
    l = 0  # počet úloh v systéme (v uzle)
    x = [0] * c  # stav lekárov (0 - voľný, 1 - zaneprázdnený)
    server_busy_time = [0.0] * c  # obsadený čas pre každého lekára
    served_count = [0] * c  # počet obslúžených pacientov pre každého lekára
    queue = []  # fronta – uchováva časy príchodu pacientov
    served_times = []  # čakacie doby obslúžených pacientov

    # Zoznamy pre grafy zaznamenávajúce priebeh simulácie (index udalosti)
    jobs_in_node_run = []  # počet úloh v uzle
    jobs_in_queue_run = []  # počet úloh vo fronte
    # Pre kumulatívny počet vykonaných úloh pre jednotlivých lekárov (každý zoznam patrí jednému lekárovi)
    cumulative_served = [[] for _ in range(c)]

    # Inicializácia generátorov príchodov a služieb
    rv = stats.uniform(loc=arr_low, scale=arr_high - arr_low)
    sj = stats.uniform(loc=srv_low, scale=srv_high - srv_low)

    # Kalendár udalostí: index 0 = príchod, nasledovné indexy = ukončenie služby jednotlivých lekárov
    cal = [rv.rvs()] + [BN] * c
    t = 0  # aktuálny čas

    # Zaznamenáme počiatočné stavy pred začiatkom udalostí
    jobs_in_node_run.append(l)
    jobs_in_queue_run.append(len(queue))
    for d in range(c):
        cumulative_served[d].append(0)

    # Spustenie simulácie – pokračujeme, kým aktuálny čas < tau alebo ešte nie sú obslúžení všetci pacienti
    while t < tau or l > 0:
        min_value = min(cal)
        M = cal.index(min_value)
        t = min_value

        if M == 0:
            # Príchod nového pacienta
            l += 1
            next_arrival = t + rv.rvs()
            cal[0] = next_arrival if next_arrival < tau else BN

            free_server = next((i for i in range(c) if x[i] == 0), -1)
            if free_server != -1:
                # Pacient sa obsluhuje okamžite
                x[free_server] = 1
                service_time = sj.rvs()
                cal[free_server + 1] = t + service_time
                server_busy_time[free_server] += service_time
                served_times.append(0.0)
            else:
                # Pacient ide do fronty
                queue.append(t)

        else:
            # Ukončenie služby na danom lekárovi
            l -= 1
            server_id = M - 1
            served_count[server_id] += 1

            if queue:
                entry_time = queue.pop(0)
                wait_time = t - entry_time
                served_times.append(wait_time)
                service_time = sj.rvs()
                cal[M] = t + service_time
                server_busy_time[server_id] += service_time
            else:
                x[server_id] = 0
                cal[M] = BN

        # Zaznamenanie údajov pre grafy
        jobs_in_node_run.append(l)
        jobs_in_queue_run.append(len(queue))
        for d in range(c):
            cumulative_served[d].append(served_count[d])

    # Vyhodnotenie štatistík pre daný beh
    pvp = len(served_times)
    # Vyťaženosť každého lekára – môže byť vyššia ako 1, keďže služba prebieha až po tau
    x_i = [round(t_busy / tau, 4) for t_busy in server_busy_time]
    # Priemerná vyťaženosť systémom (všetkých lekárov)
    px = sum(server_busy_time) / (c * tau)
    pcd = sum(served_times) / pvp if pvp > 0 else 0

    # Uloženie štatistík do globálnych zoznamov
    global_pvp_list.append(pvp)
    global_px_list.append(px)
    global_pcd_list.append(pcd)
    global_x_list.append(x_i)

    # Vykreslenie grafov pre aktuálny beh
    # Graf 1: Počet úloh v uzle
    plt.figure(figsize=(8, 5))
    plt.plot(jobs_in_node_run, label="Úlohy v uzle", color='blue')
    plt.title(f"Beh {run + 1}: Počet úloh v uzle")
    plt.xlabel("Udalosť (index)")
    plt.ylabel("Počet úloh")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Graf 2: Počet úloh vo fronte
    plt.figure(figsize=(8, 5))
    plt.plot(jobs_in_queue_run, label="Úlohy vo fronte", color='orange')
    plt.title(f"Beh {run + 1}: Počet úloh vo fronte")
    plt.xlabel("Udalosť (index)")
    plt.ylabel("Počet úloh vo fronte")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Graf 3: Kumulatívny počet obslúžených pacientov pre jednotlivých lekárov
    plt.figure(figsize=(8, 5))
    for d in range(c):
        plt.plot(cumulative_served[d], label=f"Lekár {d + 1}")
    plt.title(f"Beh {run + 1}: Kumulatívny počet obslúžených pacientov")
    plt.xlabel("Udalosť (index)")
    plt.ylabel("Kumulatívny počet pacientov")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Výpis štatistík pre aktuálny beh
    print(f"--- Beh {run + 1} ---")
    print(f"Počet vyšetrených pacientov (pvp): {pvp}")
    print(f"Vyťaženosť lekárov (x_i): {x_i}")
    print(f"Priemerná vyťaženosť (px): {px:.4f}")
    print(f"Priemerná čakacia doba (pcd): {pcd:.4f}")
    print("-" * 40)

# ====================
# Výpočet a výpis priemerov zo všetkých 10 behoch (pre c = 4)
# ====================

# Priemerný počet vyšetrených pacientov, priemerná vyťaženosť a priemerná čakacia doba zo všetkých behov
ppvp = sum(global_pvp_list) / len(global_pvp_list)
pvd = sum(global_px_list) / len(global_px_list)
cpcd = sum(global_pcd_list) / len(global_pcd_list)

print("\n=== PRIEMERNÉ HODNOTY ZE VŠETKÝCH 20 BEHOV (c = 4) ===")
print(f"Priemerný počet vyšetrených pacientov (ppvp): {ppvp:.2f}")
print(f"Celková priemerná vyťaženosť (pvd): {pvd:.4f}")
print(f"Celková priemerná čakacia doba (cpcd): {cpcd:.4f}")

# Výpočet priemernej vyťažnosti pre jednotlivých lekárov zo všetkých 10 behov
avg_utilization_per_doctor = []
for i in range(c):
    # Pre každého lekára spočítame súčet vyťaženosť z každého behu a vydelíme počtom behov
    avg_util = sum(run_util[i] for run_util in global_x_list) / n_runs
    avg_utilization_per_doctor.append(round(avg_util, 4))

print("Priemerná vyťaženosť jednotlivých lekárov zo všetkých 10 behov:")
for i, avg_util in enumerate(avg_utilization_per_doctor, start=1):
    print(f"Lekár {i}: {avg_util}")

# ====================
# Časť 2: Závislosť priemernej čakacej doby od počtu lekárov
# ====================

# Pre rôzne hodnoty c (počet lekárov) vykonáme simulácie a spočítame priemernú čakaciu dobu.
c_values = list(range(1, 11))
n_simulations = 10  # počet simulácií pre každú hodnotu c
avg_waiting_times = []


def simulacia_behu(c, tau, BN, arr_low, arr_high, srv_low, srv_high):
    """Pre daný počet lekárov vykoná jednu simuláciu a vráti priemernú čakaciu dobu."""
    l = 0
    x = [0] * c
    server_busy_time = [0.0] * c
    queue = []
    served_times = []

    rv = stats.uniform(loc=arr_low, scale=arr_high - arr_low)
    sj = stats.uniform(loc=srv_low, scale=srv_high - srv_low)

    cal = [rv.rvs()] + [BN] * c
    t = 0
    while t < tau or l > 0:
        min_value = min(cal)
        M = cal.index(min_value)
        t = min_value

        if M == 0:
            l += 1
            next_arrival = t + rv.rvs()
            cal[0] = next_arrival if next_arrival < tau else BN

            free_server = next((i for i in range(c) if x[i] == 0), -1)
            if free_server != -1:
                x[free_server] = 1
                service_time = sj.rvs()
                cal[free_server + 1] = t + service_time
                server_busy_time[free_server] += service_time
                served_times.append(0.0)
            else:
                queue.append(t)
        else:
            l -= 1
            server_id = M - 1
            if queue:
                entry_time = queue.pop(0)
                wait_time = t - entry_time
                served_times.append(wait_time)
                service_time = sj.rvs()
                cal[M] = t + service_time
                server_busy_time[server_id] += service_time
            else:
                x[server_id] = 0
                cal[M] = BN
    return sum(served_times) / len(served_times) if served_times else 0


# Simulácie pre rôzne hodnoty c
for c_current in c_values:
    waiting_times = []
    for _ in range(n_simulations):
        pcd = simulacia_behu(c_current, tau, BN, arr_low, arr_high, srv_low, srv_high)
        waiting_times.append(pcd)
    avg_waiting_times.append(sum(waiting_times) / n_simulations)

# Vykreslenie grafu 4: Závislosť priemernej čakacej doby od počtu lekárov
plt.figure(figsize=(8, 5))
plt.plot(c_values, avg_waiting_times, marker='o', linestyle='-')
plt.title("Závislosť priemernej čakacej doby od počtu lekárov")
plt.xlabel("Počet lekárov (c)")
plt.ylabel("Priemerná čakacia doba")
plt.grid(True)
plt.tight_layout()
plt.show()
