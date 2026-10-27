import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Multi-Asset Portfolio Rebalancer", page_icon="📈", layout="wide")

st.title("📈 Multi-Asset Portfolio Rebalancing Calculator")
st.markdown("Calculate individual fund/stock contribution amounts and periods under constant price assumptions.")

# 1. General Portfolio Settings
st.subheader("1. General Portfolio Settings")
col_v1, col_v2 = st.columns(2)
with col_v1:
    total_v0 = st.number_input("Total Initial Portfolio Value ($)", value=100000.0, step=1000.0, format="%.2f")

# 2. Mode Selection
calc_mode = st.radio(
    "Select Calculation Mode", 
    [
        "Mode 1: Given Investment Amount per Fund ➔ Calculate Required Periods", 
        "Mode 2: Given Target Periods ➔ Calculate Required Amount per Fund"
    ]
)

st.markdown("---")

# 3. Multi-Asset Table Input
st.subheader("2. Stock / Fund Holdings Breakdown (Max 30 Assets)")
st.markdown("""
* **Current Value ($)**: Initial value of each asset.
* **Target Ratio (%)**: Expected percentage of this asset relative to the **Total Final Portfolio Value**.
* **Amount/Period ($)** (Mode 1 only): Planned investment for each asset per period.
""")

# Initialize DataFrame session state if not existing
if "funds_df" not in st.session_state:
    st.session_state.funds_df = pd.DataFrame([
        {"Ticker / Name": "QQQ", "Current Value ($)": 15000.0, "Target Ratio (%)": 25.0, "Amount/Period ($)": 3000.0},
        {"Ticker / Name": "VOO", "Current Value ($)": 15000.0, "Target Ratio (%)": 35.0, "Amount/Period ($)": 4500.0}
    ])

# Column configuration based on mode
column_config = {
    "Current Value ($)": st.column_config.NumberColumn("Current Value ($)", min_value=0.0, step=100.0, format="$%.2f"),
    "Target Ratio (%)": st.column_config.NumberColumn("Target Ratio (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.2f%%"),
}

if "Mode 1" in calc_mode:
    column_config["Amount/Period ($)"] = st.column_config.NumberColumn("Amount/Period ($)", min_value=0.0, step=100.0, format="$%.2f")
    disabled_cols = []
else:
    # In Mode 2, Amount/Period is calculated automatically
    column_config["Amount/Period ($)"] = st.column_config.NumberColumn("Amount/Period ($) [Auto]", disabled=True, format="$%.2f")
    disabled_cols = ["Amount/Period ($)"]

edited_df = st.data_editor(
    st.session_state.funds_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config=column_config,
    disabled=disabled_cols,
    key="fund_editor"
)

# Enforce max 30 assets
if len(edited_df) > 30:
    st.warning("⚠️ Maximum 30 assets supported. The list has been trimmed.")
    edited_df = edited_df.head(30)

st.session_state.funds_df = edited_df

# Summary stats from table
stock_s0 = edited_df["Current Value ($)"].sum()
total_target_rate = edited_df["Target Ratio (%)"].sum() / 100.0
current_stock_rate = stock_s0 / total_v0 if total_v0 > 0 else 0.0

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Current Total Stock Value", f"${stock_s0:,.2f}")
col_m2.metric("Current Stock Allocation", f"{current_stock_rate * 100:.2f}%")
col_m3.metric("Target Total Stock Allocation", f"{total_target_rate * 100:.2f}%")

st.markdown("---")

# 4. Mode-specific input
if "Mode 2" in calc_mode:
    periods = st.number_input("Target Investment Periods (Periods)", value=10, min_value=1, step=1)

# 5. Execution & Calculation
if st.button("Start Calculation", type="primary", use_container_width=True):
    # Validations
    if total_v0 <= 0:
        st.error("Total initial portfolio value must be greater than 0.")
        st.stop()
    if stock_s0 > total_v0:
        st.error("Total initial stock value cannot exceed total portfolio value.")
        st.stop()
    if total_target_rate <= 0 or total_target_rate >= 1.0:
        st.error("The sum of Target Ratios (%) across all funds must be between 0% and 100%.")
        st.stop()
    if current_stock_rate >= total_target_rate:
        st.warning(f"⚠️ Current total stock allocation ({current_stock_rate*100:.2f}%) has already met or exceeded the target allocation ({total_target_rate*100:.2f}%).")
        st.stop()

    df = edited_df.copy()
    
    if "Mode 1" in calc_mode:
        # Mode 1: Given amounts per period -> calculate required periods N
        total_m = df["Amount/Period ($)"].sum()
        if total_m <= 0:
            st.error("Total investment amount per period across all funds must be greater than 0.")
            st.stop()

        req_periods = []
        for idx, row in df.iterrows():
            r_i = row["Target Ratio (%)"] / 100.0
            s_i0 = row["Current Value ($)"]
            m_i = row["Amount/Period ($)"]
            
            denom = m_i - r_i * total_m
            if denom <= 0:
                # If contribution is too low compared to target weight, target cannot be reached smoothly
                n_i = 999
            else:
                n_i = (r_i * total_v0 - s_i0) / denom
            req_periods.append(max(0, n_i))

        df["Required Periods (Exact)"] = req_periods
        max_p = math.ceil(max(req_periods)) if max(req_periods) < 999 else 0
        
        if max_p == 0:
            st.error("Selected per-period contribution amounts are insufficient to achieve target ratios. Please increase amounts.")
            st.stop()
            
        p = max_p
        amt_per_period = total_m

    else:
        # Mode 2: Given periods N -> calculate required amount for each fund
        p = int(periods)
        # Final Total Portfolio Value VN = (V0 - S0) / (1 - R_target)
        final_v_target = (total_v0 - stock_s0) / (1.0 - total_target_rate)
        
        calculated_m = []
        for idx, row in df.iterrows():
            r_i = row["Target Ratio (%)"] / 100.0
            s_i0 = row["Current Value ($)"]
            s_i_target = r_i * final_v_target
            m_i = (s_i_target - s_i0) / p
            calculated_m.append(max(0.0, m_i))

        df["Amount/Period ($)"] = calculated_m
        amt_per_period = sum(calculated_m)

    # Global Final Results
    total_invest = amt_per_period * p
    final_v = total_v0 + total_invest
    final_s = stock_s0 + total_invest
    final_rate = (final_s / final_v) * 100

    st.success("✅ Calculation Successful!")

    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Total Suggested Amount / Period", f"${amt_per_period:,.2f}")
    res_col2.metric("Total Required Periods", f"{p}")
    res_col3.metric("Final Total Stock Allocation", f"{final_rate:.2f}%")

    st.info(f"• Total Additional Capital: **${total_invest:,.2f}**  \n• Final Total Portfolio Value: **${final_v:,.2f}** (Final Stock Value: **${final_s:,.2f}**)")

    # Per-Asset Final Allocation Breakdown Table
    st.subheader("📊 Individual Asset Breakdown at End of Schedule")
    asset_summary = []
    for idx, row in df.iterrows():
        s_i0 = row["Current Value ($)"]
        m_i = row["Amount/Period ($)"]
        s_i_end = s_i0 + m_i * p
        r_i_end = (s_i_end / final_v) * 100
        
        asset_summary.append({
            "Asset / Ticker": row["Ticker / Name"],
            "Initial Value ($)": f"${s_i0:,.2f}",
            "Amount / Period ($)": f"${m_i:,.2f}",
            "Total Injected ($)": f"${m_i * p:,.2f}",
            "Final Value ($)": f"${s_i_end:,.2f}",
            "Target Ratio (%)": f"{row['Target Ratio (%)']:.2f}%",
            "Final Actual Ratio (%)": f"{r_i_end:.2f}%"
        })
    st.table(asset_summary)

    # Period-by-Period Portfolio Schedule
    st.subheader("📋 Overall Portfolio Period-by-Period Schedule")
    table_data = []
    curr_v = total_v0
    curr_s = stock_s0
    for i in range(1, p + 1):
        curr_v += amt_per_period
        curr_s += amt_per_period
        r = (curr_s / curr_v) * 100
        table_data.append({
            "Period": f"Period {i}",
            "Total Investment ($)": f"${amt_per_period:,.2f}",
            "End Stock Value ($)": f"${curr_s:,.2f}",
            "End Total Value ($)": f"${curr_v:,.2f}",
            "End Allocation (%)": f"{r:.2f}%"
        })
    
    st.table(table_data)
