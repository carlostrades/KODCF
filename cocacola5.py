"""
KO Equity Valuation Streamlit App
---------------------------------
Run with:
    streamlit run app.py

Install dependencies:
    pip install streamlit pandas numpy plotly openpyxl

Purpose:
    Estimate the intrinsic value of The Coca-Cola Company (KO) using a revenue-based
    discounted cash flow model and compare the result to KO's current market price.

This version is organized into tabs so the app is easier to navigate.
"""

from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =====================================================
# Page setup
# =====================================================
st.set_page_config(
    page_title="Coca Cola DCF Valuation",
    page_icon="🥤",
    layout="wide",
)


# =====================================================
# Styling
# =====================================================
st.markdown(
    """
    <style>
        .stApp {
            background-color: #ffffff !important;
            color: #111111 !important;
        }
        .stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div,
        .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] span {
            color: #111111 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #fff5f5 !important;
        }
        [data-testid="stSidebar"] * {
            color: #111111 !important;
        }
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea,
        [data-testid="stSidebar"] [data-baseweb="input"] input,
        [data-testid="stSidebar"] [data-baseweb="textarea"] textarea {
            color: #FFFFFF !important;
            background-color: #111111 !important;
            caret-color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] input::placeholder,
        [data-testid="stSidebar"] textarea::placeholder {
            color: #DDDDDD !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #F40009 !important;
        }
        .main-title {
            font-size: 44px;
            font-weight: 900;
            color: #F40009 !important;
            margin-bottom: 0px;
        }
        .subtitle {
            font-size: 18px;
            color: #111111 !important;
            margin-top: 0px;
            margin-bottom: 20px;
        }
        .coke-card {
            background: linear-gradient(135deg, #F40009 0%, #9b0000 100%);
            color: white !important;
            padding: 24px;
            border-radius: 18px;
            box-shadow: 0 5px 16px rgba(244, 0, 9, 0.25);
            margin-bottom: 22px;
        }
        .coke-card h3, .coke-card p, .coke-card div, .coke-card span {
            color: white !important;
        }
        .formula-box {
            background-color: #fff7f7 !important;
            color: #111111 !important;
            border-left: 7px solid #F40009;
            padding: 16px;
            border-radius: 10px;
            margin-top: 10px;
            margin-bottom: 10px;
            border: 1px solid #f0d0d0;
        }
        .formula-box, .formula-box * {
            color: #111111 !important;
        }
        [data-testid="stMetric"] {
            background-color: #ffffff !important;
            border: 1px solid #eeeeee;
            border-radius: 12px;
            padding: 10px;
        }
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
            color: #F40009 !important;
        }
        [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
            color: #111111 !important;
        }
        [data-testid="stMetricDelta"], [data-testid="stMetricDelta"] * {
            color: #111111 !important;
        }
        [data-testid="stExpander"] {
            background-color: #ffffff !important;
            color: #111111 !important;
            border: 1px solid #eeeeee;
        }
        [data-testid="stExpander"] * {
            color: #111111 !important;
        }
        [data-testid="stDataFrame"] * {
            color: #111111 !important;
        }
        .stAlert, .stAlert * {
            color: #111111 !important;
        }
        /* General button styling */
        button,
        [data-testid="stSidebar"] button,
        .stDownloadButton button {
            background-color: #111111 !important;
            color: #F40009 !important;
            border: 2px solid #F40009 !important;
            border-radius: 10px !important;
            font-weight: 800 !important;
        }
        button *,
        [data-testid="stSidebar"] button *,
        .stDownloadButton button * {
            color: #F40009 !important;
            font-weight: 800 !important;
        }
        button:hover,
        [data-testid="stSidebar"] button:hover,
        .stDownloadButton button:hover {
            background-color: #000000 !important;
            color: #F40009 !important;
            border: 2px solid #F40009 !important;
        }
        button:hover *,
        [data-testid="stSidebar"] button:hover *,
        .stDownloadButton button:hover * {
            color: #F40009 !important;
        }

        /* Tab buttons: white background, black text, red border */
        [data-baseweb="tab-list"] button,
        [data-testid="stTabs"] button,
        [role="tab"] {
            background-color: #FFFFFF !important;
            color: #111111 !important;
            border: 2px solid #F40009 !important;
            border-radius: 10px !important;
            font-weight: 800 !important;
            margin-right: 8px !important;
        }
        [data-baseweb="tab-list"] button *,
        [data-testid="stTabs"] button *,
        [role="tab"] * {
            color: #111111 !important;
            font-weight: 800 !important;
        }
        [data-baseweb="tab-list"] button:hover,
        [data-testid="stTabs"] button:hover,
        [role="tab"]:hover {
            background-color: #fff5f5 !important;
            color: #111111 !important;
            border: 2px solid #F40009 !important;
        }
        [data-baseweb="tab-highlight"] {
            background-color: #F40009 !important;
        }

        /* Expanders: white background with black text */
        [data-testid="stExpander"],
        [data-testid="stExpander"] details,
        [data-testid="stExpander"] summary {
            background-color: #FFFFFF !important;
            color: #111111 !important;
            border-color: #DDDDDD !important;
        }
        [data-testid="stExpander"] *,
        [data-testid="stExpander"] summary *,
        [data-testid="stExpander"] div,
        [data-testid="stExpander"] p,
        [data-testid="stExpander"] span {
            color: #111111 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# Image paths
# =====================================================
APP_FOLDER = Path(__file__).parent
POSTER_IMAGE_PATH = APP_FOLDER / "coke_poster.png"
LOGO_IMAGE_PATH = APP_FOLDER / "coke_logo.png"


# =====================================================
# Header
# =====================================================
header_left, header_right = st.columns([3, 1])

with header_left:
    st.markdown('<div class="main-title">🥤 Coca Cola DCF Valuation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">A transparent DCF model for estimating KO intrinsic value and comparing it to market price.</div>',
        unsafe_allow_html=True,
    )

with header_right:
    if POSTER_IMAGE_PATH.exists():
        st.image(str(POSTER_IMAGE_PATH), width=150)
    else:
        st.caption("Add coke_poster.png to this app folder to show the vintage poster here.")

st.markdown(
    """
    <div class="coke-card">
        <h3>Valuation Goal</h3>
        <p>
        This app helps investors estimate whether a stock appears undervalued, overvalued, or near fair value.
        It projects future free cash flows, discounts them back to today, adjusts for debt and cash,
        and divides by shares outstanding to estimate intrinsic value per share.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# Helper functions
# =====================================================
def currency(value):
    if value is None or pd.isna(value):
        return "N/A"
    return f"${value:,.2f}"


def large_currency(value):
    if value is None or pd.isna(value):
        return "N/A"
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:,.2f}T"
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    return f"${value:,.2f}"


def percent(value):
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.1%}"


def calculate_dcf(
    current_revenue,
    annual_growth_rate,
    ebit_margin,
    tax_rate,
    reinvestment_rate,
    wacc,
    terminal_growth_rate,
    projection_years,
    debt,
    cash,
    shares_outstanding,
):
    if wacc <= terminal_growth_rate or shares_outstanding <= 0:
        return None, None

    rows = []
    present_value_fcf = 0

    for year in range(1, projection_years + 1):
        revenue = current_revenue * ((1 + annual_growth_rate) ** year)
        ebit = revenue * ebit_margin
        nopat = ebit * (1 - tax_rate)
        reinvestment = nopat * reinvestment_rate
        free_cash_flow = nopat - reinvestment
        discount_factor = 1 / ((1 + wacc) ** year)
        pv_fcf = free_cash_flow * discount_factor
        present_value_fcf += pv_fcf

        rows.append(
            {
                "Year": year,
                "Revenue": revenue,
                "EBIT": ebit,
                "NOPAT": nopat,
                "Reinvestment": reinvestment,
                "Free Cash Flow": free_cash_flow,
                "Discount Factor": discount_factor,
                "PV of FCF": pv_fcf,
            }
        )

    final_year_fcf = rows[-1]["Free Cash Flow"]
    terminal_value = final_year_fcf * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    pv_terminal_value = terminal_value / ((1 + wacc) ** projection_years)

    enterprise_value = present_value_fcf + pv_terminal_value
    equity_value = enterprise_value - debt + cash
    intrinsic_value_per_share = equity_value / shares_outstanding

    summary = {
        "Present Value of Projected FCF": present_value_fcf,
        "Final Year FCF": final_year_fcf,
        "Terminal Value": terminal_value,
        "Present Value of Terminal Value": pv_terminal_value,
        "Enterprise Value": enterprise_value,
        "Debt": debt,
        "Cash": cash,
        "Equity Value": equity_value,
        "Intrinsic Value Per Share": intrinsic_value_per_share,
    }

    return pd.DataFrame(rows), summary


def margin_of_safety(intrinsic_value, current_market_price):
    if current_market_price <= 0:
        return np.nan
    return (intrinsic_value - current_market_price) / current_market_price


def apply_clean_chart_layout(fig, title, x_title=None, y_title=None, height=440):
    fig.update_layout(
        title=dict(text=title, font=dict(color="#F40009", size=21, family="Arial Black"), x=0.02),
        xaxis_title=x_title,
        yaxis_title=y_title,
        height=height,
        margin=dict(l=45, r=35, t=75, b=55),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#111111", size=13),
        xaxis=dict(
            title=dict(font=dict(color="#111111")),
            tickfont=dict(color="#111111"),
            color="#111111",
            gridcolor="#E6E6E6",
            linecolor="#111111",
            zerolinecolor="#999999",
        ),
        yaxis=dict(
            title=dict(font=dict(color="#111111")),
            tickfont=dict(color="#111111"),
            color="#111111",
            gridcolor="#E6E6E6",
            linecolor="#111111",
            zerolinecolor="#999999",
        ),
        legend=dict(font=dict(color="#111111"), bgcolor="#FFFFFF", bordercolor="#DDDDDD", borderwidth=1),
        hoverlabel=dict(bgcolor="#FFFFFF", font=dict(color="#111111"), bordercolor="#F40009"),
    )
    return fig


def create_value_comparison_chart(current_market_price, intrinsic_value, ticker):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Current Market Price", "Estimated Intrinsic Value"],
            y=[current_market_price, intrinsic_value],
            text=[currency(current_market_price), currency(intrinsic_value)],
            textposition="outside",
            marker=dict(color=["#111111", "#F40009"], line=dict(color="#111111", width=1.5)),
            textfont=dict(color="#111111", size=14),
        )
    )
    higher_label = "Estimated Intrinsic Value" if intrinsic_value >= current_market_price else "Current Market Price"
    higher_value = max(current_market_price, intrinsic_value)
    fig.add_annotation(
        x=higher_label,
        y=higher_value,
        text="🥤",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor="#F40009",
        ax=0,
        ay=-70,
        font=dict(size=34, color="#111111"),
        bgcolor="#FFFFFF",
        bordercolor="#F40009",
        borderwidth=1,
    )
    apply_clean_chart_layout(fig, f"{ticker} Market Price vs. Intrinsic Value", "Valuation Measure", "Value Per Share")
    return fig


def create_fcf_chart(dcf_table):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dcf_table["Year"],
            y=dcf_table["Free Cash Flow"],
            mode="lines+markers",
            name="Free Cash Flow",
            line=dict(color="#F40009", width=4),
            marker=dict(size=10, color="#FFFFFF", line=dict(color="#F40009", width=2.5)),
        )
    )
    last_year = dcf_table["Year"].iloc[-1]
    last_fcf = dcf_table["Free Cash Flow"].iloc[-1]
    fig.add_annotation(
        x=last_year,
        y=last_fcf,
        text="🥤 FCF",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.4,
        arrowwidth=3,
        arrowcolor="#F40009",
        ax=-60,
        ay=-45,
        font=dict(size=18, color="#111111"),
        bgcolor="#FFFFFF",
        bordercolor="#F40009",
        borderwidth=1,
    )
    apply_clean_chart_layout(fig, "Projected Free Cash Flow", "Projection Year", "Free Cash Flow")
    return fig


def create_revenue_to_fcf_chart(year_one_row):
    categories = ["Revenue", "EBIT", "NOPAT", "Free Cash Flow"]
    values = [year_one_row["Revenue"], year_one_row["EBIT"], year_one_row["NOPAT"], year_one_row["Free Cash Flow"]]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            text=[large_currency(v) for v in values],
            textposition="outside",
            marker=dict(color=["#111111", "#F40009", "#B00000", "#F40009"], line=dict(color="#111111", width=1)),
            textfont=dict(color="#111111", size=13),
        )
    )
    apply_clean_chart_layout(fig, "Year 1 Revenue to Free Cash Flow Breakdown", "DCF Step", "Dollar Amount")
    return fig


def create_ev_bridge_chart(dcf_summary):
    fig = go.Figure(
        go.Waterfall(
            name="EV to Equity Bridge",
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Enterprise Value", "Less: Debt", "Add: Cash", "Equity Value"],
            y=[dcf_summary["Enterprise Value"], -dcf_summary["Debt"], dcf_summary["Cash"], 0],
            text=[
                large_currency(dcf_summary["Enterprise Value"]),
                f"-{large_currency(dcf_summary['Debt'])}",
                large_currency(dcf_summary["Cash"]),
                large_currency(dcf_summary["Equity Value"]),
            ],
            textposition="outside",
            textfont=dict(color="#111111"),
            connector={"line": {"color": "#999999"}},
            increasing={"marker": {"color": "#F40009"}},
            decreasing={"marker": {"color": "#111111"}},
            totals={"marker": {"color": "#B00000"}},
        )
    )
    apply_clean_chart_layout(fig, "Enterprise Value to Equity Value Bridge", "Valuation Step", "Value")
    return fig


# =====================================================
# Defaults and reset logic
# =====================================================
DEFAULT_INPUTS = {
    "ticker_input": "KO",
    "company_name_input": "The Coca-Cola Company",
    "current_market_price_input": 75.44,
    "current_revenue_input": 47_000_000_000.0,
    "annual_growth_rate_input": 4.0,
    "ebit_margin_input": 28.0,
    "tax_rate_input": 19.0,
    "reinvestment_rate_input": 20.0,
    "wacc_input": 7.5,
    "terminal_growth_rate_input": 2.5,
    "projection_years_input": 10,
    "debt_input": 45_000_000_000.0,
    "cash_input": 20_000_000_000.0,
    "shares_outstanding_input": 4_310_000_000.0,
}


def reset_inputs():
    for key, value in DEFAULT_INPUTS.items():
        st.session_state[key] = value


# =====================================================
# Sidebar inputs
# =====================================================
if LOGO_IMAGE_PATH.exists():
    st.sidebar.image(str(LOGO_IMAGE_PATH), use_container_width=True)
else:
    st.sidebar.caption("Add coke_logo.png to this app folder to show the Coca-Cola logo here.")

st.sidebar.header("Valuation Inputs")
st.sidebar.caption("Inputs are grouped to make the model easier to use and understand.")
st.sidebar.button("Reset Inputs to Defaults", on_click=reset_inputs)
st.sidebar.divider()

st.sidebar.subheader("1. Stock Selection")
ticker = st.sidebar.text_input("Ticker Symbol", value=DEFAULT_INPUTS["ticker_input"], key="ticker_input").upper().strip()
company_name = st.sidebar.text_input("Company Name", value=DEFAULT_INPUTS["company_name_input"], key="company_name_input")

st.sidebar.subheader("2. Market Price")
current_market_price = st.sidebar.number_input(
    "Current Market Price ($)", min_value=0.01, max_value=500.00, value=DEFAULT_INPUTS["current_market_price_input"], step=0.25, key="current_market_price_input"
)

st.sidebar.subheader("3. Operating Forecast")
current_revenue = st.sidebar.number_input(
    "Current Revenue ($)", min_value=1_000_000.0, max_value=500_000_000_000.0, value=DEFAULT_INPUTS["current_revenue_input"], step=500_000_000.0, key="current_revenue_input"
)
annual_growth_rate = st.sidebar.slider("Annual Growth Rate (%)", -5.0, 15.0, DEFAULT_INPUTS["annual_growth_rate_input"], 0.25, key="annual_growth_rate_input") / 100
ebit_margin = st.sidebar.slider("EBIT Margin (%)", 0.0, 50.0, DEFAULT_INPUTS["ebit_margin_input"], 0.25, key="ebit_margin_input") / 100
tax_rate = st.sidebar.slider("Tax Rate (%)", 0.0, 40.0, DEFAULT_INPUTS["tax_rate_input"], 0.25, key="tax_rate_input") / 100
reinvestment_rate = st.sidebar.slider("Reinvestment Rate (%)", 0.0, 80.0, DEFAULT_INPUTS["reinvestment_rate_input"], 0.5, key="reinvestment_rate_input") / 100

st.sidebar.subheader("4. Discount Rate and Terminal Value")
wacc = st.sidebar.slider("WACC (%)", 3.0, 15.0, DEFAULT_INPUTS["wacc_input"], 0.25, key="wacc_input") / 100
terminal_growth_rate = st.sidebar.slider("Terminal Growth (%)", 0.0, 5.0, DEFAULT_INPUTS["terminal_growth_rate_input"], 0.25, key="terminal_growth_rate_input") / 100
projection_years = st.sidebar.slider("Projection Years", 3, 15, DEFAULT_INPUTS["projection_years_input"], 1, key="projection_years_input")

st.sidebar.subheader("5. Capital Structure")
debt = st.sidebar.number_input("Debt ($)", 0.0, 200_000_000_000.0, DEFAULT_INPUTS["debt_input"], 1_000_000_000.0, key="debt_input")
cash = st.sidebar.number_input("Cash ($)", 0.0, 200_000_000_000.0, DEFAULT_INPUTS["cash_input"], 1_000_000_000.0, key="cash_input")
shares_outstanding = st.sidebar.number_input("Shares Outstanding", 1_000_000.0, 20_000_000_000.0, DEFAULT_INPUTS["shares_outstanding_input"], 10_000_000.0, key="shares_outstanding_input")


# =====================================================
# DCF calculations
# =====================================================
dcf_table, dcf_summary = calculate_dcf(
    current_revenue=current_revenue,
    annual_growth_rate=annual_growth_rate,
    ebit_margin=ebit_margin,
    tax_rate=tax_rate,
    reinvestment_rate=reinvestment_rate,
    wacc=wacc,
    terminal_growth_rate=terminal_growth_rate,
    projection_years=projection_years,
    debt=debt,
    cash=cash,
    shares_outstanding=shares_outstanding,
)

if dcf_table is None or dcf_summary is None:
    st.error("The model cannot calculate value because WACC must be greater than terminal growth and shares outstanding must be positive.")
    st.stop()

intrinsic_value = dcf_summary["Intrinsic Value Per Share"]
mos = margin_of_safety(intrinsic_value, current_market_price)
upside_downside = intrinsic_value - current_market_price
market_cap = current_market_price * shares_outstanding
implied_equity_value = intrinsic_value * shares_outstanding

if mos >= 0.15:
    verdict = "Potentially Undervalued"
    verdict_explanation = "The estimated intrinsic value is at least 15% above the current market price."
elif mos <= -0.15:
    verdict = "Potentially Overvalued"
    verdict_explanation = "The estimated intrinsic value is at least 15% below the current market price."
else:
    verdict = "Near Fair Value"
    verdict_explanation = "The estimated intrinsic value is within roughly 15% of the current market price."


# =====================================================
# Dashboard
# =====================================================
st.header(f"{ticker} Valuation Dashboard")
st.write(f"Company being valued: **{company_name}**")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Market Price", currency(current_market_price))
col2.metric("Intrinsic Value / Share", currency(intrinsic_value), delta=currency(upside_downside))
col3.metric("Margin of Safety", percent(mos))
col4.metric("Implied Equity Value", large_currency(implied_equity_value))

st.subheader(verdict)
st.write(verdict_explanation)

left_col, right_col = st.columns(2)
with left_col:
    st.plotly_chart(create_value_comparison_chart(current_market_price, intrinsic_value, ticker), use_container_width=True)
with right_col:
    st.plotly_chart(create_fcf_chart(dcf_table), use_container_width=True)


# =====================================================
# Tabs
# =====================================================
tab_inputs, tab_dcf, tab_excel, tab_analysis, tab_peers, tab_learning = st.tabs(
    ["Input Guide", "DCF + FCFF + WACC", "Excel Replication", "Sensitivity + Scenarios", "Peer Comparisons", "Formulas + Notes"]
)


with tab_inputs:
    st.header("User Input Design")
    with st.expander("Which inputs does the user provide?", expanded=True):
        st.write(
            "The user provides the ticker, current market price, current revenue, growth rate, EBIT margin, tax rate, "
            "reinvestment rate, WACC, terminal growth, projection years, debt, cash, and shares outstanding."
        )
    with st.expander("Which inputs could be retrieved automatically in a real app?"):
        st.write(
            "A real-world version could retrieve current market price, revenue, debt, cash, and shares outstanding from Yahoo Finance, SEC filings, or financial APIs. "
            "This class version keeps them manual so the model is easier to understand and does not require yfinance."
        )
    with st.expander("How does the app help users choose assumptions?"):
        st.write(
            "The sidebar groups inputs by category. The sensitivity and scenario sections show how changes in key assumptions affect value."
        )

    st.header("Input Guide")
    input_guide = {
        "Current Revenue": "Revenue is the starting point of the DCF model. The model grows revenue each year using the annual growth rate.",
        "Annual Growth Rate": "This estimates how quickly sales grow each year. Mature companies like Coca-Cola usually have lower long-term growth.",
        "EBIT Margin": "EBIT margin measures operating income before interest and taxes as a percentage of revenue.",
        "Tax Rate": "The tax rate turns EBIT into NOPAT, or after-tax operating income.",
        "Reinvestment Rate": "Reinvestment estimates how much of NOPAT must be put back into the business. FCFF = NOPAT - Reinvestment.",
        "WACC": "WACC is the discount rate. Higher WACC lowers present value because future cash flows are discounted more heavily.",
        "Terminal Growth": "Terminal growth is the long-term growth rate after the explicit forecast period. It should usually stay below WACC.",
        "Debt, Cash, and Shares Outstanding": "Debt and cash adjust enterprise value into equity value. Shares outstanding converts total equity value into value per share.",
    }
    for title, explanation in input_guide.items():
        with st.expander(title):
            st.write(explanation)


with tab_dcf:
    st.header("DCF Model Summary")
    summary_df = pd.DataFrame(
        {
            "Metric": [
                "Present Value of Projected FCF",
                "Final Year Free Cash Flow",
                "Terminal Value",
                "Present Value of Terminal Value",
                "Enterprise Value",
                "Less: Debt",
                "Add: Cash",
                "Equity Value",
                "Shares Outstanding",
                "Intrinsic Value Per Share",
                "Current Market Price",
                "Market Cap at Current Price",
                "Margin of Safety",
            ],
            "Value": [
                dcf_summary["Present Value of Projected FCF"],
                dcf_summary["Final Year FCF"],
                dcf_summary["Terminal Value"],
                dcf_summary["Present Value of Terminal Value"],
                dcf_summary["Enterprise Value"],
                debt,
                cash,
                dcf_summary["Equity Value"],
                shares_outstanding,
                intrinsic_value,
                current_market_price,
                market_cap,
                mos,
            ],
        }
    )
    summary_display = summary_df.copy()
    summary_display["Value"] = summary_display.apply(
        lambda row: percent(row["Value"])
        if row["Metric"] == "Margin of Safety"
        else currency(row["Value"])
        if row["Metric"] in ["Intrinsic Value Per Share", "Current Market Price"]
        else f"{row['Value']:,.0f}"
        if row["Metric"] == "Shares Outstanding"
        else large_currency(row["Value"]),
        axis=1,
    )
    st.dataframe(summary_display, use_container_width=True, hide_index=True)
    st.plotly_chart(create_ev_bridge_chart(dcf_summary), use_container_width=True)

    st.header("Simple FCFF Intrinsic Value Estimate")
    st.write(
        "This section estimates intrinsic value per share using a simple Free Cash Flow to the Firm approach. "
        "FCFF represents cash flow available to all capital providers before debt payments."
    )
    current_ebit = current_revenue * ebit_margin
    current_nopat = current_ebit * (1 - tax_rate)
    current_reinvestment = current_nopat * reinvestment_rate
    current_fcff = current_nopat - current_reinvestment
    next_year_revenue = current_revenue * (1 + annual_growth_rate)
    next_year_ebit = next_year_revenue * ebit_margin
    next_year_nopat = next_year_ebit * (1 - tax_rate)
    next_year_reinvestment = next_year_nopat * reinvestment_rate
    next_year_fcff = next_year_nopat - next_year_reinvestment
    simple_enterprise_value = next_year_fcff * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    simple_equity_value = simple_enterprise_value - debt + cash
    simple_fcff_value_per_share = simple_equity_value / shares_outstanding
    simple_fcff_mos = margin_of_safety(simple_fcff_value_per_share, current_market_price)

    fcff_col1, fcff_col2, fcff_col3, fcff_col4 = st.columns(4)
    fcff_col1.metric("Current FCFF", large_currency(current_fcff))
    fcff_col2.metric("Next Year FCFF", large_currency(next_year_fcff))
    fcff_col3.metric("FCFF Value / Share", currency(simple_fcff_value_per_share))
    fcff_col4.metric("FCFF Margin of Safety", percent(simple_fcff_mos))

    st.markdown(
        """
        <div class="formula-box">
            <b>FCFF Formula:</b> FCFF = EBIT × (1 - Tax Rate) - Reinvestment<br>
            <b>Terminal Value Formula:</b> Terminal Value = Next Year FCFF × (1 + Terminal Growth) ÷ (WACC - Terminal Growth)<br>
            <b>Equity Value Formula:</b> Equity Value = Enterprise Value - Debt + Cash<br>
            <b>Intrinsic Value Per Share:</b> Equity Value ÷ Shares Outstanding
        </div>
        """,
        unsafe_allow_html=True,
    )

    fcff_summary = pd.DataFrame(
        {
            "Step": [
                "Current Revenue",
                "Current EBIT",
                "Current NOPAT",
                "Current Reinvestment",
                "Current FCFF",
                "Next Year Revenue",
                "Next Year EBIT",
                "Next Year NOPAT",
                "Next Year Reinvestment",
                "Next Year FCFF",
                "Simple FCFF Enterprise Value",
                "Less: Debt",
                "Add: Cash",
                "Simple FCFF Equity Value",
                "Simple FCFF Intrinsic Value Per Share",
            ],
            "Formula / Description": [
                "User input",
                "Current Revenue × EBIT Margin",
                "Current EBIT × (1 - Tax Rate)",
                "Current NOPAT × Reinvestment Rate",
                "Current NOPAT - Current Reinvestment",
                "Current Revenue × (1 + Growth Rate)",
                "Next Year Revenue × EBIT Margin",
                "Next Year EBIT × (1 - Tax Rate)",
                "Next Year NOPAT × Reinvestment Rate",
                "Next Year NOPAT - Next Year Reinvestment",
                "Next Year FCFF × (1 + Terminal Growth) ÷ (WACC - Terminal Growth)",
                "Debt adjustment",
                "Cash adjustment",
                "Enterprise Value - Debt + Cash",
                "Equity Value ÷ Shares Outstanding",
            ],
            "Value": [
                current_revenue,
                current_ebit,
                current_nopat,
                current_reinvestment,
                current_fcff,
                next_year_revenue,
                next_year_ebit,
                next_year_nopat,
                next_year_reinvestment,
                next_year_fcff,
                simple_enterprise_value,
                debt,
                cash,
                simple_equity_value,
                simple_fcff_value_per_share,
            ],
        }
    )
    fcff_display = fcff_summary.copy()
    fcff_display["Value"] = fcff_display.apply(
        lambda row: currency(row["Value"])
        if row["Step"] == "Simple FCFF Intrinsic Value Per Share"
        else large_currency(row["Value"]),
        axis=1,
    )
    st.dataframe(fcff_display, use_container_width=True, hide_index=True)

    st.header("WACC Breakdown with Formulas")
    st.write(
        "WACC is the discount rate used in the DCF model. The sidebar uses your chosen WACC directly, "
        "but this section shows how WACC can be built from equity and debt components."
    )
    wacc_input_col1, wacc_input_col2, wacc_input_col3, wacc_input_col4 = st.columns(4)
    with wacc_input_col1:
        cost_of_equity = st.number_input("Cost of Equity (%)", 0.0, 25.0, 8.0, 0.25) / 100
    with wacc_input_col2:
        pre_tax_cost_of_debt = st.number_input("Pre-Tax Cost of Debt (%)", 0.0, 20.0, 4.5, 0.25) / 100
    with wacc_input_col3:
        market_value_equity = st.number_input("Market Value of Equity ($)", 1_000_000.0, 1_000_000_000_000.0, market_cap, 1_000_000_000.0)
    with wacc_input_col4:
        market_value_debt = st.number_input("Market Value of Debt ($)", 0.0, 500_000_000_000.0, debt, 1_000_000_000.0)

    total_capital = market_value_equity + market_value_debt
    equity_weight = market_value_equity / total_capital if total_capital > 0 else np.nan
    debt_weight = market_value_debt / total_capital if total_capital > 0 else np.nan
    after_tax_cost_of_debt = pre_tax_cost_of_debt * (1 - tax_rate)
    calculated_wacc = (equity_weight * cost_of_equity) + (debt_weight * after_tax_cost_of_debt)

    wacc_metric1, wacc_metric2, wacc_metric3, wacc_metric4 = st.columns(4)
    wacc_metric1.metric("Equity Weight", percent(equity_weight))
    wacc_metric2.metric("Debt Weight", percent(debt_weight))
    wacc_metric3.metric("After-Tax Cost of Debt", percent(after_tax_cost_of_debt))
    wacc_metric4.metric("Calculated WACC", percent(calculated_wacc))

    st.markdown(
        """
        <div class="formula-box">
            <b>Equity Weight:</b> E ÷ (D + E)<br>
            <b>Debt Weight:</b> D ÷ (D + E)<br>
            <b>After-Tax Cost of Debt:</b> Cost of Debt × (1 - Tax Rate)<br>
            <b>WACC:</b> [E ÷ (D + E) × Cost of Equity] + [D ÷ (D + E) × Cost of Debt × (1 - Tax Rate)]
        </div>
        """,
        unsafe_allow_html=True,
    )
    wacc_breakdown = pd.DataFrame(
        {
            "Component": [
                "Market Value of Equity",
                "Market Value of Debt",
                "Total Capital",
                "Equity Weight",
                "Debt Weight",
                "Cost of Equity",
                "Pre-Tax Cost of Debt",
                "Tax Rate",
                "After-Tax Cost of Debt",
                "Calculated WACC",
                "WACC Used in DCF Sidebar",
            ],
            "Formula": [
                "Current Price × Shares Outstanding",
                "User input or total debt approximation",
                "Equity + Debt",
                "Equity ÷ Total Capital",
                "Debt ÷ Total Capital",
                "User input",
                "User input",
                "User input from sidebar",
                "Pre-Tax Cost of Debt × (1 - Tax Rate)",
                "Equity Weight × Cost of Equity + Debt Weight × After-Tax Cost of Debt",
                "User input from sidebar",
            ],
            "Value": [
                large_currency(market_value_equity),
                large_currency(market_value_debt),
                large_currency(total_capital),
                percent(equity_weight),
                percent(debt_weight),
                percent(cost_of_equity),
                percent(pre_tax_cost_of_debt),
                percent(tax_rate),
                percent(after_tax_cost_of_debt),
                percent(calculated_wacc),
                percent(wacc),
            ],
        }
    )
    st.dataframe(wacc_breakdown, use_container_width=True, hide_index=True)


with tab_excel:
    st.header("Excel Replication Table for KO DCF Walkthrough")
    st.write(
        "This section recreates the structure of the Excel DCF model for **KO**. "
        "It includes input assumptions, the DCF forecast, valuation summary, and formula transparency."
    )

    excel_inputs = pd.DataFrame(
        {
            "Input Assumption": [
                "Ticker",
                "Company Name",
                "Current Revenue",
                "Revenue Growth",
                "EBIT Margin",
                "Tax Rate",
                "Reinvestment Rate",
                "WACC",
                "Terminal Growth",
                "Projection Years",
                "Debt",
                "Cash",
                "Shares Outstanding",
                "Current Market Price",
            ],
            "Value": [
                ticker,
                company_name,
                current_revenue,
                annual_growth_rate,
                ebit_margin,
                tax_rate,
                reinvestment_rate,
                wacc,
                terminal_growth_rate,
                projection_years,
                debt,
                cash,
                shares_outstanding,
                current_market_price,
            ],
            "Excel-Style Formula / Source": [
                "User input",
                "User input",
                "User input or latest annual revenue",
                "User input",
                "User input",
                "User input",
                "User input",
                "User input",
                "User input; should be less than WACC",
                "User input",
                "User input or latest total debt",
                "User input or latest cash balance",
                "User input or latest diluted shares outstanding",
                "User input or current market quote",
            ],
        }
    )

    excel_inputs_display = excel_inputs.copy()
    excel_inputs_display["Value"] = excel_inputs_display.apply(
        lambda row: percent(row["Value"])
        if row["Input Assumption"] in ["Revenue Growth", "EBIT Margin", "Tax Rate", "Reinvestment Rate", "WACC", "Terminal Growth"]
        else currency(row["Value"])
        if row["Input Assumption"] == "Current Market Price"
        else large_currency(row["Value"])
        if row["Input Assumption"] in ["Current Revenue", "Debt", "Cash"]
        else f"{row['Value']:,.0f}"
        if row["Input Assumption"] == "Shares Outstanding"
        else row["Value"],
        axis=1,
    )

    st.subheader("1. Input Assumptions")
    st.dataframe(excel_inputs_display, use_container_width=True, hide_index=True)

    excel_forecast = dcf_table[
        [
            "Year",
            "Revenue",
            "EBIT",
            "NOPAT",
            "Reinvestment",
            "Free Cash Flow",
            "Discount Factor",
            "PV of FCF",
        ]
    ].copy()

    st.subheader("2. DCF Forecast")
    st.dataframe(
        excel_forecast.style.format(
            {
                "Revenue": "${:,.0f}",
                "EBIT": "${:,.0f}",
                "NOPAT": "${:,.0f}",
                "Reinvestment": "${:,.0f}",
                "Free Cash Flow": "${:,.0f}",
                "Discount Factor": "{:.4f}",
                "PV of FCF": "${:,.0f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        """
        <div class="formula-box">
            <b>DCF Forecast Formulas:</b><br>
            <b>Revenue:</b> Prior Year Revenue × (1 + Revenue Growth)<br>
            <b>EBIT:</b> Revenue × EBIT Margin<br>
            <b>NOPAT:</b> EBIT × (1 - Tax Rate)<br>
            <b>Reinvestment:</b> NOPAT × Reinvestment Rate<br>
            <b>Free Cash Flow / FCFF:</b> NOPAT - Reinvestment<br>
            <b>Discount Factor:</b> 1 ÷ (1 + WACC)<sup>Year</sup><br>
            <b>PV of FCF:</b> Free Cash Flow × Discount Factor
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.plotly_chart(create_revenue_to_fcf_chart(dcf_table.iloc[0]), use_container_width=True)

    excel_summary = pd.DataFrame(
        {
            "Valuation Summary": [
                "PV of Projected FCF",
                "Terminal Value",
                "PV of Terminal Value",
                "Enterprise Value",
                "Debt",
                "Cash",
                "Equity Value",
                "Intrinsic Value Per Share",
                "Current Market Price",
                "Upside / Downside",
                "Margin of Safety",
            ],
            "Excel-Style Formula": [
                "=SUM(PV of FCF forecast column)",
                "=Final Year FCF × (1 + Terminal Growth) ÷ (WACC - Terminal Growth)",
                "=Terminal Value ÷ (1 + WACC)^Projection Years",
                "=PV of Projected FCF + PV of Terminal Value",
                "=Debt input",
                "=Cash input",
                "=Enterprise Value - Debt + Cash",
                "=Equity Value ÷ Shares Outstanding",
                "=Current Market Price input",
                "=Intrinsic Value Per Share - Current Market Price",
                "=(Intrinsic Value Per Share - Current Market Price) ÷ Current Market Price",
            ],
            "Value": [
                dcf_summary["Present Value of Projected FCF"],
                dcf_summary["Terminal Value"],
                dcf_summary["Present Value of Terminal Value"],
                dcf_summary["Enterprise Value"],
                debt,
                cash,
                dcf_summary["Equity Value"],
                intrinsic_value,
                current_market_price,
                upside_downside,
                mos,
            ],
        }
    )

    excel_summary_display = excel_summary.copy()
    excel_summary_display["Value"] = excel_summary_display.apply(
        lambda row: percent(row["Value"])
        if row["Valuation Summary"] == "Margin of Safety"
        else currency(row["Value"])
        if row["Valuation Summary"] in ["Intrinsic Value Per Share", "Current Market Price", "Upside / Downside"]
        else large_currency(row["Value"]),
        axis=1,
    )

    st.subheader("3. Valuation Summary")
    st.dataframe(excel_summary_display, use_container_width=True, hide_index=True)

    formula_transparency = pd.DataFrame(
        {
            "Line Item": [
                "Revenue",
                "EBIT",
                "NOPAT",
                "Reinvestment",
                "Free Cash Flow / FCFF",
                "Terminal Value",
                "Enterprise Value",
                "Equity Value",
                "Intrinsic Value Per Share",
                "Upside / Downside",
                "Margin of Safety",
            ],
            "Formula Transparency": [
                "Prior Year Revenue × (1 + Revenue Growth)",
                "Revenue × EBIT Margin",
                "EBIT × (1 - Tax Rate)",
                "NOPAT × Reinvestment Rate",
                "NOPAT - Reinvestment",
                "Final Year FCF × (1 + Terminal Growth) ÷ (WACC - Terminal Growth)",
                "PV of Projected FCF + PV of Terminal Value",
                "Enterprise Value - Debt + Cash",
                "Equity Value ÷ Shares Outstanding",
                "Intrinsic Value Per Share - Current Market Price",
                "Upside / Downside ÷ Current Market Price",
            ],
        }
    )

    st.subheader("4. Formula Transparency")
    st.dataframe(formula_transparency, use_container_width=True, hide_index=True)

    combined_excel_export = pd.concat(
        [
            pd.DataFrame({"Section": ["INPUT ASSUMPTIONS"]}),
            excel_inputs,
            pd.DataFrame({"Section": ["DCF FORECAST"]}),
            excel_forecast,
            pd.DataFrame({"Section": ["VALUATION SUMMARY"]}),
            excel_summary,
            pd.DataFrame({"Section": ["FORMULA TRANSPARENCY"]}),
            formula_transparency,
        ],
        ignore_index=True,
        sort=False,
    )

    excel_output = BytesIO()
    with pd.ExcelWriter(excel_output, engine="openpyxl") as writer:
        excel_inputs.to_excel(writer, sheet_name="Inputs", index=False)
        excel_forecast.to_excel(writer, sheet_name="DCF Forecast", index=False)
        excel_summary.to_excel(writer, sheet_name="Valuation Summary", index=False)
        formula_transparency.to_excel(writer, sheet_name="Formulas", index=False)

    excel_output.seek(0)

    st.download_button(
        "Download KO DCF Excel Workbook",
        data=excel_output,
        file_name="ko_dcf_valuation_workbook.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.caption(
        "This download creates a real Excel workbook with separate sheets for Inputs, DCF Forecast, Valuation Summary, and Formulas."
    )


with tab_analysis:
    st.header("Sensitivity Analysis")
    st.write("This table shows how estimated intrinsic value changes when WACC and terminal growth change.")
    wacc_range = np.arange(max(0.03, wacc - 0.02), wacc + 0.025, 0.005)
    terminal_growth_range = np.arange(max(0.00, terminal_growth_rate - 0.01), terminal_growth_rate + 0.0125, 0.0025)
    sensitivity_table = pd.DataFrame(index=[f"{tg:.2%}" for tg in terminal_growth_range])
    for w in wacc_range:
        values = []
        for tg in terminal_growth_range:
            if w <= tg:
                values.append(np.nan)
            else:
                _, sensitivity_summary = calculate_dcf(
                    current_revenue,
                    annual_growth_rate,
                    ebit_margin,
                    tax_rate,
                    reinvestment_rate,
                    w,
                    tg,
                    projection_years,
                    debt,
                    cash,
                    shares_outstanding,
                )
                values.append(sensitivity_summary["Intrinsic Value Per Share"])
        sensitivity_table[f"{w:.2%}"] = values
    st.dataframe(sensitivity_table.style.format("${:,.2f}"), use_container_width=True)

    heatmap = go.Figure(
        data=go.Heatmap(
            z=sensitivity_table.values,
            x=sensitivity_table.columns,
            y=sensitivity_table.index,
            colorbar=dict(
                title=dict(text="Value / Share", font=dict(color="#111111")),
                tickfont=dict(color="#111111"),
                bgcolor="#FFFFFF",
                bordercolor="#111111",
                borderwidth=1,
            ),
            colorscale=[[0, "#FFF2F2"], [0.5, "#F47C7C"], [1, "#F40009"]],
            hovertemplate="Terminal Growth: %{y}<br>WACC: %{x}<br>Value: $%{z:,.2f}<extra></extra>",
        )
    )
    apply_clean_chart_layout(heatmap, "Intrinsic Value Sensitivity: WACC vs. Terminal Growth", "WACC", "Terminal Growth", 470)
    st.plotly_chart(heatmap, use_container_width=True)

    st.header("Scenario Analysis")
    scenarios = {
        "Conservative": {"growth": max(annual_growth_rate - 0.02, -0.05), "ebit_margin": max(ebit_margin - 0.03, 0), "wacc": wacc + 0.01, "terminal_growth": max(terminal_growth_rate - 0.005, 0)},
        "Base Case": {"growth": annual_growth_rate, "ebit_margin": ebit_margin, "wacc": wacc, "terminal_growth": terminal_growth_rate},
        "Optimistic": {"growth": annual_growth_rate + 0.02, "ebit_margin": ebit_margin + 0.03, "wacc": max(wacc - 0.01, 0.01), "terminal_growth": terminal_growth_rate + 0.005},
    }
    scenario_rows = []
    for scenario_name, assumptions in scenarios.items():
        if assumptions["wacc"] <= assumptions["terminal_growth"]:
            scenario_value = np.nan
        else:
            _, scenario_summary = calculate_dcf(
                current_revenue,
                assumptions["growth"],
                assumptions["ebit_margin"],
                tax_rate,
                reinvestment_rate,
                assumptions["wacc"],
                assumptions["terminal_growth"],
                projection_years,
                debt,
                cash,
                shares_outstanding,
            )
            scenario_value = scenario_summary["Intrinsic Value Per Share"]
        scenario_rows.append(
            {
                "Scenario": scenario_name,
                "Revenue Growth": assumptions["growth"],
                "EBIT Margin": assumptions["ebit_margin"],
                "WACC": assumptions["wacc"],
                "Terminal Growth": assumptions["terminal_growth"],
                "Intrinsic Value / Share": scenario_value,
                "Margin of Safety": margin_of_safety(scenario_value, current_market_price),
            }
        )
    scenario_df = pd.DataFrame(scenario_rows)
    st.dataframe(
        scenario_df.style.format(
            {
                "Revenue Growth": "{:.1%}",
                "EBIT Margin": "{:.1%}",
                "WACC": "{:.1%}",
                "Terminal Growth": "{:.1%}",
                "Intrinsic Value / Share": "${:,.2f}",
                "Margin of Safety": "{:.1%}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    scenario_chart = go.Figure()
    scenario_chart.add_trace(
        go.Bar(
            x=scenario_df["Scenario"],
            y=scenario_df["Intrinsic Value / Share"],
            text=[currency(v) for v in scenario_df["Intrinsic Value / Share"]],
            textposition="outside",
            marker=dict(color=["#111111", "#F40009", "#B00000"]),
            textfont=dict(color="#111111"),
        )
    )
    scenario_chart.add_hline(y=current_market_price, line_dash="dash", line_color="#111111", annotation_text="Current Market Price", annotation_font_color="#111111")
    apply_clean_chart_layout(scenario_chart, "Scenario Intrinsic Value Compared to Current Market Price", "Scenario", "Intrinsic Value Per Share")
    st.plotly_chart(scenario_chart, use_container_width=True)


with tab_peers:
    st.header("Peer Comparisons")
    st.write(
        "This tab compares KO with similar beverage and consumer staples companies. "
        "The default numbers are illustrative placeholders, so update them with current market data before relying on the analysis."
    )

    peer_data = pd.DataFrame(
        {
            "Ticker": ["KO", "PEP", "KDP", "MNST", "CCEP", "NSRGY"],
            "Company": [
                "The Coca-Cola Company",
                "PepsiCo, Inc.",
                "Keurig Dr Pepper Inc.",
                "Monster Beverage Corp.",
                "Coca-Cola Europacific Partners",
                "Nestlé S.A. ADR",
            ],
            "Business Focus": [
                "Global beverages",
                "Beverages + snacks",
                "Coffee + soft drinks",
                "Energy drinks",
                "Coca-Cola bottler",
                "Global food + beverages",
            ],
            "Market Price": [current_market_price, 175.00, 34.00, 55.00, 75.00, 100.00],
            "P/E Multiple": [25.0, 22.0, 20.0, 32.0, 19.0, 21.0],
            "EV/EBITDA Multiple": [20.0, 15.0, 13.0, 24.0, 12.0, 14.0],
            "Revenue Growth": [annual_growth_rate, 0.04, 0.03, 0.08, 0.04, 0.03],
            "EBIT Margin": [ebit_margin, 0.16, 0.23, 0.28, 0.13, 0.17],
            "Dividend Yield": [0.028, 0.030, 0.025, 0.000, 0.025, 0.030],
        }
    )

    st.subheader("Comparable Company Table")
    st.dataframe(
        peer_data.style.format(
            {
                "Market Price": "${:,.2f}",
                "P/E Multiple": "{:.1f}x",
                "EV/EBITDA Multiple": "{:.1f}x",
                "Revenue Growth": "{:.1%}",
                "EBIT Margin": "{:.1%}",
                "Dividend Yield": "{:.1%}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    peer_col1, peer_col2 = st.columns(2)

    with peer_col1:
        pe_chart = go.Figure()
        pe_chart.add_trace(
            go.Bar(
                x=peer_data["Ticker"],
                y=peer_data["P/E Multiple"],
                text=[f"{x:.1f}x" for x in peer_data["P/E Multiple"]],
                textposition="outside",
                marker=dict(
                    color=["#F40009" if ticker_symbol == "KO" else "#111111" for ticker_symbol in peer_data["Ticker"]]
                ),
                textfont=dict(color="#111111"),
            )
        )
        apply_clean_chart_layout(pe_chart, "Peer P/E Multiple Comparison", "Ticker", "P/E Multiple")
        st.plotly_chart(pe_chart, use_container_width=True)

    with peer_col2:
        ev_chart = go.Figure()
        ev_chart.add_trace(
            go.Bar(
                x=peer_data["Ticker"],
                y=peer_data["EV/EBITDA Multiple"],
                text=[f"{x:.1f}x" for x in peer_data["EV/EBITDA Multiple"]],
                textposition="outside",
                marker=dict(
                    color=["#F40009" if ticker_symbol == "KO" else "#111111" for ticker_symbol in peer_data["Ticker"]]
                ),
                textfont=dict(color="#111111"),
            )
        )
        apply_clean_chart_layout(ev_chart, "Peer EV/EBITDA Multiple Comparison", "Ticker", "EV/EBITDA Multiple")
        st.plotly_chart(ev_chart, use_container_width=True)

    peer_col3, peer_col4 = st.columns(2)

    with peer_col3:
        margin_chart = go.Figure()
        margin_chart.add_trace(
            go.Bar(
                x=peer_data["Ticker"],
                y=peer_data["EBIT Margin"],
                text=[f"{x:.1%}" for x in peer_data["EBIT Margin"]],
                textposition="outside",
                marker=dict(
                    color=["#F40009" if ticker_symbol == "KO" else "#111111" for ticker_symbol in peer_data["Ticker"]]
                ),
                textfont=dict(color="#111111"),
            )
        )
        apply_clean_chart_layout(margin_chart, "Peer EBIT Margin Comparison", "Ticker", "EBIT Margin")
        st.plotly_chart(margin_chart, use_container_width=True)

    with peer_col4:
        growth_chart = go.Figure()
        growth_chart.add_trace(
            go.Scatter(
                x=peer_data["Revenue Growth"],
                y=peer_data["EBIT Margin"],
                mode="markers+text",
                text=peer_data["Ticker"],
                textposition="top center",
                marker=dict(
                    size=16,
                    color=["#F40009" if ticker_symbol == "KO" else "#111111" for ticker_symbol in peer_data["Ticker"]],
                    line=dict(color="#F40009", width=1),
                ),
                textfont=dict(color="#111111"),
            )
        )
        apply_clean_chart_layout(growth_chart, "Growth vs. EBIT Margin Peer Map", "Revenue Growth", "EBIT Margin")
        growth_chart.update_xaxes(tickformat=".0%")
        growth_chart.update_yaxes(tickformat=".0%")
        st.plotly_chart(growth_chart, use_container_width=True)

    st.subheader("Peer Valuation Takeaway")
    st.write(
        "Peer comparisons help investors judge whether KO's valuation assumptions look reasonable relative to similar companies. "
        "For example, if KO trades at a much higher P/E than peers, investors may need stronger growth, stronger margins, or lower risk to justify the premium. "
        "If KO has lower growth but a higher multiple, the valuation may depend more heavily on brand strength, stability, dividends, and defensive characteristics."
    )

    peer_csv = peer_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Peer Comparison Table as CSV",
        peer_csv,
        "ko_peer_comparison_table.csv",
        "text/csv",
    )


with tab_learning:
    st.header("Model Transparency: Formula Breakdown")
    st.markdown(
        """
        <div class="formula-box">
            <b>Step 1:</b> Revenue = Current Revenue × (1 + Growth Rate)<sup>Year</sup><br>
            <b>Step 2:</b> EBIT = Revenue × EBIT Margin<br>
            <b>Step 3:</b> NOPAT = EBIT × (1 - Tax Rate)<br>
            <b>Step 4:</b> Reinvestment = NOPAT × Reinvestment Rate<br>
            <b>Step 5:</b> Free Cash Flow = NOPAT - Reinvestment<br>
            <b>Step 6:</b> PV of FCF = Free Cash Flow ÷ (1 + WACC)<sup>Year</sup><br>
            <b>Step 7:</b> Terminal Value = Final Year FCF × (1 + Terminal Growth) ÷ (WACC - Terminal Growth)<br>
            <b>Step 8:</b> Enterprise Value = PV of Projected FCF + PV of Terminal Value<br>
            <b>Step 9:</b> Equity Value = Enterprise Value - Debt + Cash<br>
            <b>Step 10:</b> Intrinsic Value Per Share = Equity Value ÷ Shares Outstanding<br>
            <b>Step 11:</b> Margin of Safety = (Intrinsic Value - Market Price) ÷ Market Price
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write(
        "The model values the operating business first, then adjusts for debt and cash to estimate the value available to shareholders. "
        "Finally, it divides by shares outstanding to estimate value per share."
    )
    st.header("Final Notes")
    st.info(
        "This app uses manual inputs instead of yfinance, which makes it easier to run for class without package issues. "
        "In a real-world app, current price, revenue, debt, cash, and shares outstanding could be retrieved automatically from online data sources."
    )
    st.markdown(
        """
        **Coca-Cola branding touches included:**
        - Coke-red title and dashboard card
        - Red and black chart accents
        - Clean white chart backgrounds with black text
        - Coke bottle/cup style arrow annotations in charts
        - Coca-Cola themed color palette throughout the app
        """
    )
