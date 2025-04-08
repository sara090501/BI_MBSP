import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt

# Konštanty
c = 4               # počet lekárov
tau = 240           # dĺžka simulácie
BN = 1_000_000      # veľké číslo pre ukončenie udalosti

# Distribúcie príchodu a služby
arr_low, arr_high = 3, 7
srv_low, srv_high = 15, 25

# Zoznamy pre štatistiky z behov
pvp_list = []           # počet vyšetrených pacientov pre každý beh
px_list = []            # priemerná vyťaženosť doktorov pre každý beh
pcd_list = []           # priemerná čakacia doba pacientov pre každý beh
x_i_list = []           # vyťaženosti každého doktora pre každý beh
cdp_list_all = []       # čakacie doby všetkých pacientov pre každý beh

# Spusti 10 behov
for run in range(10):
    # Inicializácia pre jeden beh
    l = 0
    x = [0] * c
    server_busy_time = [0.0] * c
    queue = []
    served_times = []       # čakacie doby každého pacienta

    # Generátory
    rv = stats.uniform(loc=arr_low, scale=arr_high - arr_low)
    sj = stats.uniform(loc=srv_low, scale=srv_high - srv_low)

    cal = [rv.rvs()] + [BN] * c
    t = 0

    while t < tau or l > 0:
        min_value = min(cal)
        M = cal.index(min_value)
        t = min_value

        if M == 0:
            # Príchod pacienta
            l += 1
            next_arrival = t + rv.rvs()
            cal[0] = next_arrival if next_arrival < tau else BN

            free_server = next((i for i in range(c) if x[i] == 0), -1)

            if free_server != -1:
                x[free_server] = 1
                service_time = sj.rvs()
                cal[free_server + 1] = t + service_time
                server_busy_time[free_server] += service_time
                served_times.append(0.0)  # nečakal
            else:
                queue.append(t)  # čaká vo fronte

        else:
            # Ukončenie služby
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

    # Vyhodnotenie štatistík
    pvp = len(served_times)
    x_i = [round(t_busy / tau, 4) for t_busy in server_busy_time]
    px = sum(server_busy_time) / (c * tau)
    pcd = sum(served_times) / pvp if pvp > 0 else 0

    # Uloženie do zoznamov
    pvp_list.append(pvp)
    px_list.append(px)
    pcd_list.append(pcd)
    x_i_list.append(x_i)
    cdp_list_all.append(served_times)

    # Výpis pre tento beh
    print(f"\n--- Beh {run + 1} ---")
    print(f"Počet vyšetrených pacientov (pvp): {pvp}")
    print(f"Vyťaženosti doktorov (x_i): {x_i}")
    print(f"Priemerná vyťaženosť (px): {px:.4f}")
    print(f"Priemerná čakacia doba (pcd): {pcd:.4f}")
    print("-" * 40)

# Výpočty po 10 behoch
ppvp = sum(pvp_list) / 10
pvd = sum(px_list) / 10
cpcd = sum(pcd_list) / 10

# Výpis finálnych štatistík
print("\n=== PRIEMERY PO 10 BEHOCH ===")
print(f"Priemerný počet vyšetrených pacientov (ppvp): {ppvp:.2f}")
print(f"Priemerná vyťaženosť doktorov (pvd): {pvd:.4f}")
print(f"Celková priemerná čakacia doba (cpcd): {cpcd:.4f}")
