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
# 深度定制 CSS：弥散科技感风格
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

    /* 1. 主视觉 Hero Banner 样式 */
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

    /* 3. 修复计算模式单选框（Radio）文字看不清的问题 */
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

    /* 4. 消除表格（DataFrame）的突兀白色底色 */
    .stDataFrame, [data-testid="stDataFrame"], [data-testid="stTable"] {
        background-color: #0f172a !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
