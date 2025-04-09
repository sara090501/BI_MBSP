import math
import random
import heapq
import matplotlib.pyplot as plt
import numpy as np

# SIMULAČNÉ PARAMETRE
# Teraz simulácia pokrýva 13 hodín, teda 780 minút (napr. od 9:00 do 22:00)
SIM_END = 780.0
NUM_DOCTORS = 4  # počet lekárov

# Globálne pre predpočítané príchody a index
precomputed_arrivals = []
arrival_index = 0


def initialize_arrivals():
    """
    Predpočíta absolútne časy príchodov na základe hodinového rozdelenia.
    Každý interval trvá 60 minút, pričom hour_counts definuje počet pacientov
    v jednotlivých hodinách. Napríklad ak interval 0 (9:00–10:00) má 14 pacientov,
    vygenerujeme 14 náhodných časov v intervalu [0, 60).
    """
    global precomputed_arrivals
    hour_counts = [14, 15, 13, 12, 11, 10, 5, 5, 4, 2, 2, 4, 3]
    arrivals = []
    for i, count in enumerate(hour_counts):
        bin_start = i * 60  # začiatok i-teho hodinového intervalu
        bin_end = (i + 1) * 60  # koniec intervalu
        for _ in range(count):
            arrivals.append(random.uniform(bin_start, bin_end))
    precomputed_arrivals = sorted(arrivals)


def triangular_interarrival():
    """
    Funkcia vráti časový rozdiel medzi po sebe nasledujúcimi príchodmi podľa
    predpočítaného zoznamu pre príchody. Pri prvom zavolaní vráti čas prvej
    udalosti (t.j. čas od začiatku simulácie) a potom rozdiely medzi príchodmi.
    """
    global arrival_index, precomputed_arrivals
    if arrival_index >= len(precomputed_arrivals):
        return None  # už nie sú ďalšie príchody
    if arrival_index == 0:
        interarrival = precomputed_arrivals[0]  # čas od 0 do prvého príchodu
    else:
        interarrival = precomputed_arrivals[arrival_index] - precomputed_arrivals[arrival_index - 1]
    arrival_index += 1
    return interarrival


# ================================
# DÁTOVÉ ŠTRUKTÚRY
# ================================

# area_node – reprezentácia pacienta
class AreaNode:
    def __init__(self, arrival_time, id):
        self.id = id
        self.arrival_time = arrival_time  # čas príchodu do čakárne
        self.service_start_time = None  # kedy začína vyšetrenie
        self.departure_time = None  # kedy skončí vyšetrenie
        self.service_time = None  # trvanie vyšetrenia
        self.waiting_time = None  # čakacia doba


# area_queue – FIFO fronta pacientov
class AreaQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, node):
        self.queue.append(node)

    def dequeue(self):
        if self.queue:
            return self.queue.pop(0)
        else:
            return None

    def __len__(self):
        return len(self.queue)


# area_server_x – reprezentácia lekára
class AreaServer:
    def __init__(self, id):
        self.id = id
        self.busy_time = 0.0  # celkový čas, kedy je server zaneprázdnený
        self.count_served = 0  # počet vyšetrených pacientov
        self.next_free_time = 0.0  # čas, kedy bude server opäť voľný
        self.is_busy = False  # príznak, či je server práve zaneprázdnený


# ================================
# SIMULAČNÝ MECHANIZMUS
# ================================

# Globálny čítač udalostí pre zabezpečenie správneho radenia udalostí
event_counter = 0


def schedule_event(event_list, event_time, event_type, event_info):
    global event_counter
    heapq.heappush(event_list, (event_time, event_counter, event_type, event_info))
    event_counter += 1


def uniform_service():
    # Doba služieb: U(15,40) – možno upraviť podľa potreby
    return random.uniform(15, 40)


def simulation():
    # Inicializujeme príchody podľa zadaného rozdelenia
    initialize_arrivals()
    random.seed(42)  # pre reprodukovateľnosť
    current_time = 0.0
    event_list = []

    # Inicializácia čakacej fronty
    queue = AreaQueue()

    # Inicializácia zoznamu serverov (lekárov)
    servers = [AreaServer(i) for i in range(NUM_DOCTORS)]
    next_server_index = 0  # cyklický ukazovateľ pre výber servera

    # Zber štatistík
    waiting_times = []  # čakacie doby pre pacientov
    cumulative_served = []  # záznam: (čas, kumulatívny počet vyšetrených pacientov)
    served_count = 0
    queue_length_history = []  # záznam: (čas, počet pacientov vo fronte)

    # Naplánuj prvý príchod pacienta
    first_interval = triangular_interarrival()
    if first_interval is not None:
        schedule_event(event_list, first_interval, 'arrival', None)
    patient_id_counter = 0  # identifikátor pacienta

    # Hlavná slučka simulácie
    while event_list:
        event_time, _, event_type, event_info = heapq.heappop(event_list)
        current_time = event_time

        if event_type == 'arrival':
            # Spracujeme príchod len ak je do SIM_END
            if current_time <= SIM_END:
                # Vytvorenie pacienta
                patient = AreaNode(current_time, patient_id_counter)
                patient_id_counter += 1
                queue.enqueue(patient)
                queue_length_history.append((current_time, len(queue)))

                # Naplánuj ďalší príchod, ak existuje a je v rámci SIM_END
                next_interval = triangular_interarrival()
                if next_interval is not None and (current_time + next_interval) <= SIM_END:
                    schedule_event(event_list, current_time + next_interval, 'arrival', None)

                # Priraď pacienta do služby, ak fronta nie je prázdna a server voľný
                if len(queue) > 0:
                    designated_server = servers[next_server_index]
                    if not designated_server.is_busy:
                        p = queue.dequeue()
                        queue_length_history.append((current_time, len(queue)))
                        p.waiting_time = current_time - p.arrival_time
                        waiting_times.append(p.waiting_time)
                        p.service_start_time = current_time
                        service_time = uniform_service()
                        p.service_time = service_time
                        p.departure_time = current_time + service_time
                        schedule_event(event_list, p.departure_time, 'departure', next_server_index)
                        designated_server.is_busy = True
                        designated_server.next_free_time = p.departure_time
                        designated_server.busy_time += service_time
                        designated_server.count_served += 1
                        next_server_index = (next_server_index + 1) % NUM_DOCTORS
                        queue_length_history.append((current_time, len(queue)))

        elif event_type == 'departure':
            # Dokončenie vyšetrenia – server sa uvoľní
            server_id = event_info
            servers[server_id].is_busy = False
            served_count += 1
            cumulative_served.append((current_time, served_count))

            if len(queue) > 0:
                designated_server = servers[next_server_index]
                if not designated_server.is_busy:
                    p = queue.dequeue()
                    queue_length_history.append((current_time, len(queue)))
                    p.waiting_time = current_time - p.arrival_time
                    waiting_times.append(p.waiting_time)
                    p.service_start_time = current_time
                    service_time = uniform_service()
                    p.service_time = service_time
                    p.departure_time = current_time + service_time
                    schedule_event(event_list, p.departure_time, 'departure', next_server_index)
                    designated_server.is_busy = True
                    designated_server.next_free_time = p.departure_time
                    designated_server.busy_time += service_time
                    designated_server.count_served += 1
                    next_server_index = (next_server_index + 1) % NUM_DOCTORS
                    queue_length_history.append((current_time, len(queue)))

    avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0

    # Priprav údaje pre vykresľovanie
    times_queue = [t for t, q in queue_length_history]
    queue_lengths = [q for t, q in queue_length_history]
    served_times = [t for t, c in cumulative_served]
    served_counts = [c for t, c in cumulative_served]

    return servers, avg_waiting_time, served_times, served_counts, times_queue, queue_lengths


# ================================
# SPUSTENIE SIMULÁCIE A VÝSTUPY
# ================================
if __name__ == '__main__':
    # Spustíme simuláciu
    servers, avg_waiting_time, served_times, served_counts, times_queue, queue_lengths = simulation()
    print("Priemerná čakacia doba: {:.2f} minút".format(avg_waiting_time))

    # Vykreslenie histogramu vyťaženosti lekárov (počet vyšetrených pacientov na lekára)
    doc_ids = [s.id for s in servers]
    counts = [s.count_served for s in servers]
    plt.figure()
    plt.bar(doc_ids, counts, align='center', alpha=0.7)
    plt.xlabel("ID lekára")
    plt.ylabel("Počet vyšetrených pacientov")
    plt.title("Histogram vyťaženosti lekárov")
    plt.xticks(doc_ids)
    plt.show()

    # Závislosť kumulatívneho počtu vyšetrených pacientov od času
    plt.figure()
    plt.step(served_times, served_counts, where='post')
    plt.xlabel("Čas (min)")
    plt.ylabel("Kumulatívny počet vyšetrených pacientov")
    plt.title("Závislosť počtu vyšetrených pacientov od času")
    plt.show()

    # Priebeh počtu ľudí vo fronte
    plt.figure()
    plt.step(times_queue, queue_lengths, where='post')
    plt.xlabel("Čas (min)")
    plt.ylabel("Počet ľudí vo fronte")
    plt.title("Priebeh počtu ľudí vo fronte")
    plt.show()

    # -------------------------------
    # Graf príchodov pacientov
    # -------------------------------
    # Na základe predpočítaných príchodov z initialize_arrivals()
    # (pre istotu ich inicializujeme znova)
    initialize_arrivals()
    # Pre každý absolútny čas príchodu zistíme hodinový interval: 0 -> 9:00, 1 -> 10:00, atď.
    # Pretože simulácia začína na 0 (čo zodpovedá 9:00) a trvá 13 hodín.
    arrival_bins = [int(time // 60) for time in precomputed_arrivals]
    # Počet príchodov pre každý interval (očakávame 13 intervalov)
    counts_per_hour = [arrival_bins.count(i) for i in range(13)]
    # X-ové popisky prispôsobíme ako hodiny od 9:00 do 21:00
    x_labels = [f"{9 + i}:00" for i in range(13)]

    plt.figure(figsize=(8, 5))
    plt.bar(range(13), counts_per_hour, tick_label=x_labels, edgecolor='black')
    plt.xlabel("Hodina dňa")
    plt.ylabel("Počet príchodov")
    plt.title("Histogram príchodov pacientov podľa hodín")
    plt.show()
