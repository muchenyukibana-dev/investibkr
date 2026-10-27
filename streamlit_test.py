import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Portfolio Position Rebalancer", page_icon="📈", layout="centered")

st.title("📈 智能仓位调整计算器 (多股票异构定投)")
st.markdown("支持自定义每支股票的当前持仓及**不同的每期定投金额**，精准追踪整体仓位与各股票占比。")

# 1. 模式选择
calc_mode = st.radio(
    "选择计算模式", 
    [
        "模式一：指定总期数 ➔ 计算总定投及各股票分配", 
        "模式二：指定各股票每期定投金额 ➔ 计算所需总期数"
    ]
)

st.markdown("---")

# 2. 基础参数
st.subheader("1. 总体资产设置")
col1, col2 = st.columns(2)
with col1:
    total_v0 = st.number_input("目前总持仓金额 ($)", value=100000.0, step=1000.0, format="%.2f")
with col2:
    target_rate = st.number_input("目标股票仓位比例 (%)", value=60, step=1) / 100.0

st.markdown("---")

# 3. 多股票持仓与定投设置
st.subheader("2. 股票持仓与异构定投明细 (最多30支)")
st.markdown("在此处编辑每支股票的**当前价值**以及**各自每期的定投金额**（每支股票可以设为不同的金额）。记得修改后按 **Enter** 确认保存。")

if "stocks_df" not in st.session_state:
    st.session_state.stocks_df = pd.DataFrame([
        {"Stock Ticker": "AAPL", "Current Value ($)": 15000.0, "Periodic Investment ($)": 2000.0},
        {"Stock Ticker": "MSFT", "Current Value ($)": 15000.0, "Periodic Investment ($)": 3000.0}
    ])

edited_df = st.data_editor(
    st.session_state.stocks_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Current Value ($)": st.column_config.NumberColumn("Current Value ($)", min_value=0.0, step=100.0, format="$%.2f"),
        "Periodic Investment ($)": st.column_config.NumberColumn("Periodic Investment ($)", min_value=0.0, step=50.0, format="$%.2f")
    },
    key="stock_editor"
)

if len(edited_df) > 30:
    st.warning("⚠️ 已超过最多30支股票的限制，系统已自动截取前30支。")
    edited_df = edited_df.head(30)

st.session_state.stocks_df = edited_df

# 统计当前股票总市值与当前仓位
stock_s0 = edited_df["Current Value ($)"].sum()
current_rate = stock_s0 / total_v0 if total_v0 > 0 else 0

# 显示实时汇总指标
m1, m2, m3 = st.columns(3)
m1.metric("当前股票总市值", f"${stock_s0:,.2f}")
m2.metric("当前股票总仓位", f"{current_rate * 100:.2f}%")
m3.metric("当前股票种数", f"{len(edited_df)} 支")

st.markdown("---")

if "模式一" in calc_mode:
    periods = st.number_input("计划总投入期数 (期)", value=10, min_value=1, step=1)

if st.button("开始计算", type="primary", use_container_width=True):
    if total_v0 <= 0:
        st.error("目前总持仓金额必须大于 0。")
    elif stock_s0 < 0:
        st.error("股票持仓金额不能为负数。")
    elif target_rate <= 0 or target_rate >= 1:
        st.error("目标仓位必须在 0% 到 100% 之间。")
    elif stock_s0 > total_v0:
        st.error("股票总市值不能超过总持仓金额。")
    elif current_rate >= target_rate:
        st.warning(f"⚠️ 当前股票仓位 ({current_rate*100:.2f}%) 已经达到或超过目标仓位 ({target_rate*100:.2f}%)，无需调整！")
    else:
        stock_invests = edited_df["Periodic Investment ($)"].tolist()
        sum_stock_invests = sum(stock_invests)

        if "模式一" in calc_mode:
            # 模式一：指定期数 N，根据目标计算总股票需求，并按各股票定投金额比例分配权重
            total_need = (target_rate * total_v0 - stock_s0) / (1 - target_rate)
            if sum_stock_invests <= 0:
                st.error("每期各股票定投金额之和必须大于 0。")
                st.stop()
            weights = [inv / sum_stock_invests for inv in stock_invests]
            p = periods
            total_invest = total_need
            amt_per_period = total_invest / p
        else:
            # 模式二：指定每期金额（由表格各项定投金额直接相加），计算所需期数 N
            if sum_stock_invests <= 0:
                st.error("每期各股票定投金额之和必须大于 0。")
                st.stop()
            amt_per_period = sum_stock_invests
            exact_periods = (target_rate * total_v0 - stock_s0) / (amt_per_period * (1 - target_rate))
            p = math.ceil(exact_periods)
            total_invest = amt_per_period * p
            weights = [inv / sum_stock_invests for inv in stock_invests]

        final_v = total_v0 + total_invest
        final_s = stock_s0 + total_invest
        final_rate = (final_s / final_v) * 100

        st.success("✅ 计算成功！")
        
        res1, res2, res3 = st.columns(3)
        res1.metric("每期总定投金额", f"${amt_per_period:,.2f}")
        res2.metric("总计投入期数", f"${p} 期" if isinstance(p, int) else f"{p}")
        res3.metric("最终达成仓位", f"{final_rate:.2f}%")

        st.info(f"• 补充总本金: **${total_invest:,.2f}**  \n• 期末总资产: **${final_v:,.2f}**（其中期末股票市值: ${final_s:,.2f}）")

        # 逐期推演表格
        st.subheader("📋 逐期仓位与各股票明细推演")
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

        # 各股票最终市值与期末占比展示
        st.subheader("📊 各股票期末预估市值与占比明细")
        initial_values = edited_df["Current Value ($)"].tolist()
        tickers = edited_df["Stock Ticker"].tolist()
        
        final_stock_values = [init_v + (total_invest * w) for init_v, w in zip(initial_values, weights)]
        
        stock_summary_df = pd.DataFrame({
            "Stock Ticker": tickers,
            "Initial Value ($)": initial_values,
            "Total Added ($)": [total_invest * w for w in weights],
            "Final Value ($)": final_stock_values,
            "Final Portfolio Share (%)": [f"{(val / final_v) * 100:.2f}%" for val in final_stock_values]
        })
        st.table(stock_summary_df)
