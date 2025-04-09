import random
import heapq
import matplotlib.pyplot as plt

# Konštanta – trvanie zmeny v minútach (8 hodín)
SIM_END = 480.0
NUM_DOCTORS = 4  # počet lekárov


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
        self.waiting_time = None  # čakacia doba (service_start - arrival)


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


# (area_service – logika služby je priamo implementovaná v priraďovaní pacienta)

# ================================
# SIMULAČNÝ MECHANIZMUS
# ================================

# Globálny čítač udalostí pre zabezpečenie správneho radenia udalostí
event_counter = 0


def schedule_event(event_list, event_time, event_type, event_info):
    global event_counter
    heapq.heappush(event_list, (event_time, event_counter, event_type, event_info))
    event_counter += 1


def triangular_interarrival():
    # Trojuholníkové rozdelenie T(3,5,12)
    return random.triangular(3, 12, 5)


def uniform_service():
    # Rovnomerné rozdelenie U(5,25)
    return random.uniform(5, 25)


def simulation():
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
    first_arrival = triangular_interarrival()
    schedule_event(event_list, first_arrival, 'arrival', None)
    patient_id_counter = 0  # identifikátor pacienta

    # Hlavná slučka simulácie
    while event_list:
        event_time, _, event_type, event_info = heapq.heappop(event_list)
        current_time = event_time

        if event_type == 'arrival':
            # Spracujeme príchod iba ak ide o čas do konca zmeny
            if current_time <= SIM_END:
                # Vytvorenie pacienta (area_node)
                patient = AreaNode(current_time, patient_id_counter)
                patient_id_counter += 1
                queue.enqueue(patient)
                queue_length_history.append((current_time, len(queue)))

                # Naplánuj ďalší príchod, ak bude v rámci zmeny
                next_arrival = current_time + triangular_interarrival()
                if next_arrival <= SIM_END:
                    schedule_event(event_list, next_arrival, 'arrival', None)

                # Skús priradiť pacienta do služby, ak je v čele fronty
                # a server podľa cyklického poradia je voľný.
                if len(queue) > 0:
                    designated_server = servers[next_server_index]
                    if not designated_server.is_busy:
                        p = queue.dequeue()
                        queue_length_history.append((current_time, len(queue)))
                        # Čakanie = rozdiel medzi aktuálnym časom a časom príchodu
                        p.waiting_time = current_time - p.arrival_time
                        waiting_times.append(p.waiting_time)
                        p.service_start_time = current_time
                        service_time = uniform_service()
                        p.service_time = service_time
                        p.departure_time = current_time + service_time
                        schedule_event(event_list, p.departure_time, 'departure', next_server_index)
                        # Aktualizácia štatistík servera
                        designated_server.is_busy = True
                        designated_server.next_free_time = p.departure_time
                        designated_server.busy_time += service_time
                        designated_server.count_served += 1
                        # Aktualizácia cyklického ukazovateľa
                        next_server_index = (next_server_index + 1) % NUM_DOCTORS
                        queue_length_history.append((current_time, len(queue)))
            # Príchody po 8-hodinovej zmene ignorujeme.

        elif event_type == 'departure':
            # Dokončenie vyšetrenia
            server_id = event_info
            servers[server_id].is_busy = False
            served_count += 1
            cumulative_served.append((current_time, served_count))

            # Ak vo fronte čaká pacient a server určený cyklickým poradie je voľný,
            # priraď ho do služby.
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
    servers, avg_waiting_time, served_times, served_counts, times_queue, queue_lengths = simulation()
    print("Priemerná čakacia doba: {:.2f} minút".format(avg_waiting_time))

    # Histogram vyťaženosti – počet vyšetrených pacientov na lekára
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
