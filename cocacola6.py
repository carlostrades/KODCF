"""
Coca Cola DCF Valuation / Flexible Stock DCF App
------------------------------------------------
Run with:
    streamlit run app.py

Install dependencies:
    pip install streamlit pandas numpy plotly openpyxl yfinance

Purpose:
    Value KO by default, but allow users to enter another stock ticker and pull available
    market/financial data from Yahoo Finance through yfinance. The WACC breakdown now
    directly feeds the valuation dashboard.
"""

from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


# =====================================================
# Page setup
# =====================================================
st.set_page_config(
    page_title="DCF Equity Valuation",
    page_icon="🥤",
    layout="wide",
)


# =====================================================
# Styling
# =====================================================
st.markdown(
    """
    <style>
        .stApp { background-color: #ffffff !important; color: #111111 !important; }
        .stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div,
        .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
        [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] span {
            color: #111111 !important;
        }
        [data-testid="stSidebar"] { background-color: #fff5f5 !important; }
        [data-testid="stSidebar"] * { color: #111111 !important; }
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea,
        [data-testid="stSidebar"] [data-baseweb="input"] input,
        [data-testid="stSidebar"] [data-baseweb="textarea"] textarea {
            color: #FFFFFF !important;
            background-color: #111111 !important;
            caret-color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] input::placeholder,
        [data-testid="stSidebar"] textarea::placeholder { color: #DDDDDD !important; }
        h1, h2, h3, h4, h5, h6 { color: #F40009 !important; }
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
        .coke-card h3, .coke-card p, .coke-card div, .coke-card span { color: white !important; }
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
        .formula-box, .formula-box * { color: #111111 !important; }
        [data-testid="stMetric"] {
            background-color: #ffffff !important;
            border: 1px solid #eeeeee;
            border-radius: 12px;
            padding: 10px;
        }
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { color: #F40009 !important; }
        [data-testid="stMetricValue"], [data-testid="stMetricValue"] * { color: #111111 !important; }
        [data-testid="stMetricDelta"], [data-testid="stMetricDelta"] * { color: #111111 !important; }
        [data-testid="stExpander"], [data-testid="stExpander"] details, [data-testid="stExpander"] summary {
            background-color: #FFFFFF !important;
            color: #111111 !important;
            border-color: #DDDDDD !important;
        }
        [data-testid="stExpander"] *, [data-testid="stExpander"] summary *,
        [data-testid="stExpander"] div, [data-testid="stExpander"] p,
        [data-testid="stExpander"] span { color: #111111 !important; }
        [data-testid="stDataFrame"] * { color: #111111 !important; }
        .stAlert, .stAlert * { color: #111111 !important; }
        button, [data-testid="stSidebar"] button, .stDownloadButton button {
            background-color: #FFFFFF !important;
            color: #111111 !important;
            border: 2px solid #111111 !important;
            border-radius: 10px !important;
            font-weight: 800 !important;
        }
        button *, [data-testid="stSidebar"] button *, .stDownloadButton button * {
            color: #111111 !important;
            font-weight: 800 !important;
        }
        button:hover, [data-testid="stSidebar"] button:hover, .stDownloadButton button:hover {
            background-color: #fff5f5 !important;
            color: #111111 !important;
            border: 2px solid #111111 !important;
        }
        button:hover *, [data-testid="stSidebar"] button:hover *, .stDownloadButton button:hover * {
            color: #111111 !important;
        }
        [data-baseweb="tab-list"] button, [data-testid="stTabs"] button, [role="tab"] {
            background-color: #FFFFFF !important;
            color: #111111 !important;
            border: 2px solid #111111 !important;
            border-radius: 10px !important;
            font-weight: 800 !important;
            margin-right: 8px !important;
        }
        [data-baseweb="tab-list"] button *, [data-testid="stTabs"] button *, [role="tab"] * {
            color: #111111 !important;
            font-weight: 800 !important;
        }
        [data-baseweb="tab-list"] button:hover, [data-testid="stTabs"] button:hover, [role="tab"]:hover {
            background-color: #fff5f5 !important;
            color: #111111 !important;
            border: 2px solid #111111 !important;
        }
        [data-baseweb="tab-highlight"] { background-color: #111111 !important; }

        /* Dropdown and expander styling */
        [data-testid="stExpander"],
        [data-testid="stExpander"] details,
        [data-testid="stExpander"] summary {
            background-color: #FFFFFF !important;
            color: #111111 !important;
            border: 2px solid #111111 !important;
            border-radius: 8px !important;
        }
        [data-testid="stExpander"] *,
        [data-testid="stExpander"] summary *,
        [data-testid="stExpander"] div,
        [data-testid="stExpander"] p,
        [data-testid="stExpander"] span {
            color: #111111 !important;
        }

        /* Select/dropdown widgets */
        [data-baseweb="select"],
        [data-baseweb="select"] *,
        [data-baseweb="popover"],
        [data-baseweb="popover"] * {
            background-color: #FFFFFF !important;
            color: #111111 !important;
            border-color: #111111 !important;
        }
    </style>
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


def safe_number(value, fallback):
    try:
        if value is None or pd.isna(value) or value == 0:
            return fallback
        return float(value)
    except Exception:
        return fallback


@st.cache_data(ttl=900)
def get_yahoo_data(ticker):
    """Pull available market and financial data from Yahoo Finance through yfinance."""
    stock = yf.Ticker(ticker)

    try:
        info = stock.info or {}
    except Exception:
        info = {}

    try:
        fast = dict(stock.fast_info) if stock.fast_info else {}
    except Exception:
        fast = {}

    try:
        financials = stock.financials
    except Exception:
        financials = pd.DataFrame()

    try:
        balance_sheet = stock.balance_sheet
    except Exception:
        balance_sheet = pd.DataFrame()

    try:
        hist = stock.history(period="1y")
    except Exception:
        hist = pd.DataFrame()

    price = (
        fast.get("last_price")
        or info.get("currentPrice")
        or info.get("regularMarketPrice")
        or (hist["Close"].dropna().iloc[-1] if not hist.empty else np.nan)
    )

    company_name = info.get("longName") or info.get("shortName") or ticker.upper()
    market_cap = fast.get("market_cap") or info.get("marketCap")
    shares = info.get("sharesOutstanding")

    if not shares and market_cap and price:
        shares = market_cap / price

    revenue = info.get("totalRevenue")
    ebitda = info.get("ebitda")
    total_debt = info.get("totalDebt")
    total_cash = info.get("totalCash")

    # Financial statement fallbacks
    if (not revenue or pd.isna(revenue)) and not financials.empty:
        for row_name in ["Total Revenue", "Operating Revenue"]:
            if row_name in financials.index:
                revenue = financials.loc[row_name].dropna().iloc[0]
                break

    ebit = None
    if not financials.empty:
        for row_name in ["EBIT", "Operating Income"]:
            if row_name in financials.index:
                ebit = financials.loc[row_name].dropna().iloc[0]
                break

    if (not total_debt or pd.isna(total_debt)) and not balance_sheet.empty:
        debt_candidates = ["Total Debt", "Long Term Debt", "Long Term Debt And Capital Lease Obligation"]
        for row_name in debt_candidates:
            if row_name in balance_sheet.index:
                total_debt = balance_sheet.loc[row_name].dropna().iloc[0]
                break

    if (not total_cash or pd.isna(total_cash)) and not balance_sheet.empty:
        cash_candidates = ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]
        for row_name in cash_candidates:
            if row_name in balance_sheet.index:
                total_cash = balance_sheet.loc[row_name].dropna().iloc[0]
                break

    ebit_margin = None
    if ebit and revenue:
        ebit_margin = ebit / revenue

    # Build a revenue history table when Yahoo Finance provides annual financials.
    revenue_history = pd.DataFrame()
    if not financials.empty:
        revenue_row = None
        for row_name in ["Total Revenue", "Operating Revenue"]:
            if row_name in financials.index:
                revenue_row = financials.loc[row_name].dropna()
                break

        if revenue_row is not None and not revenue_row.empty:
            revenue_history = pd.DataFrame(
                {
                    "Fiscal Year": [str(idx.year) if hasattr(idx, "year") else str(idx) for idx in revenue_row.index],
                    "Revenue": revenue_row.values,
                }
            )
            revenue_history = revenue_history.sort_values("Fiscal Year")
            revenue_history["Revenue Growth"] = revenue_history["Revenue"].pct_change()

    return {
        "ticker": ticker.upper(),
        "company_name": company_name,
        "current_price": safe_number(price, 75.44),
        "market_cap": safe_number(market_cap, 325_000_000_000.0),
        "shares_outstanding": safe_number(shares, 4_310_000_000.0),
        "revenue": safe_number(revenue, 47_000_000_000.0),
        "ebit_margin": safe_number(ebit_margin, 0.28),
        "debt": safe_number(total_debt, 45_000_000_000.0),
        "cash": safe_number(total_cash, 20_000_000_000.0),
        "beta": safe_number(info.get("beta"), 0.60),
        "trailing_pe": safe_number(info.get("trailingPE"), np.nan),
        "forward_pe": safe_number(info.get("forwardPE"), np.nan),
        "ev_to_ebitda": safe_number(info.get("enterpriseToEbitda"), np.nan),
        "dividend_yield": safe_number(info.get("dividendYield"), np.nan),
        "hist": hist,
        "revenue_history": revenue_history,
    }


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
        xaxis=dict(title=dict(font=dict(color="#111111")), tickfont=dict(color="#111111"), color="#111111", gridcolor="#E6E6E6"),
        yaxis=dict(title=dict(font=dict(color="#111111")), tickfont=dict(color="#111111"), color="#111111", gridcolor="#E6E6E6"),
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
            marker=dict(color=["#111111", "#F40009", "#B00000", "#F40009"]),
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
            increasing={"marker": {"color": "#F40009"}},
            decreasing={"marker": {"color": "#111111"}},
            totals={"marker": {"color": "#B00000"}},
        )
    )
    apply_clean_chart_layout(fig, "Enterprise Value to Equity Value Bridge", "Valuation Step", "Value")
    return fig


# =====================================================
# Reset button defaults
# =====================================================
DEFAULT_SESSION_INPUTS = {
    "ticker_symbol_input": "KO",
    "annual_growth_rate_pct": 4.0,
    "tax_rate_pct": 21.0,
    "reinvestment_rate_pct": 20.0,
    "terminal_growth_pct": 2.5,
    "projection_years_input": 10,
    "risk_free_rate_pct": 4.25,
    "equity_risk_premium_pct": 5.50,
    "beta_input": 0.60,
    "equity_weight_pct": 80.0,
    "pre_tax_cost_of_debt_pct": 4.50,
}

for default_key, default_value in DEFAULT_SESSION_INPUTS.items():
    st.session_state.setdefault(default_key, default_value)


def reset_all_inputs():
    """Reset ticker, forecast assumptions, and WACC assumptions back to default values."""
    for reset_key, reset_value in DEFAULT_SESSION_INPUTS.items():
        st.session_state[reset_key] = reset_value


reset_col, spacer_col = st.columns([1, 5])
with reset_col:
    st.button("Reset Inputs", on_click=reset_all_inputs, help="Reset ticker and assumptions back to default values.")


# =====================================================
# Header
# =====================================================
st.markdown('<div class="main-title">DCF Equity Valuation</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">A flexible DCF model for any ticker supported by Yahoo Finance.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="coke-card">
        <h3>Valuation Goal</h3>
        <p>
        Enter a ticker, pull available Yahoo Finance data, adjust the valuation assumptions, and estimate intrinsic value using a DCF model.
        The WACC breakdown now directly changes the valuation dashboard.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# Sidebar inputs and Yahoo Finance data
# =====================================================
st.sidebar.header("Valuation Inputs")
st.sidebar.caption("Enter a ticker, then adjust the assumptions.")

ticker = st.sidebar.text_input(
    "Ticker Symbol",
    key="ticker_symbol_input",
    help="Try KO, PEP, AAPL, MSFT, etc.",
).upper().strip()

if not ticker:
    st.stop()

try:
    yahoo = get_yahoo_data(ticker)
except Exception as error:
    st.error("Could not load Yahoo Finance data. Check the ticker or internet connection.")
    st.exception(error)
    st.stop()

company_name = yahoo["company_name"]

st.sidebar.subheader("Yahoo Finance Data")
st.sidebar.caption(f"Loaded: {company_name}")
st.sidebar.caption("These values are pulled from Yahoo Finance and are shown for transparency. They are not editable in this version.")

current_market_price = float(yahoo["current_price"])
current_revenue = float(yahoo["revenue"])
ebit_margin = float(np.clip(yahoo["ebit_margin"], 0, 0.60))
debt = float(yahoo["debt"])
cash = float(yahoo["cash"])
shares_outstanding = float(yahoo["shares_outstanding"])

st.sidebar.metric("Current Market Price", currency(current_market_price))
st.sidebar.metric("Current Revenue", large_currency(current_revenue))
st.sidebar.metric("EBIT Margin", percent(ebit_margin))
st.sidebar.metric("Debt", large_currency(debt))
st.sidebar.metric("Cash", large_currency(cash))
st.sidebar.metric("Shares Outstanding", f"{shares_outstanding:,.0f}")

st.sidebar.subheader("Forecast Assumptions")
annual_growth_rate = st.sidebar.slider(
    "Annual Growth Rate (%)",
    -10.0,
    25.0,
    key="annual_growth_rate_pct",
    step=0.25,
) / 100
tax_rate = st.sidebar.slider(
    "Tax Rate (%)",
    0.0,
    45.0,
    key="tax_rate_pct",
    step=0.25,
) / 100
reinvestment_rate = st.sidebar.slider(
    "Reinvestment Rate (%)",
    0.0,
    90.0,
    key="reinvestment_rate_pct",
    step=0.5,
) / 100
terminal_growth_rate = st.sidebar.slider(
    "Terminal Growth (%)",
    0.0,
    6.0,
    key="terminal_growth_pct",
    step=0.25,
) / 100
projection_years = st.sidebar.slider(
    "Projection Years",
    3,
    15,
    key="projection_years_input",
    step=1,
)

st.sidebar.subheader("WACC Inputs")
st.sidebar.caption("Adjust WACC in the DCF + FCFF + WACC tab. Changes there update this dashboard.")

# WACC inputs are stored in session_state so the dashboard updates when the user changes
# the WACC controls inside the DCF + FCFF + WACC tab.
# Defaults are initialized near the top of the app. Beta can still be manually adjusted in the WACC tab.

risk_free_rate = st.session_state["risk_free_rate_pct"] / 100
equity_risk_premium = st.session_state["equity_risk_premium_pct"] / 100
beta = st.session_state["beta_input"]
equity_weight = st.session_state["equity_weight_pct"] / 100
debt_weight = 1 - equity_weight
pre_tax_cost_of_debt = st.session_state["pre_tax_cost_of_debt_pct"] / 100
market_value_equity = current_market_price * shares_outstanding
market_value_debt = debt
cost_of_equity = risk_free_rate + beta * equity_risk_premium
after_tax_cost_of_debt = pre_tax_cost_of_debt * (1 - tax_rate)
wacc = (equity_weight * cost_of_equity) + (debt_weight * after_tax_cost_of_debt)

st.sidebar.metric("Calculated WACC", percent(wacc))
st.sidebar.metric("Cost of Equity", percent(cost_of_equity))
st.sidebar.metric("Debt Weight", percent(debt_weight))

if st.sidebar.button("Refresh Yahoo Data"):
    st.cache_data.clear()
    st.rerun()


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
implied_equity_value = intrinsic_value * shares_outstanding
market_cap = current_market_price * shares_outstanding

if mos >= 0.15:
    verdict = "Potentially Undervalued"
elif mos <= -0.15:
    verdict = "Potentially Overvalued"
else:
    verdict = "Near Fair Value"


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
st.write("This dashboard updates whenever you change the ticker, operating assumptions, or WACC inputs.")

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
    st.header("Yahoo Finance Integration")
    st.write(
        "The app now uses the ticker symbol to pull available price, company name, revenue, cash, debt, shares outstanding, beta, and selected multiples from Yahoo Finance. "
        "You can still override the values in the sidebar."
    )
    data_snapshot = pd.DataFrame(
        {
            "Yahoo Finance Item": [
                "Company Name", "Current Price", "Market Cap", "Revenue", "Debt", "Cash", "Shares Outstanding", "Beta", "Trailing P/E", "Forward P/E", "EV/EBITDA", "Dividend Yield"
            ],
            "Value": [
                company_name,
                currency(yahoo["current_price"]),
                large_currency(yahoo["market_cap"]),
                large_currency(yahoo["revenue"]),
                large_currency(yahoo["debt"]),
                large_currency(yahoo["cash"]),
                f"{yahoo['shares_outstanding']:,.0f}",
                f"{yahoo['beta']:.2f}",
                "N/A" if pd.isna(yahoo["trailing_pe"]) else f"{yahoo['trailing_pe']:.1f}x",
                "N/A" if pd.isna(yahoo["forward_pe"]) else f"{yahoo['forward_pe']:.1f}x",
                "N/A" if pd.isna(yahoo["ev_to_ebitda"]) else f"{yahoo['ev_to_ebitda']:.1f}x",
                "N/A" if pd.isna(yahoo["dividend_yield"]) else percent(yahoo["dividend_yield"]),
            ],
        }
    )
    st.dataframe(data_snapshot, use_container_width=True, hide_index=True)

    st.header("Input Guide")
    with st.expander("Ticker Symbol", expanded=True):
        st.write("Changing the ticker in the sidebar reloads Yahoo Finance data and updates the valuation dashboard for that stock.")
    with st.expander("WACC Inputs"):
        st.write("Risk-free rate, beta, equity risk premium, cost of debt, tax rate, equity value, and debt value now calculate WACC. That WACC is used directly in the DCF model.")
    with st.expander("Operating Inputs"):
        st.write("Revenue, growth, EBIT margin, tax rate, reinvestment rate, and terminal growth drive the projected FCFF and intrinsic value.")

with tab_dcf:
    st.header("Growth Rate Explanation and History")
    st.write(
        "The annual growth rate is one of the most important DCF assumptions because it controls how quickly revenue grows during the forecast period. "
        "A higher growth rate increases projected revenue, EBIT, NOPAT, free cash flow, and ultimately intrinsic value. "
        "A lower growth rate makes the valuation more conservative."
    )

    revenue_history = yahoo.get("revenue_history", pd.DataFrame())
    if revenue_history is not None and not revenue_history.empty:
        st.subheader(f"Historical Revenue Growth for {ticker}")
        st.dataframe(
            revenue_history.style.format(
                {
                    "Revenue": "${:,.0f}",
                    "Revenue Growth": "{:.1%}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        valid_revenue = revenue_history.dropna(subset=["Revenue"])
        if len(valid_revenue) >= 2:
            first_revenue = valid_revenue["Revenue"].iloc[0]
            last_revenue = valid_revenue["Revenue"].iloc[-1]
            periods = len(valid_revenue) - 1
            historical_cagr = (last_revenue / first_revenue) ** (1 / periods) - 1 if first_revenue > 0 else np.nan
            average_growth = valid_revenue["Revenue Growth"].mean()

            growth_col1, growth_col2, growth_col3 = st.columns(3)
            growth_col1.metric("Historical Revenue CAGR", percent(historical_cagr))
            growth_col2.metric("Average Annual Revenue Growth", percent(average_growth))
            growth_col3.metric("Growth Used in DCF", percent(annual_growth_rate))

            fig_growth = go.Figure()
            fig_growth.add_trace(
                go.Bar(
                    x=valid_revenue["Fiscal Year"],
                    y=valid_revenue["Revenue Growth"],
                    text=["N/A" if pd.isna(x) else f"{x:.1%}" for x in valid_revenue["Revenue Growth"]],
                    textposition="outside",
                    marker=dict(color="#F40009"),
                    textfont=dict(color="#111111"),
                )
            )
            apply_clean_chart_layout(fig_growth, f"{ticker} Historical Revenue Growth", "Fiscal Year", "Revenue Growth")
            fig_growth.update_yaxes(tickformat=".0%")
            st.plotly_chart(fig_growth, use_container_width=True)

            st.markdown(
                f"""
                <div class="formula-box">
                    <b>How to use this:</b><br>
                    Historical revenue CAGR is a useful starting point, but it should not be copied blindly into the DCF. 
                    If the company is mature, the forecast growth rate should usually be close to or below its long-term historical growth. 
                    If the company is cyclical or recently changed strategy, use judgment and compare the historical CAGR to analyst expectations, industry growth, and company guidance.<br><br>
                    <b>CAGR Formula:</b> (Ending Revenue ÷ Beginning Revenue)<sup>1 / Number of Years</sup> - 1
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.warning(
            "Yahoo Finance did not provide enough annual revenue history for this ticker. "
            "You can still value the stock by entering your own revenue and growth assumptions in the sidebar."
        )

    st.header("DCF Formula Reference")
    st.markdown(
        """
        <div class="formula-box">
            <b>1. Revenue Projection:</b> Revenue<sub>t</sub> = Current Revenue × (1 + Growth Rate)<sup>t</sup><br>
            <b>2. EBIT:</b> EBIT<sub>t</sub> = Revenue<sub>t</sub> × EBIT Margin<br>
            <b>3. NOPAT:</b> NOPAT<sub>t</sub> = EBIT<sub>t</sub> × (1 - Tax Rate)<br>
            <b>4. Reinvestment:</b> Reinvestment<sub>t</sub> = NOPAT<sub>t</sub> × Reinvestment Rate<br>
            <b>5. Free Cash Flow to the Firm:</b> FCFF<sub>t</sub> = NOPAT<sub>t</sub> - Reinvestment<sub>t</sub><br>
            <b>6. Discount Factor:</b> Discount Factor<sub>t</sub> = 1 ÷ (1 + WACC)<sup>t</sup><br>
            <b>7. Present Value of FCFF:</b> PV of FCFF<sub>t</sub> = FCFF<sub>t</sub> × Discount Factor<sub>t</sub><br>
            <b>8. Terminal Value:</b> Terminal Value = Final Year FCFF × (1 + Terminal Growth) ÷ (WACC - Terminal Growth)<br>
            <b>9. Present Value of Terminal Value:</b> PV of Terminal Value = Terminal Value ÷ (1 + WACC)<sup>Projection Years</sup><br>
            <b>10. Enterprise Value:</b> Enterprise Value = Sum of PV of FCFF + PV of Terminal Value<br>
            <b>11. Equity Value:</b> Equity Value = Enterprise Value - Debt + Cash<br>
            <b>12. Intrinsic Value Per Share:</b> Intrinsic Value Per Share = Equity Value ÷ Shares Outstanding<br>
            <b>13. Margin of Safety:</b> Margin of Safety = (Intrinsic Value Per Share - Current Market Price) ÷ Current Market Price
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.header("DCF Model Summary")
    summary_df = pd.DataFrame(
        {
            "Metric": [
                "PV of Projected FCF", "Final Year FCF", "Terminal Value", "PV of Terminal Value", "Enterprise Value", "Less: Debt", "Add: Cash", "Equity Value", "Shares Outstanding", "Intrinsic Value Per Share", "Current Market Price", "Margin of Safety"
            ],
            "Value": [
                large_currency(dcf_summary["Present Value of Projected FCF"]), large_currency(dcf_summary["Final Year FCF"]), large_currency(dcf_summary["Terminal Value"]), large_currency(dcf_summary["Present Value of Terminal Value"]), large_currency(dcf_summary["Enterprise Value"]), large_currency(debt), large_currency(cash), large_currency(dcf_summary["Equity Value"]), f"{shares_outstanding:,.0f}", currency(intrinsic_value), currency(current_market_price), percent(mos)
            ],
        }
    )
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    st.plotly_chart(create_ev_bridge_chart(dcf_summary), use_container_width=True)

    st.header("Step 4: Cost of Capital and WACC Inputs")
    st.write(
        "Use these inputs to estimate the discount rate for the selected stock. These WACC controls directly update the valuation dashboard. "
        "CAPM estimates the cost of equity, and the capital structure inputs combine equity and debt costs into WACC."
    )

    capm_left, capm_right = st.columns(2)

    with capm_left:
        st.subheader("CAPM")
        risk_free_rate_pct = st.slider(
            "Risk-Free Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=st.session_state["risk_free_rate_pct"],
            step=0.25,
            key="risk_free_rate_pct",
            help="Often estimated using a U.S. Treasury yield. This is the baseline return investors can earn with relatively low risk.",
        )
        equity_risk_premium_pct = st.slider(
            "Equity Risk Premium (%)",
            min_value=0.0,
            max_value=12.0,
            value=st.session_state["equity_risk_premium_pct"],
            step=0.25,
            key="equity_risk_premium_pct",
            help="The extra return investors expect from stocks compared to a risk-free investment.",
        )
        beta_input = st.number_input(
            "Beta",
            min_value=0.0,
            max_value=3.0,
            value=st.session_state["beta_input"],
            step=0.05,
            key="beta_input",
            help="Pulled from Yahoo Finance when available. Beta measures stock risk relative to the market.",
        )

    with capm_right:
        st.subheader("Capital Structure")
        equity_weight_pct = st.slider(
            "Equity Weight (%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state["equity_weight_pct"],
            step=1.0,
            key="equity_weight_pct",
            help="The percentage of the company's capital structure financed with equity. Debt weight is automatically 100% minus equity weight.",
        )
        debt_weight_pct_display = 100 - equity_weight_pct
        st.metric("Debt Weight", f"{debt_weight_pct_display:.1f}%")
        pre_tax_cost_of_debt_pct = st.slider(
            "Pre-Tax Cost of Debt (%)",
            min_value=0.0,
            max_value=20.0,
            value=st.session_state["pre_tax_cost_of_debt_pct"],
            step=0.25,
            key="pre_tax_cost_of_debt_pct",
            help="The interest rate the company pays on debt before the tax shield.",
        )
        st.metric("Effective Tax Rate", percent(tax_rate))

    # Recalculate locally inside the tab so the displayed formulas match the current widget values.
    tab_risk_free_rate = risk_free_rate_pct / 100
    tab_equity_risk_premium = equity_risk_premium_pct / 100
    tab_beta = beta_input
    tab_equity_weight = equity_weight_pct / 100
    tab_debt_weight = 1 - tab_equity_weight
    tab_pre_tax_cost_of_debt = pre_tax_cost_of_debt_pct / 100
    tab_cost_of_equity = tab_risk_free_rate + tab_beta * tab_equity_risk_premium
    tab_after_tax_cost_of_debt = tab_pre_tax_cost_of_debt * (1 - tax_rate)
    tab_wacc = (tab_equity_weight * tab_cost_of_equity) + (tab_debt_weight * tab_after_tax_cost_of_debt)

    capm_cols = st.columns(4)
    capm_cols[0].metric("Cost of Equity", percent(tab_cost_of_equity))
    capm_cols[1].metric("After-Tax Cost of Debt", percent(tab_after_tax_cost_of_debt))
    capm_cols[2].metric("Debt Weight", percent(tab_debt_weight))
    capm_cols[3].metric("WACC", percent(tab_wacc))

    st.markdown(
        """
        <div class="formula-box">
            <b>CAPM Formula:</b> Cost of Equity = Risk-Free Rate + Beta × Equity Risk Premium<br><br>
            <b>Risk-Free Rate:</b> The return investors could earn on a low-risk investment, commonly approximated with a U.S. Treasury yield.<br>
            <b>Beta:</b> A measure of how volatile the stock is compared to the overall market. A beta above 1.0 means the stock is usually more volatile than the market. A beta below 1.0 means it is usually less volatile.<br>
            <b>Equity Risk Premium:</b> The extra return investors expect for investing in stocks instead of a risk-free asset.<br>
            <b>Cost of Equity:</b> The required return for shareholders. A higher cost of equity raises WACC and usually lowers the DCF value.
        </div>
        """,
        unsafe_allow_html=True,
    )

    capm_table = pd.DataFrame(
        {
            "CAPM Component": [
                "Risk-Free Rate",
                "Beta",
                "Equity Risk Premium",
                "Cost of Equity",
            ],
            "What It Means": [
                "Baseline return from a low-risk investment, often estimated with Treasury yields.",
                "Measures the stock's risk relative to the overall market.",
                "Extra return investors require for taking stock market risk.",
                "Required return for equity investors, calculated using CAPM.",
            ],
            "Formula / Source": [
                "User input in sidebar",
                "Pulled from Yahoo Finance when available, but can be changed in sidebar",
                "User input in sidebar",
                "Risk-Free Rate + Beta × Equity Risk Premium",
            ],
            "Current Value": [
                percent(risk_free_rate),
                f"{beta:.2f}",
                percent(equity_risk_premium),
                percent(cost_of_equity),
            ],
        }
    )
    st.dataframe(capm_table, use_container_width=True, hide_index=True)

    st.header("WACC Breakdown with Formulas")
    wacc_cols = st.columns(4)
    wacc_cols[0].metric("Cost of Equity", percent(cost_of_equity))
    wacc_cols[1].metric("After-Tax Cost of Debt", percent(after_tax_cost_of_debt))
    wacc_cols[2].metric("Equity Weight", percent(equity_weight))
    wacc_cols[3].metric("Calculated WACC", percent(wacc))
    st.markdown(
        """
        <div class="formula-box">
            <b>Cost of Equity:</b> Risk-Free Rate + Beta × Equity Risk Premium<br>
            <b>After-Tax Cost of Debt:</b> Pre-Tax Cost of Debt × (1 - Tax Rate)<br>
            <b>Equity Weight:</b> Market Value of Equity ÷ (Market Value of Equity + Market Value of Debt)<br>
            <b>Debt Weight:</b> Market Value of Debt ÷ (Market Value of Equity + Market Value of Debt)<br>
            <b>WACC:</b> Equity Weight × Cost of Equity + Debt Weight × After-Tax Cost of Debt
        </div>
        """,
        unsafe_allow_html=True,
    )
    wacc_table = pd.DataFrame(
        {
            "WACC Component": ["Risk-Free Rate", "Beta", "Equity Risk Premium", "Cost of Equity", "Pre-Tax Cost of Debt", "Tax Rate", "After-Tax Cost of Debt", "Equity Weight", "Debt Weight", "Calculated WACC"],
            "Value": [percent(risk_free_rate), f"{beta:.2f}", percent(equity_risk_premium), percent(cost_of_equity), percent(pre_tax_cost_of_debt), percent(tax_rate), percent(after_tax_cost_of_debt), percent(equity_weight), percent(debt_weight), percent(wacc)],
        }
    )
    st.dataframe(wacc_table, use_container_width=True, hide_index=True)

    st.header("Simple FCFF Intrinsic Value Estimate")
    current_ebit = current_revenue * ebit_margin
    current_nopat = current_ebit * (1 - tax_rate)
    current_reinvestment = current_nopat * reinvestment_rate
    current_fcff = current_nopat - current_reinvestment
    next_year_fcff = current_fcff * (1 + annual_growth_rate)
    simple_enterprise_value = next_year_fcff * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    simple_equity_value = simple_enterprise_value - debt + cash
    simple_fcff_value_per_share = simple_equity_value / shares_outstanding
    simple_cols = st.columns(4)
    simple_cols[0].metric("Current FCFF", large_currency(current_fcff))
    simple_cols[1].metric("Next Year FCFF", large_currency(next_year_fcff))
    simple_cols[2].metric("FCFF Value / Share", currency(simple_fcff_value_per_share))
    simple_cols[3].metric("FCFF Margin of Safety", percent(margin_of_safety(simple_fcff_value_per_share, current_market_price)))

with tab_excel:
    st.header("Excel Replication Table")
    excel_inputs = pd.DataFrame(
        {
            "Input Assumption": ["Ticker", "Company Name", "Current Price", "Revenue", "Growth", "EBIT Margin", "Tax Rate", "Reinvestment Rate", "WACC", "Terminal Growth", "Projection Years", "Debt", "Cash", "Shares"],
            "Value": [ticker, company_name, current_market_price, current_revenue, annual_growth_rate, ebit_margin, tax_rate, reinvestment_rate, wacc, terminal_growth_rate, projection_years, debt, cash, shares_outstanding],
        }
    )
    excel_forecast = dcf_table[["Year", "Revenue", "EBIT", "NOPAT", "Reinvestment", "Free Cash Flow", "Discount Factor", "PV of FCF"]].copy()
    excel_summary = pd.DataFrame(
        {
            "Valuation Summary": ["PV of Projected FCF", "Terminal Value", "PV of Terminal Value", "Enterprise Value", "Debt", "Cash", "Equity Value", "Intrinsic Value Per Share", "Current Price", "Margin of Safety"],
            "Value": [dcf_summary["Present Value of Projected FCF"], dcf_summary["Terminal Value"], dcf_summary["Present Value of Terminal Value"], dcf_summary["Enterprise Value"], debt, cash, dcf_summary["Equity Value"], intrinsic_value, current_market_price, mos],
        }
    )
    formulas = pd.DataFrame(
        {
            "Line Item": ["Revenue", "EBIT", "NOPAT", "Reinvestment", "FCFF", "Terminal Value", "Enterprise Value", "Equity Value", "Intrinsic Value Per Share", "WACC"],
            "Formula": ["Prior Revenue × (1 + Growth)", "Revenue × EBIT Margin", "EBIT × (1 - Tax Rate)", "NOPAT × Reinvestment Rate", "NOPAT - Reinvestment", "Final Year FCF × (1 + g) ÷ (WACC - g)", "PV of FCF + PV of Terminal Value", "Enterprise Value - Debt + Cash", "Equity Value ÷ Shares", "E/(D+E) × Re + D/(D+E) × Rd × (1-T)"],
        }
    )
    st.subheader("DCF Forecast")
    st.dataframe(excel_forecast.style.format({"Revenue": "${:,.0f}", "EBIT": "${:,.0f}", "NOPAT": "${:,.0f}", "Reinvestment": "${:,.0f}", "Free Cash Flow": "${:,.0f}", "Discount Factor": "{:.4f}", "PV of FCF": "${:,.0f}"}), use_container_width=True, hide_index=True)
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
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        excel_inputs.to_excel(writer, sheet_name="Inputs", index=False)
        excel_forecast.to_excel(writer, sheet_name="DCF Forecast", index=False)
        excel_summary.to_excel(writer, sheet_name="Valuation Summary", index=False)
        wacc_table.to_excel(writer, sheet_name="WACC", index=False)
        formulas.to_excel(writer, sheet_name="Formulas", index=False)
    output.seek(0)
    st.download_button("Download Excel Workbook", output, f"{ticker}_dcf_valuation_workbook.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with tab_analysis:
    st.header("Sensitivity Analysis")
    wacc_range = np.arange(max(0.03, wacc - 0.02), wacc + 0.025, 0.005)
    terminal_growth_range = np.arange(max(0.00, terminal_growth_rate - 0.01), terminal_growth_rate + 0.0125, 0.0025)
    sensitivity_table = pd.DataFrame(index=[f"{tg:.2%}" for tg in terminal_growth_range])
    for w in wacc_range:
        values = []
        for tg in terminal_growth_range:
            if w <= tg:
                values.append(np.nan)
            else:
                _, sensitivity_summary = calculate_dcf(current_revenue, annual_growth_rate, ebit_margin, tax_rate, reinvestment_rate, w, tg, projection_years, debt, cash, shares_outstanding)
                values.append(sensitivity_summary["Intrinsic Value Per Share"])
        sensitivity_table[f"{w:.2%}"] = values
    st.dataframe(sensitivity_table.style.format("${:,.2f}"), use_container_width=True)

    heatmap = go.Figure(data=go.Heatmap(z=sensitivity_table.values, x=sensitivity_table.columns, y=sensitivity_table.index, colorscale=[[0, "#FFF2F2"], [0.5, "#F47C7C"], [1, "#F40009"]]))
    apply_clean_chart_layout(heatmap, "Intrinsic Value Sensitivity: WACC vs. Terminal Growth", "WACC", "Terminal Growth", 470)
    st.plotly_chart(heatmap, use_container_width=True)

with tab_peers:
    st.header("Peer Comparisons")
    peer_defaults = ["KO", "PEP", "KDP", "MNST", "CCEP", "NSRGY"]
    peer_rows = []
    for peer in peer_defaults:
        try:
            p = get_yahoo_data(peer)
            peer_rows.append(
                {
                    "Ticker": peer,
                    "Company": p["company_name"],
                    "Market Price": p["current_price"],
                    "Market Cap": p["market_cap"],
                    "Trailing P/E": p["trailing_pe"],
                    "Forward P/E": p["forward_pe"],
                    "EV/EBITDA": p["ev_to_ebitda"],
                    "Dividend Yield": p["dividend_yield"],
                }
            )
        except Exception:
            pass
    peer_data = pd.DataFrame(peer_rows)
    st.dataframe(peer_data.style.format({"Market Price": "${:,.2f}", "Market Cap": "${:,.0f}", "Trailing P/E": "{:.1f}x", "Forward P/E": "{:.1f}x", "EV/EBITDA": "{:.1f}x", "Dividend Yield": "{:.1%}"}), use_container_width=True, hide_index=True)
    if not peer_data.empty:
        pe_chart = go.Figure()
        pe_chart.add_trace(go.Bar(x=peer_data["Ticker"], y=peer_data["Forward P/E"], text=["N/A" if pd.isna(x) else f"{x:.1f}x" for x in peer_data["Forward P/E"]], textposition="outside", marker=dict(color=["#F40009" if x == ticker else "#111111" for x in peer_data["Ticker"]])))
        apply_clean_chart_layout(pe_chart, "Peer Forward P/E Multiple Comparison", "Ticker", "Forward P/E")
        st.plotly_chart(pe_chart, use_container_width=True)

with tab_learning:
    st.header("Formula Breakdown")
    st.markdown(
        """
        <div class="formula-box">
            <b>Revenue:</b> Current Revenue × (1 + Growth Rate)<sup>Year</sup><br>
            <b>EBIT:</b> Revenue × EBIT Margin<br>
            <b>NOPAT:</b> EBIT × (1 - Tax Rate)<br>
            <b>FCFF:</b> NOPAT - Reinvestment<br>
            <b>Terminal Value:</b> Final Year FCF × (1 + Terminal Growth) ÷ (WACC - Terminal Growth)<br>
            <b>Enterprise Value:</b> PV of Projected FCF + PV of Terminal Value<br>
            <b>Equity Value:</b> Enterprise Value - Debt + Cash<br>
            <b>Intrinsic Value Per Share:</b> Equity Value ÷ Shares Outstanding<br>
            <b>WACC:</b> Equity Weight × Cost of Equity + Debt Weight × After-Tax Cost of Debt
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "Because Yahoo Finance data availability varies by ticker, you can override the pulled data in the sidebar before relying on the valuation. "
        "Some tickers may have limited financial statement data, but the app will still run using fallback values that you can edit."
    )
