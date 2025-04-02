# q = l - suma od 1 po c z xi
#pridate do uzla
# 1. l = l + 1 (l je pocet jobov v uzle)
# ak l <= s -> priradit na server
# inak -> pridat do radu
# odchod zo servera
# 1. l = l - 1
# ak l >= c (situacia ze niekto cakal v rade) -> vyber z rady

#Vytvorit mnohoserverovy servisny uzol

# import numpy as np
# import simpy
# import matplotlib.pyplot as plt
import scipy.stats as stats
import matplotlib.pyplot as plt

l = 0
x = [0, 0, 0, 0]  ##pocet uloh v servise, server list (pocet doktorov)

low, high = 3, 7  # Interval prichodov
rv = stats.uniform(loc=low, scale=high - low)

low, high = 15, 25  # Interval prichodov
sj = stats.uniform(loc=low, scale=high - low)

BN = 1000000 #big number
c = 4 #pocet serverov
cal = [rv, BN, BN, BN, BN] #kalendar udalosti
t = 0 #cas
tau = 240 #treshold skoncenia

def getFreeServer():
    for i in range(c):
        if x[i] == 0:
            return i
    return -1

while t < tau and l > 0:
    min_value = min(cal)
    M = cal.index(min_value)
    #handling prichodu
    if M == 0: # prichod jobu
        t = cal.index(min_value)
        l = l + 1
        cal[min_value] = t + rv.rvs()
        if l > c: # servery plne
            #ohandlujem radu -> pridanie
            dorobitHadlovanie = 0
        else:
            s = getFreeServer() # od o po c-1
            x[s] = 1 # server je obsadeny
            cal[s+1] = t + sj.rvs() #uniform od 15 do 25
    else: #odchod zo servera
        l = l - 1
        if l >= c: #niekto ostal v rade
            #ohandlujem radu -> odobratie
            cal[M] = t + sj.rvs()
        else:
            x[M - 1] = 0
            cal[M] = BN

# # Parametre simulácie
# ARRIVAL_MIN = 3  # Min čas medzi príchodmi
# ARRIVAL_MAX = 7  # Max čas medzi príchodmi
# SERVICE_MIN = 15  # Min dĺžka vyšetrenia
# SERVICE_MAX = 25  # Max dĺžka vyšetrenia
# DOCTORS = 4  # Počet lekárov
# SIM_TIME = 4 * 60  # Simulujeme 4 hodiny (v minútach)
#
# # Sledovanie dát
# patient_count = 0
# completed_patients = 0
# server_busy_time = np.zeros(DOCTORS)  # Čas vyťaženia lekárov
#
# def patient(env, server, doctor_id):
#     global completed_patients
#     with server.request() as req:
#         yield req  # Čakanie na voľného lekára
#         start_time = env.now
#         service_time = np.random.uniform(SERVICE_MIN, SERVICE_MAX)  # Servisný čas
#         yield env.timeout(service_time)  # Vyšetrenie
#         end_time = env.now
#         server_busy_time[doctor_id] += (end_time - start_time)
#         completed_patients += 1
#
# def patient_generator(env, server):
#     global patient_count
#     doctor_id = 0  # Indexovanie lekárov na vyváženie záťaže
#     while True:
#         yield env.timeout(np.random.uniform(ARRIVAL_MIN, ARRIVAL_MAX))  # Generovanie pacientov
#         env.process(patient(env, server, doctor_id))
#         patient_count += 1
#         doctor_id = (doctor_id + 1) % DOCTORS  # Rotácia lekárov
#
# # Spustenie simulácie
# env = simpy.Environment()
# doctor_server = simpy.Resource(env, capacity=DOCTORS)
# env.process(patient_generator(env, doctor_server))
# env.run(until=SIM_TIME)
#
# # Výsledky
# print(f"Celkový počet pacientov: {patient_count}")
# print(f"Počet vyšetrených pacientov: {completed_patients}")
# print("Vyťaženie lekárov (minúty):", server_busy_time)
#
# # Graf vyťaženia lekárov
# plt.bar(range(DOCTORS), server_busy_time, tick_label=[f"Doktor {i+1}" for i in range(DOCTORS)])
# plt.xlabel("Lekár")
# plt.ylabel("Vyťaženie (min)")
# plt.title("Vyťaženie jednotlivých lekárov")
# plt.show()
#
