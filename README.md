# Options Pricer & Implied Volatility Analysis

This is a personal Python project I started to put some of the concepts studied in my Financial Markets courses into practice, while also improving my Python skills.

I started with a Black-Scholes-Merton pricer and progressively added Greeks, implied volatility calculations and a synthetic volatility surface.

## What I implemented

- **BSM Pricer:** European call and put pricing, including intrinsic value, time value and put-call parity checks.
- **Greeks:** Delta, Gamma, Vega, Theta and Rho, calculated using both analytical formulas and central finite differences.
- **Implied Volatility:** Three methods to recover volatility from an option price: incremental search, dichotomy (bisection) and SciPy's Brent method.
- **Volatility Smile & Surface:** Generation of synthetic option prices across different strikes and maturities, followed by IV recovery and visualisation using Matplotlib.

## Methodology

My approach was mainly to try different methods to obtain the same results and compare them.

For the Greeks, I wanted to see how closely numerical approximations could reproduce the analytical formulas.

For implied volatility, I first implemented a simple incremental search, then dichotomy, before using Brent's method as a benchmark.

Finally, I used the following synthetic volatility function to generate different option prices depending on strike and maturity:

sigma(K,T)= sigma_0 + a * (K/S0 - 1)^2 + b * e^(-T)

The objective was to recover these initial volatilities using the IV solvers and construct a volatility surface.

## Results & Observations

A few observations I made while working on the project:

- The analytical and numerical Greeks gave very similar results, which helped me check my calculations.
- Incremental search was easy to implement but considerably slower than the other methods.
- Dichotomy was more efficient, as it progressively reduced the interval containing the solution.
- I encountered difficulties recovering IV for deep ITM options with short maturities. Their low Vega meant that even a very small pricing difference could make IV recovery unreliable.

## Limitations

The project uses European options under BSM assumptions, without dividends.

The volatility smile and surface are entirely synthetic and are not calibrated to real market data. The results also depend on the numerical parameters chosen, particularly the finite-difference steps and IV solver tolerances.

This was mainly an exercise in understanding and implementing the methods rather than building a market-ready pricing tool.

## Tools

Python, NumPy, SciPy and Matplotlib.

## AI Assistance

I wrote the pricing, Greeks and implied volatility calculations myself, using library documentation and AI to help answer questions along the way. AI was also used to assist with parts of the visualisation code.
