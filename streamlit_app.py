import streamlit as st
import pandas as pd
import math

# 页面基础配置
st.set_page_config(
    page_title="Portfolio Rebalancing Vision", 
    page_icon="🔮", 
    layout="wide"
)

# -----------------------------------------------------------------------------
# 深度定制 CSS：解决白底、文字不清、缺乏主视觉的问题（逻辑代码保持完全不变）
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #070913 !important;
        background-image: 
            radial-gradient(at 15% 10%, rgba(112, 0, 255, 0.3) 0px, transparent 45%),
            radial-gradient(at 85% 15%, rgba(0, 242, 254, 0.25) 0px, transparent 45%),
            radial-gradient(at 50% 75%, rgba(232, 28, 255, 0.2) 0px, transparent 50%);
        background-attachment: fixed;
        color: #f1f5f9 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* 1. 主视觉 Hero Banner 样式（解决缺乏大图视觉的问题） */
    .hero-container {
        position: relative;
        width: 100%;
        height: 220px;
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%),
                    radial-gradient(circle at 70% 30%, rgba(0, 242, 254, 0.4) 0%, transparent 60%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        padding: 0 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        right: -50px;
        top: -50px;
        width: 250px;
        height: 250px;
        background: radial-gradient(circle, rgba(232, 28, 255, 0.3) 0%, transparent 70%);
        border-radius: 50%;
        filter: blur(30px);
        z-index: 1;
    }
    .hero-title {
        position: relative;
        z-index: 2;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 20%, #38bdf8 60%, #e81cff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
    }
    .hero-subtitle {
        position: relative;
        z-index: 2;
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* 2. 玻璃拟态卡片容器 */
    div[data-testid="stVerticalBlock"] > div[style*="flex"] {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.8rem !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }

    /* 3. 彻底修复计算模式单选框（Radio）看不清的问题 */
    div[role="radiogroup"] {
        background: rgba(30, 41, 59, 0.7) !important;
        padding: 14px 20px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
    }
    div[role="radiogroup"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    div[role="radiogroup"] span {
        color: #ffffff !important;
    }

    /* 4. 彻底消除表格（DataFrame）的突兀白色底色 */
    .stDataFrame, [data-testid="stDataFrame"], [data-testid="stTable"] {
        background-color: #0f172a !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        overflow: hidden;
    }
    iframe[data-testid="stDataFrame"] {
        background-color: #0f172a !important;
    }
    
    /* 5. 指标卡片与按钮美化 */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 2rem !important;
        box-shadow: 0 0 25px rgba(124, 58, 237, 0.5) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 35px rgba(6, 182, 212, 0.8) !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 页面主视觉 Header 呈现
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🔮 Portfolio Rebalancing Vision</div>
    <div class="hero-subtitle">Advanced Multi-Asset Independent Rebalancing & Smart Allocation Engine</div>
</div>
""", unsafe_allow_html=True)

# 1. 基础总资产设置
total_v0 = st.number_input("总初始资产 (Total Portfolio Value $)", value=100000.0, step=1000.0, format="%.2f")

# 2. 模式选择
calc_mode = st.radio(
    "选择计算模式 (Calculation Mode)", 
    [
        "模式一：给定各基金定投金额 ➔ 计算各自达标所需期数", 
        "模式二：给定各基金期望定投期数 ➔ 计算各自每期定投金额"
    ],
    key="main_calc_mode"
)

st.markdown("---")

# 3. 初始化 Session State
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

is_mode_1 = "模式一" in calc_mode

column_config = {
    "Ticker / Name": st.column_config.TextColumn("资产代码/名称"),
    "Current Value ($)": st.column_config.NumberColumn("期初持仓金额 ($)", min_value=0.0, step=100.0, format="$%.2f"),
    "Target Ratio (%)": st.column_config.NumberColumn("目标占总资产比例 (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.2f%%"),
    "Amount/Period ($)": st.column_config.NumberColumn(
        "每期定投金额 ($)", 
        min_value=0.0, 
        step=100.0, 
        format="$%.2f",
        disabled=not is_mode_1
    ),
    "Target Periods": st.column_config.NumberColumn(
        "期望定投期数 (期)", 
        min_value=1, 
        step=1, 
        format="%d",
        disabled=is_mode_1
    )
}

edited_df = st.data_editor(
    st.session_state.funds_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config=column_config,
    key="asset_data_editor"
)

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

if st.button("🚀 开始极速计算 (Calculate)", type="primary", use_container_width=True):
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
                n_i = 999
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

        results = []
        for item in sim_data:
            n_display = f"{item['periods']} 期" if item['periods'] < 999 else "无法达标"
            total_inj = item['amount'] * item['periods'] if item['periods'] < 999 else 0
            results.append({
                "Asset / Ticker": item['ticker'],
                "Initial Value ($)": f"${item['s0']:,.2f}",
                "Amount / Period ($)": f"${item['amount']:,.2f}",
                "Target Ratio (%)": f"{item['r_target']*100:.2f}%",
                "Required Periods (独立达标期数)": n_display,
                "Total Injected ($)": f"${total_inj:,.2f}"
            })
        
        st.success("✨ 模式一计算成功！")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

        st.subheader("📊 逐期资产与各股票仓位百分比推演明细")
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

        st.success("✨ 模式二计算成功！")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

        st.subheader("📊 逐期资产与各股票仓位百分比推演明细")
        schedule_rows = []
        curr_v = total_v0
        curr_stocks = {item['ticker']: item['s0'] for item in sim_data}
        
        for p in range(1, max_periods + 1):
            period_invest = 0
            for item in sim_data:
                if p <= item['periods']:
                    curr_stocks[item['ticker']} += item['amount']
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
