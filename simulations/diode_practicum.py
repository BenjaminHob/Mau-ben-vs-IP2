# %% 1. INSTELLINGEN
# Diodepracticum: iteratief meten, data verwerken en Shockley-fit
#
# Schakeling zoals in de figuur:
# R2 staat boven de knoop; vanaf die knoop staan R3 en (R1 + diode)
# parallel naar de onderste rail. De voltmeters meten U_bron en U_R1.
#
# Benodigd: numpy, matplotlib, scipy
# Uitvoeren in VS Code: klik op "Run Cell" of voer het hele bestand uit.

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Weerstanden (OHM) -- pas deze waarden aan na jullie keuze
R1 = 1_000.0
R2 = 1_000.0
R3 = 1_000.0

# Onzekerheden (standaardonzekerheden, in dezelfde eenheden)
# Vul deze in aan de hand van de handleiding en/of specificaties van de DMM.
dU_bron = 0.01       # V, onzekerheid voltmeter over de bron
dU_R = 0.01          # V, onzekerheid voltmeter over R1
dR1 = 10.0           # ohm
dR2 = 10.0           # ohm
dR3 = 10.0           # ohm

# Temperatuur en natuurconstanten
T = 293.15           # K (voorbeeld: 20 graden Celsius)
k_B = 1.380649e-23   # J/K
q = 1.602176634e-19  # C

# Monte-Carlo-aantal voor onzekerheidspropagatie
N_MC = 20_000

# %% 2. RUWE MEETDATA
# Voeg na iedere meting één waarde toe aan BEIDE lijsten.
# U_bron: spanning over de volledige voeding (V)
# U_R:    spanning over R1 (V)
#
# Laat de voorbeeldwaarden hieronder NIET staan voor jullie echte analyse.
# Vervang ze door jullie eigen meetwaarden.

U_bron_data = [
    # 3.00,
    # 3.20,
]

U_R_data = [
    # 0.012,
    # 0.025,
]

# %% 3. DATA VERWERKEN EN ONZEKERHEDEN BEREKENEN

def bereken_grootheden(Ub, UR, r1=R1, r2=R2, r3=R3):
    """
    Berekent I_D en U_D uit de twee gemeten spanningen.

    I_D = U_R / R1
    KCL op de knoop: (U_bron - U_knoop)/R2 = U_knoop/R3 + I_D
    U_D = U_knoop - U_R
    """
    stroom = UR / r1
    geleiding = 1.0 / r2 + 1.0 / r3
    U_knoop = (Ub / r2 - stroom) / geleiding
    U_diode = U_knoop - UR
    return U_diode, stroom


def onzekerheden_monte_carlo(Ub, UR, n_mc=N_MC):
    """
    Monte-Carlo-propagatie. Meetonzekerheden worden per meetpunt
    gevarieerd; de weerstanden worden per simulatie getrokken en zijn
    dus gemeenschappelijk voor alle meetpunten binnen die simulatie.
    """
    ub = np.asarray(Ub, dtype=float)
    ur = np.asarray(UR, dtype=float)

    rng = np.random.default_rng(42)
    n_punten = len(ub)

    # Resistorwaarden zijn gemeenschappelijke onzekerheden voor de reeks.
    r1_trekkingen = rng.normal(R1, dR1, n_mc)
    r2_trekkingen = rng.normal(R2, dR2, n_mc)
    r3_trekkingen = rng.normal(R3, dR3, n_mc)

    # Voorkom fysisch onmogelijke negatieve weerstanden.
    r1_trekkingen = np.clip(r1_trekkingen, 1e-12, None)
    r2_trekkingen = np.clip(r2_trekkingen, 1e-12, None)
    r3_trekkingen = np.clip(r3_trekkingen, 1e-12, None)

    ub_trekkingen = rng.normal(ub, dU_bron, (n_mc, n_punten))
    ur_trekkingen = rng.normal(ur, dU_R, (n_mc, n_punten))

    stroom_mc = ur_trekkingen / r1_trekkingen[:, None]
    geleiding_mc = (
        1.0 / r2_trekkingen[:, None] + 1.0 / r3_trekkingen[:, None]
    )
    uknoop_mc = (
        ub_trekkingen / r2_trekkingen[:, None] - stroom_mc
    ) / geleiding_mc
    udiode_mc = uknoop_mc - ur_trekkingen

    d_ud = np.std(udiode_mc, axis=0, ddof=1)
    d_i = np.std(stroom_mc, axis=0, ddof=1)
    return d_ud, d_i


if len(U_bron_data) != len(U_R_data):
    raise ValueError("U_bron_data en U_R_data moeten evenveel meetwaarden bevatten.")

if len(U_bron_data) < 3:
    raise ValueError(
        "Voer minimaal drie meetpunten in U_bron_data en U_R_data in."
    )

U_bron = np.asarray(U_bron_data, dtype=float)
U_R = np.asarray(U_R_data, dtype=float)

U_D, I_D = bereken_grootheden(U_bron, U_R)
dU_D, dI_D = onzekerheden_monte_carlo(U_bron, U_R)

# Sorteer de data op diode-spanning voor een nette grafiek.
volgorde = np.argsort(U_D)
U_D, I_D = U_D[volgorde], I_D[volgorde]
dU_D, dI_D = dU_D[volgorde], dI_D[volgorde]

print("\nBerekende meetgegevens")
print("  U_D (V)       I_D (A)       dU_D (V)     dI_D (A)")
for ud, stroom, du, di in zip(U_D, I_D, dU_D, dI_D):
    print(f"{ud:10.5f}  {stroom:12.5e}  {du:10.5f}  {di:12.5e}")

# %% 4. SHOCKLEY-FIT

def shockley(ud, log10_I0, n):
    """Shockley-vergelijking; log10(I0) houdt I0 automatisch positief."""
    I0 = 10.0 ** log10_I0
    exponent = q * np.asarray(ud) / (n * k_B * T)
    exponent = np.clip(exponent, -100, 100)  # voorkomt overflow
    return I0 * np.expm1(exponent)


# Gebruik alleen positieve stroom en voorwaartse spanning voor de fit.
fit_mask = (U_D > 0) & (I_D > 0) & np.isfinite(I_D)

if np.count_nonzero(fit_mask) < 3:
    raise ValueError(
        "Er zijn minimaal drie meetpunten met U_D > 0 en I_D > 0 nodig voor de fit."
    )

x_fit = U_D[fit_mask]
y_fit = I_D[fit_mask]
dy_fit = dI_D[fit_mask]

# Een kleine ondergrens voorkomt dat nul-onzekerheden de fit blokkeren.
dy_fit = np.maximum(dy_fit, np.max(np.abs(y_fit)) * 1e-9)

popt, pcov = curve_fit(
    shockley,
    x_fit,
    y_fit,
    p0=(-9.0, 1.5),                 # startschatting log10(I0), n
    sigma=dy_fit,
    absolute_sigma=True,
    bounds=([-30.0, 0.5], [0.0, 5.0]),
    maxfev=50_000,
)

log10_I0, n_fit = popt
d_log10_I0, d_n = np.sqrt(np.diag(pcov))

I0_fit = 10.0 ** log10_I0
d_I0 = np.log(10.0) * I0_fit * d_log10_I0

print("\nResultaat Shockley-fit")
print(f"I0 = ({I0_fit:.3e} ± {d_I0:.1e}) A")
print(f"n  = {n_fit:.3f} ± {d_n:.3f}")
print(f"T  = {T:.2f} K")

# %% 5. GRAFIEK MET FIT EN FOUTBALKEN

U_plot = np.linspace(max(0.001, np.min(x_fit)), np.max(x_fit), 500)
I_plot = shockley(U_plot, *popt)

plt.figure(figsize=(8, 5))
plt.errorbar(
    U_D, I_D,
    xerr=dU_D, yerr=dI_D,
    fmt="o", capsize=3, label="Meetgegevens"
)
plt.plot(U_plot, I_plot, label="Shockley-fit")
plt.xlabel(r"Diodespanning $U_D$ (V)")
plt.ylabel(r"Di stroom $I_D$ (A)")
plt.title("I-V-karakteristiek van de diode")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# %% 6. ADVIES VOOR EEN VOLGEND MEETPUNT

# Kies het midden van het grootste gat tussen gemeten U_D-waarden.
# Als er al een fit is, schat het script ook welke U_bron daarbij hoort.
if len(U_D) >= 2:
    gaten = np.diff(U_D)
    index_grootste_gat = np.argmax(gaten)
    U_D_doel = 0.5 * (U_D[index_grootste_gat] + U_D[index_grootste_gat + 1])

    I_doel = float(shockley(U_D_doel, *popt))
    U_R_doel = I_doel * R1
    U_knoop_doel = U_D_doel + U_R_doel

    # Uit de knoopwet volgt:
    # U_bron = U_knoop + R2 * (U_knoop/R3 + I_D)
    U_bron_doel = U_knoop_doel + R2 * (U_knoop_doel / R3 + I_doel)

    print("\nSuggestie voor het volgende meetpunt")
    print(f"Richt op U_D ≈ {U_D_doel:.4f} V")
    print(f"Geschatte U_bron ≈ {U_bron_doel:.4f} V")
    print("Gebruik dit als startinstelling en controleer de werkelijke meetwaarden.")
else:
    print("\nNog onvoldoende meetpunten voor een meetadvies.")

# %% 7. DATA OPSLAAN (optioneel)
# Haal de commentaartekens weg als je de berekende data wilt bewaren.
#
# np.savetxt(
#     "diode_verwerkte_data.csv",
#     np.column_stack((U_bron, U_R, U_D, I_D, dU_D, dI_D)),
#     delimiter=",",
#     header="U_bron_V,U_R_V,U_D_V,I_D_A,dU_D_V,dI_D_A",
#     comments=""
# )
