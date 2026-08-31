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

# 2. 안전한 Custom CSS 및 Gmarket Sans 폰트 설정 (폰트 웹로드 안정화 및 아이콘 버그 완벽 수정)
st.markdown("""
<style>
    /* Gmarket Sans 폰트 안전 로드 */
    @font-face {
        font-family: 'GmarketSans';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff2') format('woff2');
        font-weight: 500;
        font-style: normal;
    }
    @font-face {
        font-family: 'GmarketSans';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff2') format('woff2');
        font-weight: 700;
        font-style: normal;
    }

    /* 전역 폰트 지정: Medium(500)으로 선명함 확보 */
    html, body, p, span, label, input, button, select {
        font-family: 'GmarketSans', -apple-system, sans-serif !important;
        font-weight: 500 !important;
        color: #1e293b;
    }

    /* Streamlit 아이콘 및 확장 버튼 텍스트 겹침 완벽 방지 */
    [class*="st-"] i, [class*="st-"] svg, .material-icons {
        font-family: inherit !important;
    }

    /* 메인 배경 */
    .main {
        background-color: #f8fafc;
    }
    
    /* 대시보드 타이틀 - Bold (700) */
    .dashboard-header, h1, h2, .section-bold-title {
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 700 !important;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    .dashboard-header {
        font-size: 2.2rem;
        margin-bottom: 6px;
    }

    /* 서브 타이틀 및 레이블 - Medium (500) */
    .dashboard-subtitle, h3, h4, h5, .stSidebar h3 {
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 500 !important;
    }
    .dashboard-subtitle {
        color: #64748b;
        font-size: 1.0rem;
        margin-bottom: 22px;
    }

    /* 탭 메뉴 폰트 크기 및 굵기 설정 */
    button[data-baseweb="tab"] div {
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
    }

    /* KPI Metric Cards - 가독성 우수 */
    .metric-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 22px 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
        text-align: left;
    }
    .metric-title {
        font-family: 'GmarketSans', sans-serif !important;
        font-size: 1.0rem !important;
        font-weight: 500 !important;
        color: #475569;
        margin-bottom: 10px;
    }
    .metric-value {
        font-family: 'GmarketSans', sans-serif !important;
        font-size: 1.85rem;
        font-weight: 700 !important;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    .metric-unit {
        font-size: 1.0rem;
        font-weight: 500 !important;
        color: #64748b;
        margin-left: 2px;
    }

    /* 파일 업로드 Expander 헤더 정돈 */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
    }

    hr {
        border-top: 1px solid #e2e8f0;
        margin: 22px 0;
    }
</style>
""", unsafe_allow_html=True)

# 3. 감성 파스텔톤 브랜드 색상 맵 (Soft Pastel Colors)
BANK_COLOR_MAP = {
    '카카오뱅크': '#FFEAA7',  # 파스텔 옐로우
    '하나은행': '#81ECEC',    # 민트 파스텔
    '신한은행': '#74B9FF',    # 소프트 스카이블루
    '케이뱅크': '#A29BFE',    # 소프트 라일락
    '국민은행': '#FAB1A0',    # 살구 파스텔
    '농축협': '#55E6C1',      # 에메랄드 파스텔
    '토스뱅크': '#70A1FF',    # 파스텔 블루
    '우리은행': '#81D4FA',    # 라이트 파스텔 블루
    'NH농협은행': '#A8E6CF',  # 연두 파스텔
    '기업은행': '#D6A2E8'     # 피치 퍼플
}

# 4. 데이터 로딩 함수 (Parquet 파일 로드)
@st.cache_data
def load_default_data():
    df = pd.read_parquet('merged_data.parquet')
    return df

try:
    df = load_default_data()
except Exception as e:
    st.error(f"데이터 파일('merged_data.parquet')을 불러오는데 실패했습니다: {e}")
    st.stop()

# 5. 헤더 영역
st.markdown('<div class="dashboard-header">💳 QR플레이트 사업자계좌 입금거래 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">실시간 검색, 금액별/일자별 필터링 및 시각화 분석 리포트</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. 엑셀 파일 업로드 창 (버튼/토글 클릭 시 확장되는 영역)
# ---------------------------------------------------------
with st.expander("📂 신규 데이터 갱신 (엑셀/CSV 파일 업로드)", expanded=False):
    st.markdown("<p style='font-size:0.95rem; color:#475569;'>💡 새로운 데이터가 있는 경우 파일 2개를 업로드하여 대시보드를 갱신할 수 있습니다.</p>", unsafe_allow_html=True)
    
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

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. 사이드바 (검색 및 필터링)
# ---------------------------------------------------------
st.sidebar.markdown("### 🔍 검색 & 필터링")
st.sidebar.markdown("---")

search_store_id = st.sidebar.text_input("🎯 판매점 ID 검색", value="", placeholder="판매점 ID 입력...")

min_date = df['입금일자'].min()
max_date = df['입금일자'].max()

date_range = st.sidebar.date_input(
    "📅 입금일자 범위",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

deposit_type = st.sidebar.multiselect(
    "💵 입금금액 구분",
    options=['소비자 입금(000단위)', '개인 입출금(기타)'],
    default=['소비자 입금(000단위)', '개인 입출금(기타)']
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 세부 항목 필터")

selected_banks = st.sidebar.multiselect("🏛️ 입금은행", options=sorted(df['입금은행'].dropna().unique()))
selected_sido = st.sidebar.multiselect("🗺️ 지역(시/도)", options=sorted(df['시도'].dropna().astype(str).unique()))
selected_category = st.sidebar.multiselect("🏢 업종구분", options=sorted(df['업종구분'].dropna().astype(str).unique()))

# --- 필터링 로직 ---
filtered_df = df.copy()

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
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
# 8. 상단 주요 지표 (KPI) 카드 영역
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
# 9. 시각화 차트 섹션 (Plotly 인터랙티브 차트)
# ---------------------------------------------------------
st.markdown("<h2 class='section-bold-title' style='font-size: 1.55rem; margin-bottom: 12px;'>📊 거래 현황 다차원 시각화</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏛️ 입금은행 점유율", "🗺️ 지역별 거래 현황", "🏢 업종별 분포"])

# Plotly 차트 공통 테마 함수
def apply_chart_theme(fig):
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="GmarketSans, sans-serif", size=12, color="#334155"),
        title_font=dict(family="GmarketSans, sans-serif", size=15, color="#0f172a"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# Tab 1: 입금은행 점유율
with tab1:
    col_c1, col_c2 = st.columns([1, 1])
    
    bank_df = filtered_df['입금은행'].value_counts().reset_index()
    bank_df.columns = ['입금은행', '거래건수']
    
    top10_bank_df = bank_df.head(10).copy()
    top8_bank_df = bank_df.head(8).copy()

    # 1. 막대 차트 (파스텔톤 적용)
    with col_c1:
        fig_bank_bar = px.bar(
            top10_bank_df, 
            x='거래건수', 
            y='입금은행', 
            orientation='h',
            title="<b>TOP 10 입금은행 (거래건수)</b>",
            color='입금은행',
            color_discrete_map=BANK_COLOR_MAP,
            text='거래건수'
        )
        
        fig_bank_bar.update_traces(
            texttemplate='%{text:,.0f}', 
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(family="GmarketSans", size=11)
        )
        
        max_val = top10_bank_df['거래건수'].max() if not top10_bank_df.empty else 100000
        step = max(20000, int(max_val // 5)) if max_val > 0 else 20000
        tick_vals = list(range(0, int(max_val) + step, step))
        tick_texts = [f"{v//10000}만" if v >= 10000 else (f"{v:,}" if v > 0 else "0") for v in tick_vals]
        
        fig_bank_bar.update_layout(
            yaxis={'categoryorder': 'total ascending'}, 
            xaxis=dict(
                tickmode='array',
                tickvals=tick_vals,
                ticktext=tick_texts
            ),
            showlegend=False, 
            height=400
        )
        fig_bank_bar = apply_chart_theme(fig_bank_bar)
        st.plotly_chart(fig_bank_bar, use_container_width=True)
        
    # 2. 파이 차트 (동일 파스텔톤)
    with col_c2:
        fig_bank_pie = px.pie(
            top8_bank_df, 
            names='입금은행', 
            values='거래건수',
            title="<b>주요 은행별 비중</b>", 
            hole=0.48,
            color='입금은행',
            color_discrete_map=BANK_COLOR_MAP
        )
        
        fig_bank_pie.update_traces(
            textinfo='percent',
            hoverinfo='label+value+percent',
            hovertemplate="<b>%{label}</b><br>거래건수: %{value:,.0f}건<br>비중: %{percent:.1%}",
            texttemplate='%{percent:.1%}',
            textfont=dict(family="GmarketSans", size=12)
        )
        
        fig_bank_pie.update_layout(height=400)
        fig_bank_pie = apply_chart_theme(fig_bank_pie)
        st.plotly_chart(fig_bank_pie, use_container_width=True)

# Tab 2: 지역별 거래 현황
with tab2:
    sido_df = filtered_df['시도'].value_counts().reset_index()
    sido_df.columns = ['지역(시/도)', '거래건수']
    
    pastel_blue_pink = ['#D6E4FF', '#ADC6FF', '#85A5FF', '#9254DE', '#F759AB']
    
    fig_sido = px.bar(
        sido_df, x='지역(시/도)', y='거래건수',
        title="<b>전국 시/도별 거래 분포</b>",
        color='거래건수', color_continuous_scale=pastel_blue_pink,
        text='거래건수'
    )
    fig_sido.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont=dict(family="GmarketSans"))
    fig_sido.update_layout(height=400)
    fig_sido = apply_chart_theme(fig_sido)
    st.plotly_chart(fig_sido, use_container_width=True)

# Tab 3: 업종별 분포
with tab3:
    cat_df = filtered_df['업종구분'].value_counts().reset_index()
    cat_df.columns = ['업종구분', '거래건수']
    
    pastel_mint_purple = ['#E6F7FF', '#BAE7FF', '#91D5FF', '#B37FEB', '#9254DE']
    
    fig_cat = px.bar(
        cat_df.head(10), x='업종구분', y='거래건수',
        title="<b>TOP 10 업종 분포</b>",
        color='거래건수', color_continuous_scale=pastel_mint_purple,
        text='거래건수'
    )
    fig_cat.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont=dict(family="GmarketSans"))
    fig_cat.update_layout(height=400)
    fig_cat = apply_chart_theme(fig_cat)
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 10. 상세 거래 내역 데이터 테이블
# ---------------------------------------------------------
st.markdown(f"<h3 style='font-size:1.25rem;'>📋 상세 거래 내역 목록 <span style='font-size:0.95rem; color:#64748b; font-weight:500;'>(조회 결과: {len(filtered_df):,} 건)</span></h3>", unsafe_allow_html=True)

display_cols = [
    '최종거래일시', '판매점ID', '상호', '대표자', '명의자명', 
    '시도', '도로명주소', '업종구분', '입금은행', '입금자', '입금금액', '입금구분'
]

# 존재하는 컬럼만 필터링하여 안전하게 표출
valid_cols = [col for col in display_cols if col in filtered_df.columns]

st.dataframe(
    filtered_df[valid_cols],
    use_container_width=True,
    height=480
)
