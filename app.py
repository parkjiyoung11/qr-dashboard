import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 레이아웃 및 기본 설정
st.set_page_config(
    page_title="QR플레이트 입금거래 대시보드", 
    page_icon="💳", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 고급스러운 Custom CSS 스타일링
st.markdown("""
<style>
    /* 메인 배경 및 Google Pretendard/Inter 스타일 폰트 적용 */
    .main {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* 대시보드 타이틀 헤더 */
    .dashboard-header {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .dashboard-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    
    /* KPI Metric Cards */
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px 16px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        text-align: left;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    .metric-unit {
        font-size: 0.9rem;
        font-weight: 500;
        color: #64748b;
        margin-left: 2px;
    }

    /* Expander (업로드 창) 커스텀 */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }
    
    /* 구분선 및 여백 정돈 */
    hr {
        border-top: 1px solid #e2e8f0;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로딩 함수 (업로드된 데이터 우선 적용 지원)
@st.cache_data
def load_default_data():
    df = pd.read_parquet('merged_data.parquet')
    return df

# 기본 데이터 로드
df = load_default_data()

# 4. 헤더 영역
st.markdown('<div class="dashboard-header">💳 QR플레이트 사업자계좌 입금거래 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">실시간 검색, 금액별/일자별 필터링 및 시각화 분석 리포트</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. 엑셀 파일 업로드 창 (버튼/토글 클릭 시 확장되는 영역)
# ---------------------------------------------------------
with st.expander("📂 신규 데이터 갱신 (엑셀/CSV 파일 업로드)", expanded=False):
    st.markdown("##### 💡 새로운 데이터가 있는 경우 파일 2개를 업로드하여 대시보드를 갱신할 수 있습니다.")
    
    col_up1, col_up2 = st.columns(2)
    
    with col_up1:
        uploaded_daily = st.file_uploader(
            "1. 일주일 / 일별 입금 내역 파일 (.xlsx, .csv)", 
            type=["xlsx", "csv"], 
            key="daily_uploader"
        )
        if uploaded_daily:
            st.caption(f"✓ 업로드됨: `{uploaded_daily.name}`")

    with col_up2:
        uploaded_weekly = st.file_uploader(
            "2. 주별 / 월별 통합 내역 파일 (.xlsx, .csv)", 
            type=["xlsx", "csv"], 
            key="weekly_uploader"
        )
        if uploaded_weekly:
            st.caption(f"✓ 업로드됨: `{uploaded_weekly.name}`")

    # 파일 전처리 및 데이터 갱신 로직 (필요 시 주석 해제하여 연결)
    # if uploaded_daily and uploaded_weekly:
    #     df = process_uploaded_files(uploaded_daily, uploaded_weekly)
    #     st.success("데이터가 성공적으로 갱신되었습니다!")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. 사이드바 (검색 및 필터링)
# ---------------------------------------------------------
st.sidebar.markdown("### 🔍 검색 & 필터링")
st.sidebar.markdown("---")

# 6-1. 판매점 ID 검색
search_store_id = st.sidebar.text_input("🎯 판매점 ID 검색", value="", placeholder="판매점 ID 입력...")

# 6-2. 일자 범위 선택
min_date = df['입금일자'].min()
max_date = df['입금일자'].max()

date_range = st.sidebar.date_input(
    "📅 입금일자 범위",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# 6-3. 입금금액 구분 필터
deposit_type = st.sidebar.multiselect(
    "💵 입금금액 구분",
    options=['소비자 입금(000단위)', '개인 입출금(기타)'],
    default=['소비자 입금(000단위)', '개인 입출금(기타)']
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 세부 항목 필터")

# 6-4. 은행, 지역, 업종 필터
selected_banks = st.sidebar.multiselect("🏛️ 입금은행", options=sorted(df['입금은행'].dropna().unique()))
selected_sido = st.sidebar.multiselect("🗺️ 지역(시/도)", options=sorted(df['시도'].dropna().astype(str).unique()))
selected_category = st.sidebar.multiselect("🏢 업종구분", options=sorted(df['업종구분'].dropna().astype(str).unique()))

# --- 필터링 로직 ---
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

# ---------------------------------------------------------
# 7. 상단 주요 지표 (KPI) 카드 영역
# ---------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_tx = len(filtered_df)
total_amount = filtered_df['입금금액'].sum()
avg_amount = int(filtered_df['입금금액'].mean()) if total_tx > 0 else 0
unique_stores = filtered_df['판매점ID'].nunique()

with kpi1:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-title">📊 총 거래 건수</div>
            <div class="metric-value">{total_tx:,}<span class="metric-unit"> 건</span></div>
        </div>
    ''', unsafe_allow_html=True)

with kpi2:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-title">💰 총 입금 금액</div>
            <div class="metric-value" style="color:#2563eb;">{total_amount:,}<span class="metric-unit"> 원</span></div>
        </div>
    ''', unsafe_allow_html=True)

with kpi3:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-title">📈 건당 평균 입금액</div>
            <div class="metric-value" style="color:#059669;">{avg_amount:,}<span class="metric-unit"> 원</span></div>
        </div>
    ''', unsafe_allow_html=True)

with kpi4:
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-title">🏪 조회 판매점 수</div>
            <div class="metric-value" style="color:#d97706;">{unique_stores:,}<span class="metric-unit"> 개소</span></div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. 시각화 차트 섹션 (Plotly 인터랙티브 차트)
# ---------------------------------------------------------
st.markdown("### 📊 거래 현황 다차원 시각화")
tab1, tab2, tab3 = st.tabs(["🏛️ 입금은행 점유율", "🗺️ 지역별 거래 현황", "🏢 업종별 분포"])

# 차트 공통 레이아웃 설정 함수
def apply_chart_theme(fig):
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=12, color="#334155"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

with tab1:
    col_c1, col_c2 = st.columns([1, 1])
    bank_df = filtered_df['입금은행'].value_counts().reset_index()
    bank_df.columns = ['입금은행', '거래건수']
    
    with col_c1:
        fig_bank_bar = px.bar(
            bank_df.head(10), x='거래건수', y='입금은행', orientation='h',
            title="<b>TOP 10 입금은행 (거래건수)</b>",
            color='거래건수', color_continuous_scale='Blues',
            text='거래건수'
        )
        fig_bank_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=380)
        fig_bank_bar = apply_chart_theme(fig_bank_bar)
        st.plotly_chart(fig_bank_bar, use_container_width=True)
        
    with col_c2:
        fig_bank_pie = px.pie(
            bank_df.head(8), names='입금은행', values='거래건수',
            title="<b>주요 은행별 비중</b>", hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bank_pie.update_layout(height=380)
        fig_bank_pie = apply_chart_theme(fig_bank_pie)
        st.plotly_chart(fig_bank_pie, use_container_width=True)

with tab2:
    sido_df = filtered_df['시도'].value_counts().reset_index()
    sido_df.columns = ['지역(시/도)', '거래건수']
    fig_sido = px.bar(
        sido_df, x='지역(시/도)', y='거래건수',
        title="<b>전국 시/도별 거래 분포</b>",
        color='거래건수', color_continuous_scale='Cividis',
        text='거래건수'
    )
    fig_sido.update_layout(height=400)
    fig_sido = apply_chart_theme(fig_sido)
    st.plotly_chart(fig_sido, use_container_width=True)

with tab3:
    cat_df = filtered_df['업종구분'].value_counts().reset_index()
    cat_df.columns = ['업종구분', '거래건수']
    fig_cat = px.bar(
        cat_df.head(10), x='업종구분', y='거래건수',
        title="<b>TOP 10 업종 분포</b>",
        color='거래건수', color_continuous_scale='Tealgrn',
        text='거래건수'
    )
    fig_cat.update_layout(height=400)
    fig_cat = apply_chart_theme(fig_cat)
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 9. 상세 거래 내역 데이터 테이블
# ---------------------------------------------------------
st.markdown(f"### 📋 상세 거래 내역 목록 <span style='font-size:0.95rem; color:#64748b;'>(조회 결과: {len(filtered_df):,} 건)</span>", unsafe_allow_html=True)

display_cols = [
    '최종거래일시', '판매점ID', '상호', '대표자', '명의자명', 
    '시도', '도로명주소', '업종구분', '입금은행', '입금자', '입금금액', '입금구분'
]

st.dataframe(
    filtered_df[display_cols],
    use_container_width=True,
    height=480
)
