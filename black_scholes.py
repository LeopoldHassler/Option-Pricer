import math as mt
from scipy import stats as st
from scipy.optimize import brentq
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random as rd
import numpy as np

def BSM_pricer(S0,K,r,T,sigma,option_type):
    d1 = (mt.log(S0/K)+(r+sigma**2/2)*T)/(sigma*mt.sqrt(T))
    d2 = d1 - sigma*mt.sqrt(T)
    if option_type == "call" :
        option_price = S0*st.norm.cdf(d1) - K*mt.exp(-r*T)*st.norm.cdf(d2)
    elif option_type == "put" : 
        option_price = K*mt.exp(-r*T)*st.norm.cdf(-d2) - S0*st.norm.cdf(-d1)
    else : 
        return "Option type incorrect - please indicate either call or put"
    return option_price

input_choice = input("Do you wish to modify the existing inputs ? (yes/no) : ").lower()

while input_choice != "yes" and input_choice != "no" :
    input_choice = input("Do you wish to modify the existing inputs ? (yes/no) : ").lower()

if input_choice == "yes" :
    K = float(input("Strike price : "))
    r = float(input("Risk-free rate (%) : "))/100
    T = float(input("Time to maturity (months) : "))/12
    sigma = float(input("Volatility (%) : "))/100
    option_type = input("Option type : ").lower()
    while option_type != "call" and option_type != "put" :
        option_type = input("Option type : ").lower()
else :
    K = 40
    r = 0.03
    T = 6/12
    sigma = 0.15
    option_type = input("Option type : ").lower()
    while option_type != "call" and option_type != "put" :
        option_type = input("Option type : ").lower()

premium = []
intrinsic_value = []
time_value = []
spot = []
parity = []
delta1 = []
delta2 = []
gamma1 = []
gamma2 = []
vega1 = []
vega2 = []
rho1 = []
rho2 = []
theta1 = []
theta2 = []
delta_error = []
gamma_error = []
vega_error = []
rho_error = []
theta_error = []
Strike_smile = []
T_smile = []
IV_brent = []
IV_solver = []
IV_dichotomy = []

h_D = 0.01
h_G = 0.1
h_V = 0.0001
h_R = 0.0001
h_T = 1/365
upper_interval = int(K*1.5)
lower_interval = int(K*0.5)

def numerical_delta(S0,K,r,T,sigma,option_type,h) :
    delta = (BSM_pricer(S0+h,K,r,T,sigma,option_type) - BSM_pricer(S0-h,K,r,T,sigma,option_type))/(2*h)
    return delta

def numerical_gamma(S0,K,r,T,sigma,option_type,h) :
    gamma = (BSM_pricer(S0+h,K,r,T,sigma,option_type) + BSM_pricer(S0-h,K,r,T,sigma,option_type) - 2 * BSM_pricer(S0,K,r,T,sigma,option_type)) / h**2
    return gamma

def numerical_vega(S0,K,r,T,sigma,option_type,h) :
    vega = (BSM_pricer(S0,K,r,T,sigma+h,option_type) - BSM_pricer(S0,K,r,T,sigma-h,option_type))/(2*h)
    return vega

def numerical_theta(S0,K,r,T,sigma,option_type,h) :
    theta = (BSM_pricer(S0,K,r,T-h,sigma,option_type) - BSM_pricer(S0,K,r,T+h,sigma,option_type))/(2*h)
    return theta

def numerical_rho(S0,K,r,T,sigma,option_type,h) :
    rho = (BSM_pricer(S0,K,r+h,T,sigma,option_type) - BSM_pricer(S0,K,r-h,T,sigma,option_type))/(2*h)
    return rho

def analytical_delta(S0,K,r,T,sigma,option_type) :
    d1 = (mt.log(S0/K)+(r+sigma**2/2)*T)/(sigma*mt.sqrt(T))
    if option_type == "call" :
        delta = st.norm.cdf(d1)
    else :
        delta = st.norm.cdf(d1) - 1 
    return delta

def analytical_gamma(S0,K,r,T,sigma,option_type) :
    d1 = (mt.log(S0/K)+(r+sigma**2/2)*T)/(sigma*mt.sqrt(T))
    gamma = st.norm.pdf(d1)/(S0*sigma*mt.sqrt(T))
    return gamma

def analytical_vega(S0,K,r,T,sigma,option_type) :
    d1 = (mt.log(S0/K)+(r+sigma**2/2)*T)/(sigma*mt.sqrt(T))
    vega = S0*st.norm.pdf(d1)*mt.sqrt(T)
    return vega

def analytical_rho(S0,K,r,T,sigma,option_type) :
    d1 = (mt.log(S0/K)+(r+sigma**2/2)*T)/(sigma*mt.sqrt(T))
    d2 = d1-sigma*mt.sqrt(T)
    if option_type == "call" :
        rho = T*K*mt.exp(-r*T)*st.norm.cdf(d2)
    else :
         rho = -T*K*mt.exp(-r*T)*st.norm.cdf(-d2)
    return rho

def analytical_theta(S0,K,r,T,sigma,option_type) :
    d1 = (mt.log(S0/K)+(r+sigma**2/2)*T)/(sigma*mt.sqrt(T))
    d2 = d1-sigma*mt.sqrt(T)
    if option_type == "call" :
        theta = - (S0*st.norm.pdf(d1)*sigma)/(2*mt.sqrt(T)) - r*K*mt.exp(-r*T)*st.norm.cdf(d2)
    else :
        theta = - (S0*st.norm.pdf(d1)*sigma)/(2*mt.sqrt(T))+r*K*mt.exp(-r*T)*st.norm.cdf(-d2)
    return theta

for S0 in range(lower_interval,upper_interval+1) :
    opt_price = BSM_pricer(S0,K,r,T,sigma,option_type)
    if option_type == "call" :
        intrinsic = max(S0-K,0)
        if abs(opt_price + K*mt.exp(-r*T) - (BSM_pricer(S0,K,r,T,sigma,"put")+S0)) <= 1*10**(-8) :
            parity_check = "Parity respected"
        else : 
            parity_check = "Parity not respected"
    elif option_type == "put" :
        if abs(BSM_pricer(S0,K,r,T,sigma,"call") + K*mt.exp(-r*T) - (opt_price + S0)) <= 1*10**(-8) :
            parity_check = "Parity respected"
        else :
            parity_check = "Parity not respected"
        intrinsic = max(K-S0,0)
    num_delta = numerical_delta(S0,K,r,T,sigma,option_type,h_D)
    num_gamma = numerical_gamma(S0,K,r,T,sigma,option_type,h_G)
    num_vega = numerical_vega(S0,K,r,T,sigma,option_type,h_V)
    num_rho = numerical_rho(S0,K,r,T,sigma,option_type,h_R)
    num_theta = numerical_theta(S0,K,r,T,sigma,option_type,h_T)
    ana_delta = analytical_delta(S0,K,r,T,sigma,option_type)
    ana_gamma = analytical_gamma(S0,K,r,T,sigma,option_type)
    ana_vega = analytical_vega(S0,K,r,T,sigma,option_type)
    ana_rho = analytical_rho(S0,K,r,T,sigma,option_type)
    ana_theta = analytical_theta(S0,K,r,T,sigma,option_type)
    delta_err = abs(ana_delta - num_delta)
    gamma_err = abs(ana_gamma - num_gamma)
    vega_err = abs(ana_vega - num_vega)
    rho_err = abs(ana_rho - num_rho)
    theta_err = abs(ana_theta - num_theta)
    TV = opt_price - intrinsic
    premium.append(opt_price)
    intrinsic_value.append(intrinsic)
    time_value.append(TV)
    spot.append(S0)
    parity.append(parity_check)
    delta1.append(num_delta)
    delta2.append(ana_delta)
    gamma1.append(num_gamma)
    gamma2.append(ana_gamma)
    vega1.append(num_vega)
    vega2.append(ana_vega)
    rho1.append(num_rho)
    rho2.append(ana_rho)
    theta1.append(num_theta)
    theta2.append(ana_theta)
    delta_error.append(delta_err)
    gamma_error.append(gamma_err)
    vega_error.append(vega_err)
    theta_error.append(theta_err)
    rho_error.append(rho_err)
    print(str(S0) + " | Option Price"+"("+str(option_type)+") :"+str(opt_price)+ "| Intrinsic Value : "+str(intrinsic)+" | Time Value : "+str(TV)+" |"+parity_check)

print("\nMaximum Delta error : " + str(max(delta_error)) + 
      "\nMaximum Gamma error : " + str(max(gamma_error)) + 
      "\nMaximum Vega error : " + str(max(vega_error)) + 
      "\nMaximum Rho error : " + str(max(rho_error)) + 
      "\nMaximum Theta error : " + str(max(theta_error)))

S0 = float(input("\nSpot price for IV : "))
K_IV = int(rd.uniform(S0*0.5,S0*1.5))
K_test = []
T_test = []
moneyness = [0.80, 0.85, 0.90, 0.95, 1.0, 1.05, 1.10, 1.15, 1.2]
maturities = [1/12, 3/12, 6/12, 9/12, 1]
up_bracket = 1
down_bracket = 0.000001
sigma_0 = 0.12
a = 0.10
b = 0.05
Smile_market_price = []
Smile_sigma = []

market_price = BSM_pricer(S0, K_IV, r, T, sigma, option_type)

def implied_volatility_solver(S0, K_IV, r, T, sigma, market_price, option_type) :
    count = 0
    diff_down = BSM_pricer(S0, K_IV, r, T , down_bracket, option_type) - market_price
    diff_up = BSM_pricer(S0, K_IV, r, T , up_bracket, option_type) - market_price
    if diff_down * diff_up > 0 :
        print("No findable root")
        return None
    sigma = down_bracket
    diff = BSM_pricer(S0, K_IV, r, T , sigma, option_type) - market_price
    while diff < 0 :
        if count < 50000 :
            sigma += 0.00001
            diff = BSM_pricer(S0, K_IV, r, T , sigma, option_type) - market_price
            count += 1
        else : 
            print("Too many iterations : method stopped")
            return None
    return sigma    

def implied_volatility_dichotomy(S0, K_IV, r, T, market_price, option_type) :
    sigma_up = up_bracket
    sigma_down = down_bracket
    IV = (sigma_up + sigma_down)/2
    diff_final = BSM_pricer(S0, K_IV, r, T, IV, option_type) - market_price
    diff_sigma = sigma_up - sigma_down
    if (BSM_pricer(S0, K_IV, r, T, sigma_up, option_type) - market_price)*(BSM_pricer(S0, K_IV, r, T, sigma_down, option_type) - market_price) <= 0 :
        while abs(diff_sigma) >= 0.0000001 :
            if diff_final > 0 :
                sigma_up = IV          
            elif diff_final < 0 :
                sigma_down = IV
            IV = (sigma_up + sigma_down)/2 
            diff_final = BSM_pricer(S0, K_IV, r, T, IV, option_type) - market_price 
            diff_sigma = sigma_up - sigma_down
    else : 
        print("No findable root for this option")
        return None
    return IV  

def implied_volatility_brentq(sigma):
    diff = BSM_pricer(S0, K_IV, r, T, sigma, option_type) - market_price
    return diff

IV = brentq(implied_volatility_brentq, down_bracket, up_bracket)

IV_smile_test = []

def sigma_surface(S0, K, sigma_0, a, b, T) :
    sigma = sigma_0 + a * (K/S0-1)**2 + b * mt.exp(-T)
    return sigma

def implied_volatility_surface_test():
    for i in range(len(moneyness)) :
        for T in maturities :
            K = int(S0 * moneyness[i])
            K_test.append(K)
            T_test.append(T)
            sigma = sigma_surface(S0, K, sigma_0, a, b, T)
            market_price = BSM_pricer(S0, K, r, T, sigma, option_type)
            def root_finding(sigma):
                diff = BSM_pricer(S0, K, r, T, sigma, option_type) - market_price
                return diff
            Imp_vol_1 = brentq(root_finding, down_bracket, up_bracket)
            Imp_vol_2 = implied_volatility_solver(S0, K, r, T, sigma, market_price, option_type)
            Imp_vol_3 = implied_volatility_dichotomy(S0, K, r, T, market_price, option_type)
            IV1_error = abs(sigma - Imp_vol_1)
            if Imp_vol_2 is None:
                IV2_error = None
            else:
                IV2_error = abs(sigma - Imp_vol_2)
            if Imp_vol_3 is None:
                IV3_error = None
            else:
                IV3_error = abs(sigma - Imp_vol_3)
            IV_smile_test.append((K, T, sigma, Imp_vol_1, Imp_vol_2, Imp_vol_3, IV1_error, IV2_error, IV3_error))   
    return IV_smile_test

IV_smile_test = implied_volatility_surface_test()

for K, T, sigma, Imp_vol_1, Imp_vol_2, Imp_vol_3, IV1_error, IV2_error, IV3_error in IV_smile_test:
    Strike_smile.append(K)
    T_smile.append(T)
    IV_brent.append(Imp_vol_1)
    IV_solver.append(Imp_vol_2)
    IV_dichotomy.append(Imp_vol_3)

IV_true = []

for K, T in zip(Strike_smile, T_smile):
    IV_true.append(sigma_surface(S0, K, sigma_0, a, b, T))   
 
IV_surface = []

previous_K = None

for K, T, sigma, Imp_vol_1, Imp_vol_2, Imp_vol_3, *_ in IV_smile_test:

    if K != previous_K:
        IV_surface.append([])

    IV_surface[-1].append(Imp_vol_1)

    previous_K = K  

fig, axes = plt.subplots(3,3, figsize=(12,10), constrained_layout=True)

axes[1,2].remove()
ax_surface = fig.add_subplot(3,3,6, projection="3d")

#Figure of the delta

axes[0,0].plot(spot, delta1, label = "Numerical Delta", color = "grey")
axes[0,0].plot(spot, delta2, label = "Analytical Delta", color = "orange")
axes[0,0].set_xlabel("Spot (S)")
axes[0,0].set_ylabel("Delta")
axes[0,0].set_title("Delta vs Spot")
axes[0,0].legend()
axes[0,0].grid()

#Figure of the gamma

axes[0,1].plot(spot, gamma1, label = "Numerical Gamma", color = "grey")
axes[0,1].plot(spot, gamma2, label = "Analytical Gamma", color = "orange")
axes[0,1].set_xlabel("Spot (S)")
axes[0,1].set_ylabel("Gamma")
axes[0,1].set_title("Gamma vs Spot")
axes[0,1].legend()
axes[0,1].grid()

#Figure of the vega

axes[1,0].plot(spot, vega1, label = "Numerical Vega", color = "grey")
axes[1,0].plot(spot, vega2, label = "Analytical Vega", color = "orange")
axes[1,0].set_xlabel("Spot (S)")
axes[1,0].set_ylabel("Vega")
axes[1,0].set_title("Vega vs Spot")
axes[1,0].legend()
axes[1,0].grid()

#Figure of the rho

axes[1,1].plot(spot, rho1, label = "Numerical Rho", color = "grey")
axes[1,1].plot(spot, rho2, label = "Analytical Rho", color = "orange")
axes[1,1].set_xlabel("Spot (S)")
axes[1,1].set_ylabel("Rho")
axes[1,1].set_title("Rho vs Spot")
axes[1,1].legend()
axes[1,1].grid()

#Figure of the theta

axes[2,0].plot(spot, theta1, label = "Numerical Theta", color = "grey")
axes[2,0].plot(spot, theta2, label = "Analytical Theta", color = "orange")
axes[2,0].set_xlabel("Spot (S)")
axes[2,0].set_ylabel("Theta")
axes[2,0].set_title("Theta vs Spot")
axes[2,0].legend()
axes[2,0].grid()

#Option Premium

axes[2,1].plot(spot, premium, label = "Option premium", color = "grey")
axes[2,1].plot(spot, intrinsic_value, label = "Intrinsic Value", color = "black")
axes[2,1].set_xlabel("Spot (S)")
axes[2,1].set_ylabel("Option price")
axes[2,1].fill_between(spot, premium, intrinsic_value, label = "Time Value", color = "grey")
axes[2,1].set_title("Premium vs Spot")
axes[2,1].legend()
axes[2,1].grid()

# IV Smile

for j, T in enumerate(maturities):
    axes[0,2].plot(
        moneyness,
        np.array(IV_surface)[:, j],
        label=f"T = {T:.2f}y"
    )

axes[0,2].set_xlabel("Moneyness (K/S)")
axes[0,2].set_ylabel("Implied Volatility")
axes[0,2].set_title("Implied Volatility Smile by Maturity")
axes[0,2].legend()
axes[0,2].grid()


# IV Surface

X, Y = np.meshgrid(moneyness, maturities)

ax_surface.plot_surface(
    X,
    Y,
    np.array(IV_surface).T,
    cmap="coolwarm",
    edgecolor="none"
)

ax_surface.set_xlabel("Moneyness (K/S)")
ax_surface.set_ylabel("Maturity (Years)")
ax_surface.set_zlabel("Implied Volatility")
ax_surface.set_title("Implied Volatility Surface")
ax_surface.view_init(elev=25, azim=-135)

plt.show()





    




