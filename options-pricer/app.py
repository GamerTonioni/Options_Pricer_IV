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

st.markdown("""
<style>
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
    max-width: 100%;
}

[data-testid="stHeader"] {
    height: 0;
}

[data-testid="stToolbar"] {
    visibility: hidden;
}

.custom-header {
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 0.1rem;
}

.custom-subtitle {
    font-size: 0.8rem;
    opacity: 0.7;
    margin-bottom: 0.7rem;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.45rem;
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
    font-size: 1.15rem;
}

div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
    font-size: 0.8rem;
}

div[data-testid="stButton"] button {
    min-height: 2.3rem;
}

h2, h3 {
    font-size: 1.05rem !important;
}

hr {
    margin: 0.4rem 0 !important;
}

@media (max-width: 900px) {
    .block-container {
        padding-left: 0.6rem;
        padding-right: 0.6rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 0.95rem;
    }
}

.block-container {
    padding-top: 0.6rem;
    padding-bottom: 0.4rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.5rem;
}

div[data-testid="stNumberInput"] input {
    min-height: 2rem;
}

div[data-testid="stSelectbox"] {
    margin-bottom: -0.4rem;
}
</style>
""", unsafe_allow_html=True)

# st.markdown(
#     '<div class="custom-header">Options Pricer</div>'
#     '<div class="custom-subtitle">'
#     'Black-Scholes pricing · Implied volatility · Greeks'
#     '</div>',
#     unsafe_allow_html=True,
# )

# Main dashboard: inputs | payoff chart | implied volatility
left_col, chart_col, iv_col = st.columns(
    [0.8, 1.7, 0.9],
    gap="small"
)

with left_col:
    st.subheader("Option inputs")

    spot = st.number_input(
        "Share price (£)",
        min_value=0.01,
        value=100.0,
        step=1.0,
    )

    strike = st.number_input(
        "Strike price (£)",
        min_value=0.01,
        value=100.0,
        step=1.0,
    )

    days = st.number_input(
        "Expiry (days)",
        min_value=1,
        value=91,
        step=1,
    )

    rate = st.number_input(
        "Risk-free rate (%)",
        value=4.0,
        step=0.25,
    )

    volatility = st.number_input(
        "Volatility (%)",
        min_value=0.1,
        value=25.0,
        step=1.0,
    )

    option_type = st.selectbox(
        "Option type",
        ["call", "put"],
    )

time_to_expiry = days / 365
risk_free_rate = rate / 100
vol = volatility / 100

try:
    price = black_scholes(
        spot,
        strike,
        time_to_expiry,
        risk_free_rate,
        vol,
        option_type,
    )

    greeks = calculate_greeks(
        spot,
        strike,
        time_to_expiry,
        risk_free_rate,
        vol,
        option_type,
    )

    premium = price

    break_even = (
        strike + premium
        if option_type == "call"
        else strike - premium
    )

    # CENTRE: payoff chart
    with chart_col:
        st.subheader("Payoff at expiry")

        st.caption(
            "Buyer profit/loss per share, excluding fees."
        )

        low_price = 0.0
        high_price = max(spot, strike, break_even) * 1.5
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
                "Profit/loss: £%{y:.2f}"
                "<extra></extra>"
            ),
        ))

        fig.add_hline(
            y=0,
            line_color="gray",
            line_width=1,
        )

        fig.add_vline(
            x=spot,
            line_color="#805AD5",
            line_dash="dash",
            annotation_text="Current",
            annotation_position="top left",
        )

        fig.add_vline(
            x=strike,
            line_color="#DD6B20",
            line_dash="dash",
            annotation_text="Strike",
            annotation_position="top right",
        )

        fig.add_vline(
            x=break_even,
            line_color="#38A169",
            line_dash="dot",
            annotation_text="Break-even",
            annotation_position="bottom right",
        )

        fig.add_trace(go.Scatter(
            x=[break_even],
            y=[0],
            mode="markers",
            name="Break-even point",
            marker=dict(color="#38A169", size=8),
            hovertemplate=(
                "Break-even: £%{x:.2f}<extra></extra>"
            ),
        ))

        fig.update_layout(
            height=340,
            autosize=True,
            margin=dict(l=5, r=5, t=35, b=5),
            xaxis_title="Share price at expiry (£)",
            yaxis_title="Profit/loss (£ per share)",
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

    # RIGHT: implied volatility calculator
    with iv_col:
        st.subheader("Implied volatility")

        st.caption(
            "Estimate volatility from a market option price."
        )

        with st.form("iv_form"):
            market_price = st.number_input(
                "Market price (£)",
                min_value=0.01,
                value=max(0.01, round(price, 2)),
                step=0.10,
            )

            submitted = st.form_submit_button(
                "Calculate IV",
                width="stretch",
            )

        if submitted:
            try:
                iv = implied_volatility(
                    market_price,
                    spot,
                    strike,
                    time_to_expiry,
                    risk_free_rate,
                    option_type,
                )

                st.metric(
                    "Implied volatility",
                    f"{iv:.2%}",
                )

            except ValueError as error:
                st.error(str(error))

    # BOTTOM: valuation and Greeks
    st.divider()

    # st.caption(
    #     "EUROPEAN OPTIONS · BLACK-SCHOLES · NO DIVIDENDS"
    # )

    st.subheader(f"{option_type.title()} option valuation")

    metrics = st.columns([1.4, 1, 1, 1, 1, 1], gap="small")

    metrics[0].metric(
        "Theoretical price",
        f"£{price:,.2f}",
    )

    metrics[1].metric(
        "Delta",
        f"{greeks['delta']:.4f}",
    )

    metrics[2].metric(
        "Gamma",
        f"{greeks['gamma']:.4f}",
    )

    metrics[3].metric(
        "Vega / 1%",
        f"{greeks['vega'] / 100:.4f}",
    )

    metrics[4].metric(
        "Theta / day",
        f"{greeks['theta']:.4f}",
    )

    metrics[5].metric(
        "Rho / 1%",
        f"{greeks['rho'] / 100:.4f}",
    )

    st.caption(
        "Vega and Rho are per 1 percentage-point change. "
        "Theta is per calendar day."
    )

    st.subheader("Risk & reward")

    risk_cols = st.columns(3, gap="small")

    risk_cols[0].metric(
        "Break-even at expiry",
        f"£{break_even:,.2f}",
    )

    risk_cols[1].metric(
        "Maximum loss / share",
        f"£{premium:,.2f}",
    )

    max_profit_text = (
        "Unlimited"
        if option_type == "call"
        else f"£{max(0, strike - premium):,.2f}"
    )

    risk_cols[2].metric(
        "Maximum profit / share",
        max_profit_text,
    )

except ValueError as error:
    st.error(str(error))
