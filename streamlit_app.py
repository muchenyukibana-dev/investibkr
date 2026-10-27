import streamlit as st
import math

st.set_page_config(page_title="仓位调整计算器", page_icon="📈", layout="centered")

st.title("📈 智能仓位调整计算器")
st.markdown("通过科学的数学模型，自动计算多期投入下的仓位变化与每期金额。")

# 1. 模式选择
calc_mode = st.radio(
    "选择计算模式", 
    ["模式一：指定期数 ➔ 计算每期应投金额", "模式二：指定每期金额 ➔ 计算所需总期数"]
)

st.markdown("---")

# 2. 基础参数输入
col1, col2 = st.columns(2)
with col1:
    v0 = st.number_input("目前总持仓金额 (元)", value=100000.0, step=1000.0)
    target_rate = st.number_input("目标股票仓位比例 (%)", value=60.0, step=1.0) / 100.0

with col2:
    s0 = st.number_input("当前股票持仓金额 (元)", value=30000.0, step=1000.0)
    if "模式一" in calc_mode:
        periods = st.number_input("计划投入期数 (期)", value=10, min_value=1, step=1)
    else:
        amount_per_period = st.number_input("每期计划投入 (元)", value=7500.0, step=500.0)

st.markdown("---")

# 3. 计算按钮与逻辑
if st.button("开始计算", type="primary", use_container_width=True):
    current_rate = s0 / v0
    
    if current_rate >= target_rate:
        st.warning(f"⚠️ 当前股票仓位 ({current_rate*100:.2f}%) 已达到或超过目标仓位，无需额外建仓！")
    else:
        if "模式一" in calc_mode:
            total_need = (target_rate * v0 - s0) / (1 - target_rate)
            amt = total_need / periods
            p = periods
        else:
            amt = amount_per_period
            exact_periods = (target_rate * v0 - s0) / (amt * (1 - target_rate))
            p = math.ceil(exact_periods)

        total_invest = amt * p
        final_v = v0 + total_invest
        final_s = s0 + total_invest
        final_rate = (final_s / final_v) * 100

        # 结果展示看板
        st.success("✅ 计算成功！")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("每期建议投入", f"{amt:,.2f} 元")
        m_col2.metric("总计投入期数", f"{p} 期")
        m_col3.metric("最终达成仓位", f"{final_rate:.2f}%")

        st.info(f"• 补充总本金: **{total_invest:,.2f} 元**  \n• 期末总资产: **{final_v:,.2f} 元**（其中股票资产: {final_s:,.2f} 元）")

        # 逐期推演表格
        st.subheader("📋 逐期仓位推演明细")
        table_data = []
        curr_v = v0
        curr_s = s0
        for i in range(1, p + 1):
            curr_v += amt
            curr_s += amt
            r = (curr_s / curr_v) * 100
            table_data.append({
                "期数": f"第 {i} 期",
                "本期投入(元)": f"{amt:,.2f}",
                "期末股票(元)": f"{curr_s:,.2f}",
                "期末总资产(元)": f"{curr_v:,.2f}",
                "期末实际仓位": f"{r:.2f}%"
            })
        
        st.table(table_data)
