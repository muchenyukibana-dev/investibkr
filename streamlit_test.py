import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Portfolio Position Rebalancer", page_icon="📈", layout="centered")

st.title("📈 Smart Portfolio Position Rebalancer")
st.markdown("Calculate multi-period funding plans to adjust your overall portfolio allocation with precision.")

# Mode selection
calc_mode = st.radio(
    "Select Calculation Mode", 
    [
        "Mode 1: Specify Periods ➔ Calculate Amount per Period", 
        "Mode 2: Specify Amount per Period ➔ Calculate Required Periods"
    ]
)

st.markdown("---")

# Basic Parameters
st.subheader("1. General Portfolio Settings")
col1, col2 = st.columns(2)
with col1:
    total_v0 = st.number_input("Total Portfolio Value ($)", value=100000.0, step=1000.0, format="%.2f")
with col2:
    target_rate = st.number_input("Target Stock Allocation (%)", value=60, step=1) / 100.0
st.markdown("---")

# Multi-stock holdings input (up to 30 stocks)
st.subheader("2. Stock Holdings Breakdown (Max 30 Stocks)")
st.markdown("Add, edit, or remove your individual stock holdings below. Remember to press **Enter** after typing a number so it saves successfully.")

# Initialize session state for stocks if not present
if "stocks_df" not in st.session_state:
    st.session_state.stocks_df = pd.DataFrame([
        {"Stock Name / Ticker": "AAPL", "Current Value ($)": 15000.0},
        {"Stock Name / Ticker": "MSFT", "Current Value ($)": 15000.0}
    ])

# Use st.data_editor with NumberColumn configuration to prevent validation errors
edited_df = st.data_editor(
    st.session_state.stocks_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Current Value ($)": st.column_config.NumberColumn(
            "Current Value ($)",
            min_value=0.0,
            step=100.0,
            format="$%.2f",
        )
    },
    key="stock_editor"
)

# Enforce max 30 stocks limit
if len(edited_df) > 30:
    st.warning("⚠️ You have exceeded the maximum limit of 30 stocks. The list has been trimmed to 30.")
    edited_df = edited_df.head(30)

st.session_state.stocks_df = edited_df

# Calculate total current stock value S0
stock_s0 = edited_df["Current Value ($)"].sum()
current_rate = stock_s0 / total_v0 if total_v0 > 0 else 0

col_m1, col_m2 = st.columns(2)
col_m1.metric("Total Current Stock Value", f"${stock_s0:,.2f}")
col_m2.metric("Current Stock Allocation", f"{current_rate * 100:.2f}%")

st.markdown("---")

if "Mode 1" in calc_mode:
    periods = st.number_input("Planned Investment Periods (Periods)", value=10, min_value=1, step=1)
else:
    amount_per_period = st.number_input("Planned Investment Amount per Period ($)", value=7500.0, step=500.0, format="%.2f")

# Calculation action
if st.button("Start Calculation", type="primary", use_container_width=True):
    if total_v0 <= 0:
        st.error("Total portfolio value must be greater than 0.")
    elif stock_s0 < 0:
        st.error("Stock values cannot be negative.")
    elif target_rate <= 0 or target_rate >= 1:
        st.error("Target allocation percentage must be between 0% and 100%.")
    elif stock_s0 > total_v0:
        st.error("Total stock value cannot exceed total portfolio value.")
    elif current_rate >= target_rate:
        st.warning(f"⚠️ Your current stock allocation ({current_rate*100:.2f}%) has already reached or exceeded the target allocation ({target_rate*100:.2f}%), no extra adjustment needed!")
    else:
        if "Mode 1" in calc_mode:
            total_need = (target_rate * total_v0 - stock_s0) / (1 - target_rate)
            amt = total_need / periods
            p = periods
        else:
            amt = amount_per_period
            if amt <= 0:
                st.error("Investment amount per period must be greater than 0.")
                st.stop()
            exact_periods = (target_rate * total_v0 - stock_s0) / (amt * (1 - target_rate))
            p = math.ceil(exact_periods)

        total_invest = amt * p
        final_v = total_v0 + total_invest
        final_s = stock_s0 + total_invest
        final_rate = (final_s / final_v) * 100

        st.success("✅ Calculation Successful!")
        
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Suggested Amount / Period", f"${amt:,.2f}")
        res_col2.metric("Total Periods", f"{p}")
        res_col3.metric("Final Allocation", f"{final_rate:.2f}%")

        st.info(f"• Total Additional Capital: **${total_invest:,.2f}**  \n• Final Total Portfolio Value: **${final_v:,.2f}** (Final Stock Value: ${final_s:,.2f})")

        # Period-by-period breakdown table
        st.subheader("📋 Period-by-Period Rebalancing Schedule")
        table_data = []
        curr_v = total_v0
        curr_s = stock_s0
        for i in range(1, p + 1):
            curr_v += amt
            curr_s += amt
            r = (curr_s / curr_v) * 100
            table_data.append({
                "Period": f"Period {i}",
                "Investment ($)": f"${amt:,.2f}",
                "End Stock Value ($)": f"${curr_s:,.2f}",
                "End Total Value ($)": f"${curr_v:,.2f}",
                "End Allocation (%)": f"{r:.2f}%"
            })
        
        st.table(table_data)
