import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Multi-Asset Independent Rebalancer", page_icon="📈", layout="wide")

st.title("📈 多资产独立定投期数与金额计算器")
st.markdown("支持每只股票/基金设置**各自独立的期数或定投金额**，达成各自的目标比例后即各自结束。")

# 1. 基础总资产设置
total_v0 = st.number_input("总初始资产 (Total Portfolio Value $)", value=100000.0, step=1000.0, format="%.2f")

# 2. 模式选择（使用独立 key 彻底解决切换无效的问题）
calc_mode = st.radio(
    "选择计算模式", 
    [
        "模式一：给定各基金定投金额 ➔ 计算各自达标所需期数", 
        "模式二：给定各基金期望定投期数 ➔ 计算各自每期定投金额"
    ],
    key="main_calc_mode"
)

st.markdown("---")

# 初始化 Session State
if "funds_df" not in st.session_state:
    st.session_state.funds_df = pd.DataFrame([
        {"Ticker / Name": "QQQ", "Current Value ($)": 8000.0, "Target Ratio (%)": 10.0, "Param": 2000.0},
        {"Ticker / Name": "VOO", "Current Value ($)": 6000.0, "Target Ratio (%)": 35.0, "Param": 2000.0}
    ])

# 根据当前选择的模式，动态命名表格中的第4列
if "模式一" in calc_mode:
    param_col_name = "Amount/Period ($) [每期定投额]"
else:
    param_col_name = "Target Periods (期数)"

# 同步更新 DataFrame 的列名
df_current = st.session_state.funds_df.copy()
# 如果之前存的是旧名字，统一归一化为当前模式的列名
df_current.columns = ["Ticker / Name", "Current Value ($)", "Target Ratio (%)", param_col_name]

st.subheader("2. 各基金详细参数配置（最多30支）")

column_config = {
    "Current Value ($)": st.column_config.NumberColumn("期初持仓金额 ($)", min_value=0.0, step=100.0, format="$%.2f"),
    "Target Ratio (%)": st.column_config.NumberColumn("目标占总资产比例 (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.2f%%"),
}

if "模式一" in calc_mode:
    column_config[param_col_name] = st.column_config.NumberColumn("每期定投金额 ($)", min_value=0.0, step=100.0, format="$%.2f")
else:
    column_config[param_col_name] = st.column_config.NumberColumn("期望定投期数 (期)", min_value=1, step=1, format="%d")

edited_df = st.data_editor(
    df_current,
    num_rows="dynamic",
    use_container_width=True,
    column_config=column_config,
    key="asset_data_editor"
)

# 限制最多30支
if len(edited_df) > 30:
    st.warning("⚠️ 最多支持 30 支资产，已自动截断至前 30 支。")
    edited_df = edited_df.head(30)

# 保存回 session_state（统一将可变列保存为 "Param"）
saved_df = edited_df.copy()
saved_df.columns = ["Ticker / Name", "Current Value ($)", "Target Ratio (%)", "Param"]
st.session_state.funds_df = saved_df

# 统计当前面板数据
stock_s0 = saved_df["Current Value ($)"].sum()
total_target_rate = saved_df["Target Ratio (%)"].sum() / 100.0
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

    df = saved_df.copy()
    
    if "模式一" in calc_mode:
        # ==================== 模式一逻辑 ====================
        # 给定每只股票的定投金额，计算各自需要多少期才能达到其目标比例
        total_m = df["Param"].sum()
        if total_m <= 0:
            st.error("每期总定投金额必须大于 0。")
            st.stop()

        results = []
        for idx, row in df.iterrows():
            r_i = row["Target Ratio (%)"] / 100.0
            s_i0 = row["Current Value ($)"]
            m_i = row["Param"]
            
            denom = m_i - r_i * total_m
            if denom <= 0:
                n_i_str = "无法达标（定投额相对于目标过低）"
            else:
                n_i = (r_i * total_v0 - s_i0) / denom
                n_i_ceil = math.ceil(n_i)
                n_i_str = f"{max(1, n_i_ceil)} 期"
            
            results.append({
                "Asset / Ticker": row["Ticker / Name"],
                "Initial Value ($)": f"${s_i0:,.2f}",
                "Amount / Period ($)": f"${m_i:,.2f}",
                "Target Ratio (%)": f"{row['Target Ratio (%)']:.2f}%",
                "Required Periods (独立达标期数)": n_i_str
            })
        
        st.success("✅ 模式一计算完成！每只股票可根据自身的定投金额独立计算所需期数：")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

    else:
        # ==================== 模式二逻辑 ====================
        # 给定各基金期望定投期数 N_i 与目标占比 r_i，精准算出每只基金每期各投多少金额
        s_0 = stock_s0
        r_sum = total_target_rate
        
        if (1.0 - r_sum) <= 0:
            st.error("目标比例总和不能等于或超过 100%。")
            st.stop()
            
        # 根据多资产多期限下的数学严谨推导计算总注入资本
        total_injected_capital = (total_v0 * r_sum - s_0) / (1.0 - r_sum)
        if total_injected_capital < 0:
            st.warning("⚠️ 当前持仓已经达到或超过目标比例，无需再投入。")
            st.stop()

        results = []
        for idx, row in df.iterrows():
            r_i = row["Target Ratio (%)"] / 100.0
            s_i0 = row["Current Value ($)"]
            n_i = max(1, int(row["Param"])) # 各自独立的期望期数
            
            # 各自每期需投入金额公式
            total_i = r_i * total_v0 - s_i0 + r_i * total_injected_capital
            m_i = total_i / n_i
            m_i = max(0.0, m_i)
            
            results.append({
                "Asset / Ticker": row["Ticker / Name"],
                "Initial Value ($)": f"${s_i0:,.2f}",
                "Target Periods (指定期数)": f"{n_i} 期",
                "Target Ratio (%)": f"{r_i * 100:.2f}%",
                "Required Amount / Period ($) [建议每期定投]": f"${m_i:,.2f}",
                "Total Injected ($) [总投入]": f"${m_i * n_i:,.2f}"
            })

        st.success("✅ 模式二计算完成！各基金按你指定的各自期数，精准算出了每期应投金额：")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
