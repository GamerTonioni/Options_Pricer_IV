
import math


def normal_cdf(x):
    """Cumulative distribution function of a standard normal variable."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def black_scholes(
    spot,
    strike,
    time_to_expiry,
    risk_free_rate,
    volatility,
    option_type="call",
):
    """
    Calculate the theoretical price of a European option.

    Parameters:
        spot: Current underlying asset price
        strike: Option strike price
        time_to_expiry: Years until expiry
        risk_free_rate: Annual risk-free rate as a decimal
        volatility: Annualised volatility as a decimal
        option_type: "call" or "put"

    Assumes no dividends and continuous compounding.
    """
    if spot <= 0 or strike <= 0:
        raise ValueError("Spot and strike must be positive.")

    if time_to_expiry <= 0:
        raise ValueError("Time to expiry must be positive.")

    if volatility <= 0:
        raise ValueError("Volatility must be positive.")

    if option_type not in ("call", "put"):
        raise ValueError("Option type must be 'call' or 'put'.")

    sqrt_t = math.sqrt(time_to_expiry)

    d1 = (
        math.log(spot / strike)
        + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry
    ) / (volatility * sqrt_t)

    d2 = d1 - volatility * sqrt_t

    if option_type == "call":
        price = (
            spot * normal_cdf(d1)
            - strike
            * math.exp(-risk_free_rate * time_to_expiry)
            * normal_cdf(d2)
        )
    else:
        price = (
            strike
            * math.exp(-risk_free_rate * time_to_expiry)
            * normal_cdf(-d2)
            - spot * normal_cdf(-d1)
        )

    return price



def implied_volatility(
    market_price,
    spot,
    strike,
    time_to_expiry,
    risk_free_rate,
    option_type="call",
    tolerance=1e-6,
    max_iterations=200,
):
    """Estimate implied volatility using bisection with price validation."""

    # Validate inputs
    values = {
        "Market price": market_price,
        "Spot": spot,
        "Strike": strike,
        "Time to expiry": time_to_expiry,
        "Risk-free rate": risk_free_rate,
        "Tolerance": tolerance,
    }

    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")

    if market_price <= 0:
        raise ValueError("Market price must be positive.")

    if spot <= 0 or strike <= 0:
        raise ValueError("Spot and strike must be positive.")

    if time_to_expiry <= 0:
        raise ValueError("Time to expiry must be positive.")

    if option_type not in ("call", "put"):
        raise ValueError("Option type must be 'call' or 'put'.")

    if tolerance <= 0:
        raise ValueError("Tolerance must be positive.")

    if max_iterations < 1:
        raise ValueError("Maximum iterations must be at least 1.")

    # Theoretical price bounds for European options without dividends
    discount_factor = math.exp(-risk_free_rate * time_to_expiry)
    discounted_strike = strike * discount_factor

    if option_type == "call":
        lower_bound = max(spot - discounted_strike, 0.0)
        upper_bound = spot
    else:
        lower_bound = max(discounted_strike - spot, 0.0)
        upper_bound = discounted_strike

    if market_price <= lower_bound:
        raise ValueError(
            f"Market price is too low for a positive implied volatility. "
            f"The theoretical lower bound is £{lower_bound:.4f}."
        )

    if market_price >= upper_bound:
        raise ValueError(
            f"Market price must be below the theoretical upper bound "
            f"of £{upper_bound:.4f}."
        )

    # Search for volatility between 0.0001% and 500%
    low_vol = 1e-6
    high_vol = 5.0

    low_price = black_scholes(
        spot, strike, time_to_expiry, risk_free_rate,
        low_vol, option_type
    )
    high_price = black_scholes(
        spot, strike, time_to_expiry, risk_free_rate,
        high_vol, option_type
    )

    if not (low_price <= market_price <= high_price):
        raise ValueError(
            "Implied volatility is outside the solver's supported "
            "range of approximately 0% to 500%."
        )

    # Bisection search
    for _ in range(max_iterations):
        mid_vol = (low_vol + high_vol) / 2

        estimated_price = black_scholes(
            spot, strike, time_to_expiry, risk_free_rate,
            mid_vol, option_type
        )

        difference = estimated_price - market_price

        if abs(difference) < tolerance:
            return mid_vol

        if difference < 0:
            low_vol = mid_vol
        else:
            high_vol = mid_vol

    raise ValueError(
        "Implied volatility solver did not converge. "
        "Try increasing max_iterations or adjusting the tolerance."
    )


def normal_pdf(x):
    """Probability density function of a standard normal variable."""
    return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)



def calculate_greeks(
    spot,
    strike,
    time_to_expiry,
    risk_free_rate,
    volatility,
    option_type="call",
):
    """Calculate the five Black-Scholes Greeks for a European option."""

    if spot <= 0 or strike <= 0:
        raise ValueError("Spot and strike must be positive.")

    if time_to_expiry <= 0:
        raise ValueError("Time to expiry must be positive.")

    if volatility <= 0:
        raise ValueError("Volatility must be positive.")

    if option_type not in ("call", "put"):
        raise ValueError("Option type must be 'call' or 'put'.")

    sqrt_t = math.sqrt(time_to_expiry)

    d1 = (
        math.log(spot / strike)
        + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry
    ) / (volatility * sqrt_t)

    d2 = d1 - volatility * sqrt_t

    pdf_d1 = normal_pdf(d1)

    # Delta: sensitivity to the underlying share price
    if option_type == "call":
        delta = normal_cdf(d1)
    else:
        delta = normal_cdf(d1) - 1

    # Gamma: rate of change of Delta
    gamma = pdf_d1 / (spot * volatility * sqrt_t)

    # Vega: price change for a 1.00 change in volatility
    vega = spot * pdf_d1 * sqrt_t

    # Theta: price change per calendar day, approximately
    common_theta = (
        -(spot * pdf_d1 * volatility) / (2 * sqrt_t)
    )

    if option_type == "call":
        theta = (
            common_theta
            - risk_free_rate * strike
            * math.exp(-risk_free_rate * time_to_expiry)
            * normal_cdf(d2)
        )
        rho = (
            strike * time_to_expiry
            * math.exp(-risk_free_rate * time_to_expiry)
            * normal_cdf(d2)
        )
    else:
        theta = (
            common_theta
            + risk_free_rate * strike
            * math.exp(-risk_free_rate * time_to_expiry)
            * normal_cdf(-d2)
        )
        rho = (
            -strike * time_to_expiry
            * math.exp(-risk_free_rate * time_to_expiry)
            * normal_cdf(-d2)
        )

    return {
        "delta": delta,
        "gamma": gamma,
        "vega": vega,
        "theta": theta / 365,
        "rho": rho,
    }



if __name__ == "__main__":
    call_price = black_scholes(
        spot=100,
        strike=100,
        time_to_expiry=0.25,
        risk_free_rate=0.04,
        volatility=0.25,
        option_type="call",
    )

    put_price = black_scholes(
        spot=100,
        strike=100,
        time_to_expiry=0.25,
        risk_free_rate=0.04,
        volatility=0.25,
        option_type="put",
    )

    print(f"European call price: GBP {call_price:.2f}")
    print(f"European put price:  GBP {put_price:.2f}")

    market_price = 5.47

    iv = implied_volatility(
        market_price=market_price,
        spot=100,
        strike=100,
        time_to_expiry=0.25,
        risk_free_rate=0.04,
        option_type="call",
    )

    print(f"Implied volatility: {iv:.2%}")


    
    greeks = calculate_greeks(
        spot=100,
        strike=100,
        time_to_expiry=0.25,
        risk_free_rate=0.04,
        volatility=0.25,
        option_type="call",
    )

    for greek, value in greeks.items():
        print(f"{greek.capitalize()}: {value:.6f}")



