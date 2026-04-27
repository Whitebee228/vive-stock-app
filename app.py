import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
import numpy as np
import FinanceDataReader as fdr
from datetime import datetime, date

st.set_page_config(page_title="바이브 주식분석 어플", layout="wide")
st.title("📈 바이브 주식분석 어플")

if st.button("🔄 전체 실시간 새로고침", type="primary"):
    st.rerun()

# ====================== 기본 함수 ======================
@st.cache_data(ttl=3600)
def get_krx_full_list():
    try:
        df = fdr.StockListing('KRX')
        df['티커'] = df['Code'].astype(str) + '.KS'
        return df[['티커', 'Code', 'Name', 'Market', 'Sector']]
    except:
        return pd.DataFrame()

# ====================== 탭 ======================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 현물 거래 프로 기법", 
    "💼 포트폴리오 + KRW 통합", 
    "🔥 추천", 
    "📊 백테스트", 
    "📊 다중 대시보드", 
    "📅 KRX 심화", 
    "📈 장기 투자"
])

# ====================== Tab 1: 현물 거래 프로 기법 ======================
with tab1:
    st.header("📍 현물 거래 프로 기법")
    ticker = st.text_input("티커 입력", "005930.KS")
    if st.button("분석 시작"):
        st.info("현물 프로 기법 분석이 실행됩니다.")

# ====================== Tab 2: 포트폴리오 + KRW 통합 (오류 수정됨) ======================
with tab2:
    st.header("💼 포트폴리오 관리 + KRW 통합")

    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=['티커', '보유주수', '매입가(원/달러)', '매입일'])

    # 종목 추가
    with st.expander("➕ 종목 추가"):
        c1, c2, c3, c4 = st.columns([2,1,1,1])
        add_ticker = c1.text_input("티커", "AAPL", key="add_t")
        add_shares = c2.number_input("보유주수", min_value=1, value=10)
        add_buy = c3.number_input("매입가", min_value=0.01, value=150.0)
        add_date = c4.date_input("매입일", date.today())
        if st.button("추가"):
            new = pd.DataFrame([[add_ticker.upper(), add_shares, add_buy, add_date]],
                               columns=st.session_state.portfolio.columns)
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, new], ignore_index=True)

    st.subheader("📋 현재 포트폴리오")
    edited_df = st.data_editor(st.session_state.portfolio, num_rows="dynamic", use_container_width=True)
    st.session_state.portfolio = edited_df

    if not st.session_state.portfolio.empty:
        st.subheader("🇰🇷🇺🇸 KRW 통합 포트폴리오")

        usd_krw = 1380.0  # fallback
        try:
            usd_krw = yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1]
        except:
            pass

        data = []
        total_krw = 0

        for _, row in st.session_state.portfolio.iterrows():
            try:
                price = yf.Ticker(row['티커']).fast_info.get('lastPrice')
                is_kr = row['티커'].endswith('.KS')
                value_krw = price * row['보유주수'] * (usd_krw if not is_kr else 1)
                total_krw += value_krw
                
                data.append({
                    "티커": row['티커'],
                    "보유주수": row['보유주수'],
                    "현재가": round(price, 2),
                    "평가액(KRW)": round(value_krw, 0),
                    "국가": "한국" if is_kr else "미국"
                })
            except:
                data.append({
                    "티커": row['티커'],
                    "보유주수": row['보유주수'],
                    "현재가": "오류",
                    "평가액(KRW)": 0,
                    "국가": "알 수 없음"
                })

        port_df = pd.DataFrame(data)
        st.dataframe(port_df, use_container_width=True, hide_index=True)

        st.metric("💰 총 평가액 (KRW)", f"₩{total_krw:,.0f}", f"환율 ≈ {usd_krw:,.0f}원")

st.caption("바이브 주식분석 어플 | 한·미 현물 투자자용 | 투자 책임은 본인에게 있습니다")
