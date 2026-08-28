import streamlit as st
import pandas as pd

# 웹페이지 기본 설정
st.set_page_config(page_title="QR플레이트 입금거래 대시보드", layout="wide")

@st.cache_data
def load_data():
    # 변환된 압축 데이터 로드
    df = pd.read_parquet('merged_data.parquet')
    return df

df = load_data()

st.title("💳 QR플레이트 사업자계좌 입금거래 대시보드")
st.caption("64만 건 전체 입금 거래 내역 시각화 및 필터링 시스템")
st.markdown("---")

# 사이드바 (필터 옵션)
st.sidebar.header("🔍 검색 및 필터")

# 1. 판매점 ID 검색창
search_store_id = st.sidebar.text_input("판매점 ID 검색", value="")

# 2. 날짜 선택기
min_date = df['입금일자'].min()
max_date = df['입금일자'].max()

date_range = st.sidebar.date_input(
    "입금일자 범위",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# 3. 입금금액 필터 (000 단위 구분)
deposit_type = st.sidebar.multiselect(
    "입금금액 구분",
    options=['소비자 입금(000단위)', '개인 입출금(기타)'],
    default=['소비자 입금(000단위)', '개인 입출금(기타)']
)

# 4. 기타 필터 (은행, 지역, 업종)
selected_banks = st.sidebar.multiselect("입금은행", options=sorted(df['입금은행'].dropna().unique()))
selected_sido = st.sidebar.multiselect("지역(시/도)", options=sorted(df['시도'].dropna().astype(str).unique()))
selected_category = st.sidebar.multiselect("업종구분", options=sorted(df['업종구분'].dropna().astype(str).unique()))

# 데이터 필터링 적용
filtered_df = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[(filtered_df['입금일자'] >= start_date) & (filtered_df['입금일자'] <= end_date)]

if search_store_id.strip():
    filtered_df = filtered_df[filtered_df['판매점ID'].astype(str).str.contains(search_store_id.strip())]

if deposit_type:
    filtered_df = filtered_df[filtered_df['입금구분'].isin(deposit_type)]

if selected_banks:
    filtered_df = filtered_df[filtered_df['입금은행'].isin(selected_banks)]
if selected_sido:
    filtered_df = filtered_df[filtered_df['시도'].isin(selected_sido)]
if selected_category:
    filtered_df = filtered_df[filtered_df['업종구분'].isin(selected_category)]

# 요약 카드 (KPI)
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 거래 건수", f"{len(filtered_df):,} 건")
col2.metric("총 입금 금액", f"{filtered_df['입금금액'].sum():,} 원")
col3.metric("평균 입금 금액", f"{int(filtered_df['입금금액'].mean() if len(filtered_df)>0 else 0):,} 원")
col4.metric("조회된 판매점 수", f"{filtered_df['판매점ID'].nunique():,} 개")

st.markdown("---")

# 차트 시각화
st.subheader("📊 항목별 시각화 (입금은행 / 지역 / 업종)")
t1, t2, t3 = st.tabs(["🏛️ 입금은행별", "🗺️ 지역별(시/도)", "🏢 업종별"])

with t1:
    st.bar_chart(filtered_df['입금은행'].value_counts().head(10))
with t2:
    st.bar_chart(filtered_df['시도'].value_counts())
with t3:
    st.bar_chart(filtered_df['업종구분'].value_counts().head(10))

st.markdown("---")

# 상세 거래내역 표출
st.subheader("📋 전체 입금거래 상세 내역")
st.caption(f"조회된 데이터: 총 {len(filtered_df):,} 건")

display_cols = [
    '최종거래일시', '판매점ID', '상호', '대표자', '명의자명', 
    '시도', '도로명주소', '업종구분', '입금은행', '입금자', '입금금액', '입금구분'
]

st.dataframe(
    filtered_df[display_cols],
    use_container_width=True,
    height=500
)