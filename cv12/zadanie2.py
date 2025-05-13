import numpy as np
import matplotlib.pyplot as plt


def simulate_sird(N, beta, gamma, mu, I0, R0, D0, days, intervention_day=None, beta_factor=1.0):
    """
    Simulate the SIRD model using Euler's method.
    Returns arrays of t, S, I, R, D sampled at integer days.
    """
    dt = 0.1
    t_cont = np.arange(0, days + dt, dt)
    S_cont = np.zeros_like(t_cont)
    I_cont = np.zeros_like(t_cont)
    R_cont = np.zeros_like(t_cont)
    D_cont = np.zeros_like(t_cont)

    # initial conditions
    S_cont[0] = N - I0 - R0 - D0
    I_cont[0] = I0
    R_cont[0] = R0
    D_cont[0] = D0

    for i in range(1, len(t_cont)):
        ti = t_cont[i]
        curr_beta = beta * (beta_factor if (intervention_day is not None and ti >= intervention_day) else 1.0)

        dS = -curr_beta * S_cont[i - 1] * I_cont[i - 1] / N
        dI = curr_beta * S_cont[i - 1] * I_cont[i - 1] / N - (gamma + mu) * I_cont[i - 1]
        dR = gamma * I_cont[i - 1]
        dD = mu * I_cont[i - 1]

        S_cont[i] = S_cont[i - 1] + dS * dt
        I_cont[i] = I_cont[i - 1] + dI * dt
        R_cont[i] = R_cont[i - 1] + dR * dt
        D_cont[i] = D_cont[i - 1] + dD * dt

    # sample at integer days
    step = int(1 / dt)
    S = S_cont[::step]
    I = I_cont[::step]
    R = R_cont[::step]
    D = D_cont[::step]
    t = np.arange(0, days + 1)
    return t, S, I, R, D


if __name__ == "__main__":
    # parameters
    N = 500  # celkový počet obyvateľov
    R0_val = 1.5  # základné reprodukčné číslo
    D_inf = 7.0  # dĺžka infekčnosti (dní)
    mort = 0.2  # mortalita (20 %)

    removal = 1 / D_inf
    gamma = removal * (1 - mort)  # miera zotavenia
    mu = removal * mort  # miera úmrtí
    beta = R0_val * removal  # prenosová rýchlosť

    # necháme si zadať počiatočný počet nakazených
    try:
        I0 = int(input("Zadaj počiatočný počet nakazených (napr. 1): "))
    except ValueError:
        print("Neplatný vstup, nastavujem I0 = 1")
        I0 = 1

    R0_init, D0_init = 0, 0
    days = 30

    # simulácie
    t, S, I, R, D = simulate_sird(
        N, beta, gamma, mu, I0, R0_init, D0_init, days
    )
    t2, S2, I2, R2, D2 = simulate_sird(
        N, beta, gamma, mu, I0, R0_init, D0_init, days,
        intervention_day=10, beta_factor=0.3
    )

    # vykreslenie infikovaných
    plt.figure(figsize=(10, 6))
    plt.plot(t, I, label='Infikovaní (bez izolácie)')
    plt.plot(t2, I2, '--', label='Infikovaní (s izoláciou od dňa 10)')
    plt.xlabel('Dni')
    plt.ylabel('Počet infikovaných')
    plt.title('SIRD simulácia: základ vs. izolácia')
    plt.legend()
    plt.grid(True)
    plt.show()

    # denný súhrn
    header = f"{'Deň':>3} | {'S':>6} {'I':>6} {'R':>6} {'D':>6} || {'I_iso':>6} {'R_iso':>6} {'D_iso':>6}"
    print(header)
    print("-" * len(header))
    for day in range(days + 1):
        print(f"{day:3d} | "
              f"{S[day]:6.1f} {I[day]:6.1f} {R[day]:6.1f} {D[day]:6.1f} || "
              f"{I2[day]:6.1f} {R2[day]:6.1f} {D2[day]:6.1f}")

    # konečné súčty
    print("\nKonečné po 30 dňoch:")
    print(f"Bez izolácie:     úmrtí = {D[-1]:.0f}, zotavených = {R[-1]:.0f}")
    print(f"So izoláciou:     úmrtí = {D2[-1]:.0f}, zotavených = {R2[-1]:.0f}")
    print(f"Úspora na životoch: {D[-1] - D2[-1]:.0f}")
