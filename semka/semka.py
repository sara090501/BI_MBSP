# ===== Nastaviteľné parametre simulácie =====
num_doctors      = 4            # počet doktorov
shift_duration   = 240          # dĺžka zmeny v minútach (4 hodiny)
arrival_interval = 4           # čas medzi príchodmi pacienta v minútach
service_duration = 15.0          # dĺžka vyšetrenia v minútach
n_simulations    = 30           # počet simulačných behoov
BN               = 1_000_000      # veľká hodnota pre ukončenie udalostí
# ==============================================

# Globálne zoznamy pre štatistiky každého behu
global_pvp_list = []  # počet vyšetrených pacientov v danom behu
global_px_list = []   # priemerná vyťaženosť pre daný beh
global_pcd_list = []  # priemerná čakacia doba pre daný beh

for run in range(n_simulations):
    # Inicializácia stavu simulácie pre jeden beh
    l = 0                                      # aktuálny počet pacientov v systéme (čekáreň + vyšetrenie)
    x = [0] * num_doctors                      # stav jednotlivých doktorov (0 - voľný, 1 - zaneprázdnený)
    server_busy_time = [0.0] * num_doctors       # kumulatívny čas vyšetrení pre každého doktora
    served_count = [0] * num_doctors             # počet pacientov, ktorých daný doktor vyšetril
    queue = []                                 # čakáreň – uchováva časy príchodov pacientov
    served_times = []                          # čakacie doby obslúžených pacientov

    # Kalendár udalostí: index 0 = príchod pacienta, index 1..num_doctors = ukončenie vyšetrenia u jednotlivých doktorov.
    # Prvý príchod je naplánovaný na arrival_interval minút.
    cal = [arrival_interval] + [BN] * num_doctors
    t = 0  # aktuálny čas simulácie

    # Simulácia pokračuje, kým je čas < shift_duration alebo ešte zostali pacienti (v systéme)
    while t < shift_duration or l > 0:
        min_value = min(cal)
        M = cal.index(min_value)
        t = min_value

        if M == 0:
            # Udalosť: príchod pacienta
            l += 1
            # Naplánovanie ďalšieho príchodu (iba ak sa uskutoční pred koncom zmeny)
            next_arrival = t + arrival_interval
            cal[0] = next_arrival if next_arrival < shift_duration else BN

            # Ak je aspoň jeden doktor voľný, pacient sa obslúži okamžite
            free_server = next((i for i in range(num_doctors) if x[i] == 0), -1)
            if free_server != -1:
                x[free_server] = 1
                cal[free_server + 1] = t + service_duration
                server_busy_time[free_server] += service_duration
                served_times.append(0.0)  # čakacia doba je 0, pacient sa obsluhuje okamžite
                served_count[free_server] += 1
            else:
                # Všetci doktori sú zaneprázdnení – pacient ide do čakárne
                queue.append(t)
        else:
            # Udalosť: ukončenie vyšetrenia u doktora M-1
            l -= 1
            server_id = M - 1
            if queue:
                # Ak čakáreň nie je prázdna, vyberieme pacienta, ktorý čakal najdlhšie (FIFO)
                entry_time = queue.pop(0)
                wait_time = t - entry_time
                served_times.append(wait_time)
                cal[M] = t + service_duration
                server_busy_time[server_id] += service_duration
                served_count[server_id] += 1
            else:
                # Ak je čakáreň prázdna, doktor sa uvoľní
                x[server_id] = 0
                cal[M] = BN

    # Vyhodnotenie štatistík pre daný beh
    pvp = len(served_times)   # počet vyšetrených pacientov
    # Vyťaženosť každého doktora – pomer času stráveného vyšetrením voči dĺžke zmeny
    x_i = [round(t_busy / shift_duration, 4) for t_busy in server_busy_time]
    # Celková priemerná vyťaženosť (všetkých doktorov)
    px = sum(server_busy_time) / (num_doctors * shift_duration)
    # Priemerná čakacia doba
    pcd = sum(served_times) / pvp if pvp > 0 else 0

    global_pvp_list.append(pvp)
    global_px_list.append(px)
    global_pcd_list.append(pcd)

# Výpočet priemerov zo všetkých simulácií
avg_pvp = sum(global_pvp_list) / len(global_pvp_list)
avg_px = sum(global_px_list) / len(global_px_list)
avg_pcd = sum(global_pcd_list) / len(global_pcd_list)

# Výstup požadovaných výsledkov
print("\n=== PRIEMERNÉ HODNOTY ZE VŠETKÝCH 10 BEHOV (c = 4) ===")
print(f"Priemerný počet vyšetrených pacientov: {avg_pvp:.2f}")
print(f"Celková priemerná vyťaženosť: {avg_px:.4f}")
print(f"Celková priemerná čakacia doba: {avg_pcd:.4f}")
