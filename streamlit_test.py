import streamlit as st
import pandas as pd
import math

# 页面基础配置
st.set_page_config(
    page_title="Portfolio Rebalancing Vision", 
    page_icon="📈", 
    layout="wide"
)

# -----------------------------------------------------------------------------
# 深度定制 CSS：弥散科技感风格 + 卡片式并排模式选择 + 发光容器
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #070913 !important;
        background-image: 
            radial-gradient(at 10% 15%, rgba(112, 0, 255, 0.25) 0px, transparent 50%),
            radial-gradient(at 90% 20%, rgba(0, 242, 254, 0.2) 0px, transparent 50%),
            radial-gradient(at 50% 85%, rgba(232, 28, 255, 0.18) 0px, transparent 55%);
        background-attachment: fixed;
        color: #f1f5f9 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* 顶部主视觉 Hero Banner 样式 */
    .hero-container {
        position: relative;
        width: 100%;
        height: 180px;
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%),
                    radial-gradient(circle at 70% 30%, rgba(0, 242, 254, 0.4) 0%, transparent 60%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        padding: 0 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 20%, #38bdf8 60%, #e81cff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        font-weight: 400;
    }

    /* 总初始资产发光玻璃容器 */
    .glow-asset-box {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(0, 242, 254, 0.4);
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.15), inset 0 0 15px rgba(0, 242, 254, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* 玻璃拟态卡片容器区块 */
    div[data-testid="stVerticalBlock"] > div[style*="flex"] {
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        padding: 2rem !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
    }

    /* 确认计算按钮强制占满整行并具备炫彩发光 */
    .stFormSubmitButton {
        width: 100% !important;
    }
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 1rem 2rem !important;
        width: 100% !important;
        box-shadow: 0 0 30px rgba(124, 58, 237, 0.6) !important;
        transition: all 0.3s ease !important;
    }
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 40px rgba(6, 182, 212, 0.9) !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 页面主视觉 Header
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Portfolio Rebalancing Vision</div>
    <div class="hero-subtitle">Advanced Multi-Asset Independent Rebalancing & Smart Allocation Engine</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 并排等分的计算模式选择卡片（带悬停与点击交互效果）
# -----------------------------------------------------------------------------
st.markdown("### 选择计算模式 (Calculation Mode)")

# 初始化选中的模式状态
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "mode_1"

col_mode1, col_mode2 = st.columns(2)

# 自定义卡片样式（动态响应选中状态）
with col_mode1:
    is_active_1 = st.session_state.selected_mode == "mode_1"
    bg_1 = "linear-gradient(135deg, rgba(124, 58, 237, 0.4), rgba(6, 182, 212, 0.4))" if is_active_1 else "rgba(30, 41, 59, 0.6)"
    border_1 = "2px solid #06b6d4" if is_active_1 else "1px solid rgba(255, 255, 255, 0.1)"
    
    st.markdown(f"""
    <div style="
        background: {bg_1};
        border: {border_1};
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        cursor: pointer;
        box-shadow: {'0 0 20px rgba(6, 182, 212, 0.4)' if is_active_1 else 'none'};
        transition: all 0.3s ease;
    ">
        <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-bottom: 6px;">模式一：定投金额 ➔ 求期数</div>
        <div style="font-size: 0.85rem; color: #94a3b8;">给定各基金定投金额，计算各自达标所需期数</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("👉 切换到模式一", use_container_width=True, key="btn_mode_1"):
        st.session_state.selected_mode = "mode_1"
        st.rerun()

with col_mode2:
    is_active_2 = st.session_state.selected_mode == "mode_2"
    bg_2 = "linear-gradient(135deg, rgba(124, 58, 237, 0.4), rgba(6, 182, 212, 0.4))" if is_active_2 else "rgba(30, 41, 59, 0.6)"
    border_2 = "2px solid #06b6d4" if is_active_2 else "1px solid rgba(255, 255, 255, 0.1)"
    
    st.markdown(f"""
    <div style="
        background: {bg_2};
        border: {border_2};
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        cursor: pointer;
        box-shadow: {'0 0 20px rgba(6, 182, 212, 0.4)' if is_active_2 else 'none'};
        transition: all 0.3s ease;
    ">
        <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-bottom: 6px;">模式二：期望期数 ➔ 求定投额</div>
        <div style="font-size: 0.85rem; color: #94a3b8;">给定各基金期望期数，计算各自每期定投金额</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("👉 切换到模式二", use_container_width=True, key="btn_mode_2"):
        st.session_state.selected_mode = "mode_2"
        st.rerun()

is_mode_1 = (st.session_state.selected_mode == "mode_1")

st.markdown("---")

# 初始化双模式各自独立的 Session State 数据
if "funds_df_mode1" not in st.session_state:
    st.session_state.funds_df_mode1 = pd.DataFrame([
        {"Ticker / Name": "QQQ", "Current Value ($)": 8000.0, "Target Ratio (%)": 10.0, "Amount/Period ($)": 2000.0},
        {"Ticker / Name": "VOO", "Current Value ($)": 6000.0, "Target Ratio (%)": 35.0, "Amount/Period ($)": 2000.0}
    ])

if "funds_df_mode2" not in st.session_state:
    st.session_state.funds_df_mode2 = pd.DataFrame([
        {"Ticker / Name": "QQQ", "Current Value ($)": 8000.0, "Target Ratio (%)": 10.0, "Target Periods": 10},
        {"Ticker / Name": "VOO", "Current Value ($)": 6000.0, "Target Ratio (%)": 35.0, "Target Periods": 10}
    ])

# -----------------------------------------------------------------------------
# 使用 Form 统一填写并提交计算
# -----------------------------------------------------------------------------
with st.form("rebalance_form"):
    
    # 总初始资产发光容器包裹
    st.markdown('<div class="glow-asset-box">', unsafe_allow_html=True)
    st.subheader("1. 基础全局设置")
    total_v0 = st.number_input("总初始资产 (Total Portfolio Value $)", value=100000.0, step=1000.0, format="%.2f")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("2. 各基金详细参数配置（最多30支）")
    st.markdown(f"💡 **当前模式**：{'【模式一：修改定投金额】' if is_mode_1 else '【模式二：修改期望期数】'}。修改完成后，点击下方按钮统一提交计算。")

    # 根据当前模式动态展示专属列
    if is_mode_1:
        column_config = {
            "Ticker / Name": st.column_config.TextColumn("资产代码/名称"),
            "Current Value ($)": st.column_config.NumberColumn("期初持仓金额 ($)", min_value=0.0, step=100.0, format="$%.2f"),
            "Target Ratio (%)": st.column_config.NumberColumn("目标占总资产比例 (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.1f"),
            "Amount/Period ($)": st.column_config.NumberColumn("每期定投金额 ($)", min_value=0.0, step=100.0, format="$%.2f")
        }
        edited_df = st.data_editor(
            st.session_state.funds_df_mode1,
            num_rows="dynamic",
            use_container_width=True,
            column_config=column_config,
            key="editor_mode_1"
        )
        st.session_state.funds_df_mode1 = edited_df
    else:
        column_config = {
            "Ticker / Name": st.column_config.TextColumn("资产代码/名称"),
            "Current Value ($)": st.column_config.NumberColumn("期初持仓金额 ($)", min_value=0.0, step=100.0, format="$%.2f"),
            "Target Ratio (%)": st.column_config.NumberColumn("目标占总资产比例 (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.1f"),
            "Target Periods": st.column_config.NumberColumn("期望定投期数 (期)", min_value=1, step=1, format="%d")
        }
        edited_df = st.data_editor(
            st.session_state.funds_df_mode2,
            num_rows="dynamic",
            use_container_width=True,
            column_config=column_config,
            key="editor_mode_2"
        )
        st.session_state.funds_df_mode2 = edited_df

    # 占满整行的确认计算按钮
    submitted = st.form_submit_button("✅ 确认计算并录入")

# 限制最多30支
if len(edited_df) > 30:
    st.warning("⚠️ 最多支持 30 支资产，已自动截断至前 30 支。")
    edited_df = edited_df.head(30)

# -----------------------------------------------------------------------------
# 计算与渲染逻辑（点击表单提交按钮后触发）
# -----------------------------------------------------------------------------
if submitted:
    stock_s0 = edited_df["Current Value ($)"].sum()
    total_target_rate = edited_df["Target Ratio (%)"].sum() / 100.0
    current_stock_rate = stock_s0 / total_v0 if total_v0 > 0 else 0.0

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
                "Target Ratio (%)": f"{item['r_target']*100:.1f}%",
                "Required Periods (系统计算结果)": n_display,
                "Total Injected ($)": f"${total_inj:,.2f}"
            })
        
        st.success("✨ 模式一计算成功！")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

        st.subheader("📊 逐期资产与各股票仓位百分比推演明细（只读结果）")
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
                "Target Ratio (%)": f"{item['r_target']*100:.1f}%",
                "Required Amount / Period ($) [系统计算]": f"${item['amount']:,.2f}",
                "Total Injected ($)": f"${total_inj:,.2f}"
            })

        st.success("✨ 模式二计算成功！")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

        st.subheader("📊 逐期资产与各股票仓位百分比推演明细（只读结果）")
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
