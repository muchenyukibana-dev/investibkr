import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Multi-Asset Independent Rebalancer", page_icon="📈", layout="wide")

st.title("📈 多资产独立定投期数与金额计算器")
st.markdown("支持每只股票/基金设置**各自独立的定投期数或定投金额**，到达各自目标后即自动停止定投。")

# 1. 基础总资产设置
total_v0 = st.number_input("总初始资产 (Total Portfolio Value $)", value=100000.0, step=1000.0, format="%.2f")

# 2. 模式选择
calc_mode = st.radio(
    "选择计算模式", 
    [
        "模式一：给定各基金定投金额 ➔ 计算各自达标所需期数", 
        "模式二：给定各基金期望定投期数 ➔ 计算各自每期定投金额"
    ],
    key="main_calc_mode"
)

st.markdown("---")

# 3. 初始化 Session State（使用固定 Schema 彻底解决填写两遍的问题）
if "funds_df" not in st.session_state:
    st.session_state.funds_df = pd.DataFrame([
        {
            "Ticker / Name": "QQQ", 
            "Current Value ($)": 8000.0, 
            "Target Ratio (%)": 10.0, 
            "Amount/Period ($)": 2000.0,
            "Target Periods": 10
        },
        {
            "Ticker / Name": "VOO", 
            "Current Value ($)": 6000.0, 
            "Target Ratio (%)": 35.0, 
            "Amount/Period ($)": 2000.0,
            "Target Periods": 10
        }
    ])

st.subheader("2. 各基金详细参数配置（最多30支）")
st.markdown("提示：表格结构已优化，修改数值后按 **Enter** 键即可直接保存生效，无需重复填写。")

is_mode_1 = "模式一" in calc_mode

# 动态配置列的可用状态，保持表格 Schema 恒定不变，彻底解决填写两遍的 Bug
column_config = {
    "Ticker / Name": st.column_config.TextColumn("资产代码/名称"),
    "Current Value ($)": st.column_config.NumberColumn("期初持仓金额 ($)", min_value=0.0, step=100.0, format="$%.2f"),
    "Target Ratio (%)": st.column_config.NumberColumn("目标占总资产比例 (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.2f%%"),
    "Amount/Period ($)": st.column_config.NumberColumn(
        "每期定投金额 ($)", 
        min_value=0.0, 
        step=100.0, 
        format="$%.2f",
        disabled=not is_mode_1  # 模式二时自动锁定此列
    ),
    "Target Periods": st.column_config.NumberColumn(
        "期望定投期数 (期)", 
        min_value=1, 
        step=1, 
        format="%d",
        disabled=is_mode_1     # 模式一时自动锁定此列
    )
}

edited_df = st.data_editor(
    st.session_state.funds_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config=column_config,
    key="asset_data_editor"
)

# 限制最多30支
if len(edited_df) > 30:
    st.warning("⚠️ 最多支持 30 支资产，已自动截断至前 30 支。")
    edited_df = edited_df.head(30)

st.session_state.funds_df = edited_df

# 统计当前面板数据
stock_s0 = edited_df["Current Value ($)"].sum()
total_target_rate = edited_df["Target Ratio (%)"].sum() / 100.0
current_stock_rate = stock_s0 / total_v0 if total_v0 > 0 else 0.0

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("期初股票总持仓", f"${stock_s0:,.2f}")
col_m2.metric("当前股票总仓位", f"{current_stock_rate * 100:.2f}%")
col_m3.metric("目标股票总仓位之和", f"{total_target_rate * 100:.2f}%")

st.markdown("---")

if st.button("开始计算", type="primary", use_container_width=True):
    if total_v0 <= 0:
        st.error("总初始资产必须大于 0。")
        st.stop()
    if stock_s0 > total_v0:
        st.error("期初股票总持仓不能大于总资产。")
        st.stop()
    if total_target_rate <= 0 or total_target_rate >= 1.0:
        st.error("所有基金的目标比例总和必须在 0% 到 100% 之间。")
        st.stop()

    df = edited_df.copy()
    
    if is_mode_1:
        # ==================== 模式一计算 ====================
        total_m = df["Amount/Period ($)"].sum()
        if total_m <= 0:
            st.error("每期总定投金额必须大于 0。")
            st.stop()

        sim_data = []
        max_periods = 0
        for idx, row in df.iterrows():
            r_i = row["Target Ratio (%)"] / 100.0
            s_i0 = row["Current Value ($)"]
            m_i = row["Amount/Period ($)"]
            
            denom = m_i - r_i * total_m
            if denom <= 0:
                n_i = 999  # 无法达标
            else:
                n_i = math.ceil((r_i * total_v0 - s_i0) / denom)
                n_i = max(1, n_i)
            
            if n_i < 999 and n_i > max_periods:
                max_periods = n_i
                
            sim_data.append({
                "ticker": row["Ticker / Name"],
                "s0": s_i0,
                "r_target": r_i,
                "amount": m_i,
                "periods": n_i
            })
        
        if max_periods == 0:
            st.error("定投金额相对于目标比例过低，无法达成目标，请调高定投额。")
            st.stop()

        # 展示资产汇总明细
        results = []
        for item in sim_data:
            n_display = f"{item['periods']} 期" if item['periods'] < 999 else "无法达标"
            total_inj = item['amount'] * item['periods'] if item['periods'] < 999 else 0
            final_val = item['s0'] + total_inj if item['periods'] < 999 else 0
            results.append({
                "Asset / Ticker": item['ticker'],
                "Initial Value ($)": f"${item['s0']:,.2f}",
                "Amount / Period ($)": f"${item['amount']:,.2f}",
                "Target Ratio (%)": f"{item['r_target']*100:.2f}%",
                "Required Periods (独立达标期数)": n_display,
                "Total Injected ($)": f"${total_inj:,.2f}"
            })
        
        st.success("✅ 模式一计算完成！")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

        # 逐期推演（带每期末各个股票金额占总资产的百分比）
        st.subheader("📋 逐期资产与各股票仓位百分比推演明细")
        schedule_rows = []
        curr_v = total_v0
        curr_stocks = {item['ticker']: item['s0'] for item in sim_data}
        
        for p in range(1, max_periods + 1):
            period_invest = 0
            for item in sim_data:
                if p <= item['periods']:
                    curr_stocks[item['ticker']] += item['amount']
                    period_invest += item['amount']
            
            curr_v += period_invest
            row_data = {
                "Period": f"Period {p}",
                "Total Investment ($)": f"${period_invest:,.2f}",
                "End Total Portfolio ($)": f"${curr_v:,.2f}"
            }
            for item in sim_data:
                s_val = curr_stocks[item['ticker']]
                pct = (s_val / curr_v) * 100 if curr_v > 0 else 0
                row_data[f"{item['ticker']} Value ($)"] = f"${s_val:,.2f}"
                row_data[f"{item['ticker']} Allocation (%)"] = f"{pct:.2f}%"
            schedule_rows.append(row_data)
            
        st.dataframe(pd.DataFrame(schedule_rows), use_container_width=True)

    else:
        # ==================== 模式二计算 ====================
        s_0 = stock_s0
        r_sum = total_target_rate
        
        final_v_target = (total_v0 - s_0) / (1.0 - r_sum)
        if final_v_target < total_v0:
            st.warning("⚠️ 当前持仓已经达到或超过目标比例，无需再投入。")
            st.stop()

        sim_data = []
        max_periods = 0
        for idx, row in df.iterrows():
            r_i = row["Target Ratio (%)"] / 100.0
            s_i0 = row["Current Value ($)"]
            n_i = max(1, int(row["Target Periods"]))
            
            if n_i > max_periods:
                max_periods = n_i
                
            s_i_target = r_i * final_v_target
            m_i = max(0.0, (s_i_target - s_i0) / n_i)
            
            sim_data.append({
                "ticker": row["Ticker / Name"],
                "s0": s_i0,
                "r_target": r_i,
                "amount": m_i,
                "periods": n_i
            })

        results = []
        for item in sim_data:
            total_inj = item['amount'] * item['periods']
            results.append({
                "Asset / Ticker": item['ticker'],
                "Initial Value ($)": f"${item['s0']:,.2f}",
                "Target Periods (指定期数)": f"{item['periods']} 期",
                "Target Ratio (%)": f"{item['r_target']*100:.2f}%",
                "Required Amount / Period ($)": f"${item['amount']:,.2f}",
                "Total Injected ($)": f"${total_inj:,.2f}"
            })

        st.success("✅ 模式二计算完成！")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

        # 逐期推演（带每期末各个股票金额占总资产的百分比）
        st.subheader("📋 逐期资产与各股票仓位百分比推演明细")
        schedule_rows = []
        curr_v = total_v0
        curr_stocks = {item['ticker']: item['s0'] for item in sim_data}
        
        for p in range(1, max_periods + 1):
            period_invest = 0
            for item in sim_data:
                if p <= item['periods']:
                    curr_stocks[item['ticker']] += item['amount']
                    period_invest += item['amount']
            
            curr_v += period_invest
            row_data = {
                "Period": f"Period {p}",
                "Total Investment ($)": f"${period_invest:,.2f}",
                "End Total Portfolio ($)": f"${curr_v:,.2f}"
            }
            for item in sim_data:
                s_val = curr_stocks[item['ticker']]
                pct = (s_val / curr_v) * 100 if curr_v > 0 else 0
                row_data[f"{item['ticker']} Value ($)"] = f"${s_val:,.2f}"
                row_data[f"{item['ticker']} Allocation (%)"] = f"{pct:.2f}%"
            schedule_rows.append(row_data)
            
        st.dataframe(pd.DataFrame(schedule_rows), use_container_width=True)
