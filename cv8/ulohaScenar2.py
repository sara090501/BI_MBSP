# ●	V originálnom zadaní zmeňte: Do radu chodia oprioritizované úlohy. Zhruba tretina má prioritu 1, zhruba šestina prioritu 2 a zvyšok prioritu 3 (najnižšiu). Implementujte to a vypočítajte osobitne priemerný čakací čas ľudí s prioritou 1, ľudí s prioritou 2 a ľudí s prioritou 3.

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
        self.waiting_time = None  # čakacia doba (service_start_time - arrival_time)
        self.priority = None  # priorita: 1 (najvyššia), 2, 3 (najnižšia)


# area_queue – prioritizovaná fronta pacientov.
# Úloha dequeue() vyberie pacienta s najnižším číslom priority.
# V prípade zhodnej priority uprednostníme pacienta, ktorý prišiel skôr.
class AreaQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, node):
        self.queue.append(node)

    def dequeue(self):
        if not self.queue:
            return None
        # Vyberieme pacienta s najnižšou prioritou; FIFO v rámci rovnakej priority.
        chosen_index = 0
        chosen_node = self.queue[0]
        for i, node in enumerate(self.queue):
            if (node.priority < chosen_node.priority) or \
                    (node.priority == chosen_node.priority and node.arrival_time < chosen_node.arrival_time):
                chosen_index = i
                chosen_node = node
        return self.queue.pop(chosen_index)

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
# SIMULAČNÝ MECHANIZMUS A POMOCNÉ FUNKCIE
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
    return random.uniform(15, 40)


def assign_patients(current_time, servers, queue, event_list, waiting_times_by_priority, queue_length_history):
    """
    Priraďovanie čakajúcich pacientov k voľným serverom.
    Vždy sa vyberie pacient s najvyššou prioritou (tj. s najnižším číslom).
    """
    assigned = True
    while assigned and len(queue) > 0:
        assigned = False
        # Prechádzame servery zoradené podľa id (od najmenšieho)
        for server in sorted(servers, key=lambda s: s.id):
            if not server.is_busy and len(queue) > 0:
                patient = queue.dequeue()  # vyberie pacienta s najvyššou prioritou
                queue_length_history.append((current_time, len(queue)))
                patient.waiting_time = current_time - patient.arrival_time
                # Ulož waiting time do príslušného zoznamu podľa priority
                if patient.priority == 1:
                    waiting_times_by_priority[1].append(patient.waiting_time)
                elif patient.priority == 2:
                    waiting_times_by_priority[2].append(patient.waiting_time)
                else:
                    waiting_times_by_priority[3].append(patient.waiting_time)
                patient.service_start_time = current_time
                service_time = uniform_service()
                patient.service_time = service_time
                patient.departure_time = current_time + service_time
                schedule_event(event_list, patient.departure_time, 'departure', server.id)
                server.is_busy = True
                server.next_free_time = patient.departure_time
                server.busy_time += service_time
                server.count_served += 1
                assigned = True


def simulation():
    random.seed(42)  # pre reprodukovateľnosť
    current_time = 0.0
    event_list = []

    # Inicializácia prioritizovanej čakacej fronty
    queue = AreaQueue()

    # Inicializácia zoznamu serverov (lekárov) s pridelenými poradovými číslami (0, 1, 2, ...)
    servers = [AreaServer(i) for i in range(NUM_DOCTORS)]

    # Zber štatistík
    waiting_times_by_priority = {1: [], 2: [], 3: []}  # čakacie doby rozdelené podľa priority
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
            # Spracujeme príchod iba ak je v rámci zmeny
            if current_time <= SIM_END:
                # Vytvorenie pacienta (area_node)
                patient = AreaNode(current_time, patient_id_counter)
                patient_id_counter += 1
                # Priradenie priority:
                r = random.random()
                if r < 1 / 3:
                    patient.priority = 1
                elif r < (1 / 3 + 1 / 6):  # asi 0.5
                    patient.priority = 2
                else:
                    patient.priority = 3
                queue.enqueue(patient)
                queue_length_history.append((current_time, len(queue)))

                # Naplánuj ďalší príchod, ak je v rámci zmeny
                next_arrival = current_time + triangular_interarrival()
                if next_arrival <= SIM_END:
                    schedule_event(event_list, next_arrival, 'arrival', None)

            # Pokúsime sa priradiť čakajúcich pacientov k dostupným serverom
            assign_patients(current_time, servers, queue, event_list, waiting_times_by_priority, queue_length_history)

        elif event_type == 'departure':
            # Ukončenie vyšetrenia – server sa uvoľní
            server_id = event_info
            servers[server_id].is_busy = False
            served_count += 1
            cumulative_served.append((current_time, served_count))
            assign_patients(current_time, servers, queue, event_list, waiting_times_by_priority, queue_length_history)

    # Vypočítame priemernú čakaciu dobu pre každú prioritu
    avg_waiting_1 = sum(waiting_times_by_priority[1]) / len(waiting_times_by_priority[1]) if waiting_times_by_priority[
        1] else 0
    avg_waiting_2 = sum(waiting_times_by_priority[2]) / len(waiting_times_by_priority[2]) if waiting_times_by_priority[
        2] else 0
    avg_waiting_3 = sum(waiting_times_by_priority[3]) / len(waiting_times_by_priority[3]) if waiting_times_by_priority[
        3] else 0

    # Priprav údaje pre vykresľovanie
    times_queue = [t for t, q in queue_length_history]
    queue_lengths = [q for t, q in queue_length_history]
    served_times = [t for t, c in cumulative_served]
    served_counts = [c for t, c in cumulative_served]

    return servers, (
    avg_waiting_1, avg_waiting_2, avg_waiting_3), served_times, served_counts, times_queue, queue_lengths


# ================================
# SPUSTENIE SIMULÁCIE A VÝSTUPY
# ================================
if __name__ == '__main__':
    servers, avg_waitings, served_times, served_counts, times_queue, queue_lengths = simulation()
    avg_waiting_1, avg_waiting_2, avg_waiting_3 = avg_waitings
    print("Priemerná čakacia doba pacientov s prioritou 1: {:.2f} minút".format(avg_waiting_1))
    print("Priemerná čakacia doba pacientov s prioritou 2: {:.2f} minút".format(avg_waiting_2))
    print("Priemerná čakacia doba pacientov s prioritou 3: {:.2f} minút".format(avg_waiting_3))

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
