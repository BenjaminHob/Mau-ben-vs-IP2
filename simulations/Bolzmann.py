import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


R1 = 32950.0
R2 = 10004.0
R3 = 990.0


dU_bron = 0.01       # V, onzekerheid voltmeter over de bron
dU_R = 0.01          # V, onzekerheid voltmeter over R1
dR1 = 10.0           # ohm
dR2 = 10.0           # ohm
dR3 = 10.0           # ohm


T = 294.15           # K 
k_B = 1.380649e-23   # J/K
q = 1.602176634e-19  # C


U_bron_data = np.array([1.1,2.3,1.69,1.20,3.3,4.4,7.0,6.0,6.3,6.7,10,15,25,20,17.5,16,14.5,13,11.5,8,7.5,6.5,5,4,3.6,3,2.5,2,1.5])

U_R_data = np.array([0.8,6.89,2.50,0.98,26.8,73.37,242.7,171.9,192.5,220.8,473.4,882.2,1726,1300,1091,965.3,841.1,716.4,593.9,317.1,279.4,206.4,106,53.4,36.8,18.5,9.18,4.1,1.7])*10**-3



element = len(U_bron_data)-1




def bereken_grootheden(Ub, UR):

    stroom = UR / R1
    geleiding = 1.0 / R2 + 1.0 / R3
    U_knoop = (Ub / R2 - stroom) / geleiding
    U_diode = U_knoop - UR
    return U_diode, stroom



U_bron = U_bron_data
U_R = U_R_data


Udiode, Idiode = bereken_grootheden(U_bron[element],U_R[element])
print(len(U_bron),len(U_R))
print(Udiode)
U_D, I_D = bereken_grootheden(U_bron, U_R)


def shockley(ud, I0, n):
    exponent = q * ud / (n * k_B * T)
    return I0 * np.exp(exponent)


x_fit = U_D
y_fit = I_D

print(np.argmax(x_fit))

popt, pcov = curve_fit(
    shockley,
    x_fit,
    y_fit,
    p0=(10**-9, 1.5)
)

I0_fit, n_fit = popt


print("\nResultaat Shockley-fit")
print(f"I0 = {I0_fit:.3e}A")
print(f"n  = {n_fit:.3f}")
print(f"T  = {T:.2f} K")

xtest = np.linspace(0.1,0.5,1000)
ytest = shockley(xtest,*popt)

plt.figure()
plt.plot(x_fit,y_fit,'k.')
plt.plot(xtest,ytest,'r--')
plt.grid(True)
plt.xlabel('Spanning diode (V)')
plt.ylabel('Stroom diode (A)')
plt.show()