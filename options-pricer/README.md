# Options Pricer & Implied Volatility Calculator

A Python-based options pricing application that implements the Black–Scholes model to calculate European call and put option prices, estimate implied volatility, and analyse option risk using the Greeks.

The project combines financial mathematics, numerical methods, automated testing, and an interactive Streamlit dashboard.

## Features

- **Black–Scholes pricing:** Calculate theoretical prices for European call and put options.
- **Implied volatility:** Estimate implied volatility from a market option price using the bisection method.
- **Option Greeks:** Calculate Delta, Gamma, Vega, Theta, and Rho to analyse option price sensitivities.
- **Interactive dashboard:** Explore pricing scenarios using adjustable inputs and real-time calculations.
- **Payoff visualisation:** Plot potential profit and loss at expiry, including the strike price and break-even point.
- **Input validation:** Handle invalid inputs and option prices outside the supported theoretical bounds.
- **Automated tests:** Validate pricing calculations, Greeks, implied volatility recovery, and error handling.

## Technologies

- Python
- Streamlit
- Plotly
- `unittest` and `pytest`

## Financial Model

The application uses the Black–Scholes model for European options on a non-dividend-paying underlying asset.

For a call option:

\[
C=S N(d_1)-K e^{-rT}N(d_2)
\]

For a put option:

\[
P=K e^{-rT}N(-d_2)-S N(-d_1)
\]

Where:

\[
d_1=\frac{\ln(S/K)+(r+\sigma^2/2)T}{\sigma\sqrt{T}}
\]

\[
d_2=d_1-\sigma\sqrt{T}
\]

Here, \(S\) is the underlying asset price, \(K\) is the strike price, \(T\) is time to expiry in years, \(r\) is the continuously compounded risk-free interest rate, and \(\sigma\) is volatility. \(N(x)\) denotes the standard normal cumulative distribution function.

### Implied Volatility

Implied volatility is estimated by finding the volatility that makes the model price match the observed market price. The application uses the **bisection method**, a numerical root-finding technique, with validation to reject unsupported prices.

### The Greeks

The application calculates:

- **Delta:** Sensitivity of the option price to the underlying asset price.
- **Gamma:** Sensitivity of Delta to the underlying asset price.
- **Vega:** Sensitivity to volatility.
- **Theta:** Sensitivity to the passage of time.
- **Rho:** Sensitivity to the risk-free interest rate.

These measures help explain the key risk exposures of an option position.

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

Replace the placeholders with your actual GitHub repository URL and folder name.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install streamlit plotly pytest
```

If your code imports additional libraries, install those as well. Once your environment is working, you can record the project's dependencies in `requirements.txt`.

## Run the Application

From the project root directory, run:

```bash
python -m streamlit run options-pricer/app.py
```

Streamlit will provide a local URL where you can interact with the calculator in your browser.

## Run the Tests

Run the automated test suite with:

```bash
python -m pytest -v
```

The current test suite contains **13 passing tests**, covering option pricing, implied volatility recovery, Greeks, and invalid-input handling.

## Project Structure

```text
Options Pricer + Implied Volatility Calculator/
├── options-pricer/
│   ├── app.py
│   ├── options_pricer.py
│   └── test_options_pricer.py
├── README.md
└── requirements.txt
```

Adjust this structure if your actual files are organised differently.

## Assumptions and Limitations

- Prices European-style options that can only be exercised at expiry.
- Assumes the underlying asset pays no dividends.
- Assumes constant volatility and a constant risk-free interest rate over the option's life.
- Uses a numerical method with finite volatility bounds to estimate implied volatility.
- Produces theoretical model values, not guaranteed market prices or trading recommendations.

## Future Improvements

- Add dividend-adjusted Black–Scholes pricing.
- Visualise option prices and Greeks across different volatility and expiry scenarios.
- Compare theoretical prices with live or historical market data.
- Add interactive volatility and sensitivity surfaces.
- Expand test coverage for edge cases and numerical accuracy.

## Disclaimer

This project is for educational and portfolio demonstration purposes only. It is not financial advice and should not be used as the sole basis for investment decisions.

## Author

Developed as a Python and quantitative finance portfolio project, demonstrating financial modelling, numerical methods, software testing, and interactive data visualisation.