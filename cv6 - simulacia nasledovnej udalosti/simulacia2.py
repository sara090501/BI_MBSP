# 1/n suma(wi) = w(priemer)
# 1/n suma(si) = s(priemer)
# 1/n suma(ri) = r(priemer)
# 1/n suma(di) = d(priemer)
# lt pocet uloh v uzle v case t (v tejto simulacii -> l(priemer) = 1/T suma od 1 do n z wi)
# qt pocet uloh v rade v case t (v tejto simulacii -> l(priemer) = 1/T suma od 1 do n z di)
# xt pocet uloh v servise v case t (v tejto simulacii -> l(priemer) = 1/T suma od 1 do n z si)

# a = 15, 47, 71, 111, 123, 152, 166, 226, 310, 320 -> cas prichodu, kedy pride uloha do uzlu
# b -> kedy uloha zacne byt obsluhovana
# c -> kedy uloha skonci byt obsluhovana
# d -> ako dlho caka uloha na obsluhu
# s = 43, 36, 34, 30, 38, 40, 31, 29, 36, 30 -> ako dlho trva obsluha ulohy
# potom by sme mali dostat -> d = 0, 11, 23, 17, 35, 44, 70, 41, 0, 26

# Given arrival times and service times
a = [15, 47, 71, 111, 123, 152, 166, 226, 310, 320]
s = [43, 36, 34, 30, 38, 40, 31, 29, 36, 30]
n = len(a)

# Initialize completion times and waiting times
c = [0] * n
d = [0] * n
w = [0] * n # -> celkovy cas ktory uloha stravi v uzle

i = 0
while i < len(a):
    if i == 0:
        c[i] = a[i] + s[i]  # First task starts immediately
    else:
        c[i] = max(a[i], c[i - 1]) + s[i]  # Service starts after the previous completion

    d[i] = c[i] - a[i] - s[i]  # Waiting time
    w[i] = d[i] + s[i]
    i += 1

# Output results
print("Casy konca v uzle:", c)
print("Casy cakania uloh:", d)
print("Celkovy cas v uzle:", w)

print("Priemerny cas v rade:", sum(d)/n) #qt
print("Priemerny cas servise:", sum(s)/n) #xt
print("Priemerny cas celkovo:", sum(w)/n) #lt

# l, q, x
print("l: priemerny pocet uloh v uzle:", 1/max(c) * sum(w)) # lt pocet uloh v uzle v case t (v tejto simulacii -> l(priemer) = 1/T suma od 1 do n z wi)
print("q: priemerny pocet uloh v rade", 1/max(c) * sum(d)) # qt pocet uloh v rade v case t (v tejto simulacii -> l(priemer) = 1/T suma od 1 do n z di)
print("x: priemerny pocet uloh v servise", 1/max(c) * sum(s)) # xt pocet uloh v servise v case t (v tejto simulacii -> l(priemer) = 1/T suma od 1 do n z si)

# # Initialize completion times and waiting times
# c = [0] * len(a)
# d = [0] * len(a)
#
# # Compute completion times and waiting times
# for i in range(len(a)):
#     if i == 0:
#         c[i] = a[i] + s[i]  # First task starts immediately
#     else:
#         c[i] = max(a[i], c[i - 1]) + s[i]  # Service starts after the previous completion
#
#     d[i] = c[i] - a[i] - s[i]  # Waiting time
#
# # Output results
# print("Completion times:", c)
# print("Waiting times:", d)
