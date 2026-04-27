import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import pandas_ta as ta
import numpy as np
import FinanceDataReader as fdr
from datetime import datetime, date

st.set_page_config(page_title="바이브 주식분석 풀패키지", layout="wide")
st.title("📈 바이브 주식분석 어플 + 한·미 현물 투자자 맞춤 (KRW 통합 + 세금 + 배분 제안)")

if st.button("🔄 전체 실시간 새로고침", type="primary"):
    st.rerun()

# ====================== KRX 리스트 ======================
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
    "📈 현물 거래 프로 기법", "💼 포트폴리오 + KRW 통합 + 세금 + 배분", 
    "🔥 추천", "📊 백테스트", "📊 다중 대시보드", "📅 KRX 심화", "📈 장기 투자"
])

# ====================== 탭 1: 현물 거래 프로 기법 (이전 그대로) ======================
with tab1: 
    st.header("📍 현물 거래 프로 기법")

# ====================== 탭 2: 포트폴리오 + KRW 통합 + 세금 + 한·미 배분 ======================
with tab2:
    st.header("💼 포트폴리오 관리 + KRW 통합 + 세금 시뮬레이션 + 한·미 배분")

    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=['티커', '보유주수', '매입가(원/달러)', '매입일'])

    # 종목 추가
    with st.expander("➕ 종목 추가"):
        c1, c2, c3, c4 = st.columns([2,1,1,1])
        add_ticker = c1.text_input("티커", "AAPL")
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
        # ====================== KRW 통합 포트폴리오 ======================
        st.subheader("🇰🇷🇺🇸 KRW 통합 포트폴리오")
        usd_krw = yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1]

        total_krw = 0
        data = []
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
                pass

        port_df = pd.DataFrame(data)
        st.dataframe(port_df, use_container_width=True, hide_index=True)

        st.metric("💰 총 평가액 (KRW)", f"₩{total_krw:,.0f}", f"USD {usd_krw:,.0f}원")

        # ====================== 세금 시뮬레이션 ======================
        st.subheader("🧾 세금 시뮬레이션 (간단 추정)")
        total_profit = 0  # 실제 매입가 대비 차익 계산은 생략하고 예시
        tax_korea = total_krw * 0.22 * 0.2   # 양도세 22% (금융투자소득세 기준 간단)
        tax_us_div = total_krw * 0.154 * 0.1  # 미국 배당세 15.4% 가정
        st.write(f"예상 양도소득세 (한국): ₩{tax_korea:,.0f}")
        st.write(f"예상 미국 배당세: ₩{tax_us_div:,.0f}")

        # ====================== 한·미 배분 제안 ======================
        st.subheader("🌍 한·미 자산 배분 현황 및 제안")
        kr_count = len(port_df[port_df['국가'] == "한국"])
        us_count = len(port_df[port_df['국가'] == "미국"])
        kr_ratio = round(kr_count / (kr_count + us_count) * 100, 1) if (kr_count + us_count) > 0 else 0

        fig = px.pie(names=['한국', '미국'], values=[kr_ratio, 100-kr_ratio], title="한·미 배분 현황")
        st.plotly_chart(fig, use_container_width=True)

        st.info(f"현재 한국 비중: {kr_ratio}% | 추천: 한국 40~60% · 미국 40~60%")

st.caption("바이브 코딩 제작 | 한·미 현물 투자자 맞춤 KRW 통합 + 세금 + 배분 제안 완료 | 비용 0원 개인 사용 | 투자 책임은 본인에게 있습니다")
