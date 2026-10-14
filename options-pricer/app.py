
import streamlit as st
import plotly.graph_objects as go

from options_pricer import (
    black_scholes,
    implied_volatility,
    calculate_greeks,
)

st.set_page_config(
    page_title="Options Pricer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Compact styling
st.markdown("""
<style>
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 0.3rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}
h1 {
    font-size: 1.65rem !important;
    padding-bottom: 0 !important;
    margin-bottom: 0 !important;
}
h2, h3 {
    font-size: 1.05rem !important;
    padding-bottom: 0 !important;
}
p {
    margin-bottom: 0.3rem !important;
}
div[data-testid="stVerticalBlock"] {
    gap: 0.55rem;
}
div[data-testid="stMetric"] {
    padding: 0.35rem 0.45rem;
    background: rgba(128, 128, 128, 0.07);
    border-radius: 7px;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.75rem;
}
div[data-testid="stMetricValue"] {
    font-size: 1.25rem;
}
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
    font-size: 0.78rem;
}
div[data-testid="stNumberInput"] input {
    font-size: 0.9rem;
}
div[data-testid="stButton"] button {
    min-height: 2.4rem;
}
hr {
    margin: 0.35rem 0 !important;
}
@media (max-width: 900px) {
    .block-container {
        padding-left: 0.7rem;
        padding-right: 0.7rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1rem;
    }
}

/* Hide Streamlit's top toolbar and decoration */
[data-testid="stHeader"] {
    height: 0rem;
    background: transparent;
}

[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}

/* Reduce space above the app content */
.block-container {
    padding-top: 0.6rem !important;
}

/* Custom compact app header */
.custom-header {
    font-size: 1.65rem;
    font-weight: 700;
    margin: 0 0 0.2rem 0;
    padding: 0;
    line-height: 1.2;
}

.custom-subtitle {
    font-size: 0.8rem;
    opacity: 0.7;
    margin-bottom: 0.6rem;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="custom-header">Options Pricer</div>'
    '<div class="custom-subtitle">'
    'Black-Scholes pricing · Implied volatility · Greeks'
    '</div>',
    unsafe_allow_html=True
)


# st.title("Options Pricer")
# st.caption("Black–Scholes · European options · No dividends")

# All market inputs in one horizontal row
inputs = st.columns(6, gap="small")

spot = inputs[0].number_input(
    "Share (£)", min_value=0.01, value=100.0, step=1.0
)
strike = inputs[1].number_input(
    "Strike (£)", min_value=0.01, value=100.0, step=1.0
)
days = inputs[2].number_input(
    "Expiry (days)", min_value=1, value=91, step=1
)
rate = inputs[3].number_input(
    "Rate (%)", value=4.0, step=0.25
)
volatility = inputs[4].number_input(
    "Volatility (%)", min_value=0.1, value=25.0, step=1.0
)
option_type = inputs[5].selectbox(
    "Option", ["call", "put"]
)

time_to_expiry = days / 365
risk_free_rate = rate / 100
vol = volatility / 100

try:
    price = black_scholes(
        spot, strike, time_to_expiry,
        risk_free_rate, vol, option_type,
    )

    greeks = calculate_greeks(
        spot, strike, time_to_expiry,
        risk_free_rate, vol, option_type,
    )

    
    st.divider()

    st.caption(
        "EUROPEAN OPTIONS  ·  BLACK–SCHOLES  ·  NO DIVIDENDS"
    )

    st.subheader(f"{option_type.title()} option valuation")

    # Give the theoretical price more space than the Greeks
    metrics = st.columns([1.5, 1, 1, 1, 1, 1], gap="small")

    metrics[0].metric(
        "Theoretical price",
        f"£{price:,.2f}",
    )
    metrics[1].metric("Delta", f"{greeks['delta']:.4f}")
    metrics[2].metric("Gamma", f"{greeks['gamma']:.4f}")
    metrics[3].metric("Vega / 1%", f"{greeks['vega'] / 100:.4f}")
    metrics[4].metric("Theta / day", f"{greeks['theta']:.4f}")
    metrics[5].metric("Rho / 1%", f"{greeks['rho'] / 100:.4f}")

    st.caption(
        "Vega and Rho are per 1 percentage-point change. "
        "Theta is per calendar day."
    )

    st.divider()


    # Risk and reward for the option buyer
    st.subheader("Risk & reward")

    premium = price
    break_even = (
        strike + premium
        if option_type == "call"
        else strike - premium
    )

    risk_cols = st.columns(3, gap="small")

    risk_cols[0].metric(
        "Break-even at expiry",
        f"£{break_even:,.2f}",
    )

    risk_cols[1].metric(
        "Maximum loss",
        f"£{premium:,.2f} per share",
    )

    if option_type == "call":
        max_profit_text = "Unlimited"
    else:
        max_profit_text = f"£{max(0, strike - premium):,.2f} per share"

    risk_cols[2].metric(
        "Maximum profit",
        max_profit_text,
    )

    
    
    # Interactive payoff chart
    st.subheader("Payoff at expiry")

    st.caption(
        "Profit or loss per share for the option buyer. "
        "Excludes fees and transaction costs."
    )

    premium = price

    break_even = (
        strike + premium
        if option_type == "call"
        else strike - premium
    )

    
    low_price = 0.0
    high_price = max(spot, strike, break_even) * 1.5

    # Ensure the chart range includes the break-even point
    high_price = max(high_price, break_even + 1.0)


    price_points = [
        low_price + i * (high_price - low_price) / 200
        for i in range(201)
    ]

    if option_type == "call":
        payoff = [
            max(s - strike, 0) - premium
            for s in price_points
        ]
    else:
        payoff = [
            max(strike - s, 0) - premium
            for s in price_points
        ]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=price_points,
        y=payoff,
        mode="lines",
        name="Profit / loss",
        line=dict(color="#3182CE", width=3),
        hovertemplate=(
            "Share price: £%{x:.2f}<br>"
            "Profit/loss: £%{y:.2f}<extra></extra>"
        ),
    ))

    # Zero-profit reference line
    fig.add_hline(
        y=0,
        line_color="gray",
        line_dash="solid",
        line_width=1,
    )

    # Current share price
    fig.add_vline(
        x=spot,
        line_color="#805AD5",
        line_dash="dash",
        annotation_text="Current share",
        annotation_position="top left",
    )

    # Strike price
    fig.add_vline(
        x=strike,
        line_color="#DD6B20",
        line_dash="dash",
        annotation_text="Strike",
        annotation_position="top right",
    )

    
    # Break-even price
    fig.add_vline(
        x=break_even,
        line_color="#38A169",
        line_dash="dot",
        annotation_text=f"Break-even £{break_even:.2f}",
        annotation_position="bottom right",
    )

    # Highlight the break-even point on the zero-profit line
    fig.add_trace(go.Scatter(
        x=[break_even],
        y=[0],
        mode="markers",
        name="Break-even point",
        marker=dict(color="#38A169", size=9),
        hovertemplate=(
            "Break-even: £%{x:.2f}<br>"
            "Profit/loss: £%{y:.2f}<extra></extra>"
        ),
    ))


    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=45, b=10),
        xaxis_title="Share price at expiry (£)",
        yaxis_title="Profit / loss per share (£)",
        hovermode="x",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )

    fig.update_xaxes(rangemode="tozero")
    fig.update_yaxes(zeroline=False)

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False},
    )

    # Compact implied volatility section
    st.subheader("Implied volatility")

    with st.form("iv_form"):
        iv_cols = st.columns([2, 1, 1], gap="small")

        market_price = iv_cols[0].number_input(
            "Market option price (£)",
            min_value=0.01,
            value=max(0.01, round(price, 2)),
            step=0.10,
        )

        iv_cols[1].markdown(
            "<div style='padding-top: 2rem; font-size: 0.8rem;'>"
            "Solve for market-implied volatility</div>",
            unsafe_allow_html=True,
        )

        submitted = iv_cols[2].form_submit_button(
            "Calculate IV",
            width="stretch",
        )

    if submitted:
        try:
            iv = implied_volatility(
                market_price, spot, strike,
                time_to_expiry, risk_free_rate, option_type,
            )
            st.success(f"Implied volatility: {iv:.2%}")
        except ValueError as error:
            st.error(str(error))

except ValueError as error:
    st.error(str(error))
