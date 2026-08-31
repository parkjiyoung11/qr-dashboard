import streamlit as st
import pandas as pd
import plotly.express as px
import math

# 1. 페이지 레이아웃 및 기본 설정
st.set_page_config(
    page_title="QR플레이트 입금거래 대시보드", 
    page_icon="💳", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS 및 Gmarket Sans 폰트 + 깔끔한 페이지네이션 UI 스타일
st.markdown("""
<style>
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

    body, p, label, input, button, select, div[data-testid="stMarkdownContainer"] p {
        font-family: 'GmarketSans', -apple-system, sans-serif !important;
        font-weight: 500;
        color: #1e293b;
    }

    i, svg, [class*="st-"], [data-testid="stExpanderToggleIcon"], .material-icons {
        font-family: inherit;
    }

    .main {
        background-color: #f8fafc;
    }
    
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

    .dashboard-subtitle, h3, h4, h5, .stSidebar h3 {
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 500 !important;
    }
    .dashboard-subtitle {
        color: #64748b;
        font-size: 1.0rem;
        margin-bottom: 22px;
    }

    button[data-baseweb="tab"] div {
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
    }

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

    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
    }

    hr {
        border-top: 1px solid #e2e8f0;
        margin: 22px 0;
    }

    /* 콤팩트 페이지네이션 버튼 커스텀 */
    .pagination-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 6px;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .page-btn {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 34px;
        height: 34px;
        border-radius: 50%;
        font-size: 0.95rem;
        font-weight: 500;
        color: #334155;
        background-color: transparent;
        border: 1px solid transparent;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none !important;
    }
    .page-btn.active {
        background-color: #262626;
        color: #ffffff !important;
        font-weight: 700;
    }
    .page-btn.circle-border {
        border: 1px solid #e2e8f0;
        color: #475569;
    }
    .page-btn:hover:not(.active) {
        background-color: #f1f5f9;
    }
</style>
""", unsafe_allow_html=True)

# 3. 감성 파스텔톤 브랜드 색상 맵
BANK_COLOR_MAP = {
    '카카오뱅크': '#FFEAA7',
    '하나은행': '#81ECEC',
    '신한은행': '#74B9FF',
    '케이뱅크': '#A29BFE',
    '국민은행': '#FAB1A0',
    '농축협': '#55E6C1',
    '토스뱅크': '#70A1FF',
    '우리은행': '#81D4FA',
    'NH농협은행': '#A8E6CF',
    '기업은행': '#D6A2E8'
}

# 4. 데이터 로딩 및 속도 최적화 함수
@st.cache_data
def load_default_data():
    df = pd.read_parquet('merged_data.parquet')
    if '입금일자' in df.columns:
        df['입금일자'] = pd.to_datetime(df['입금일자']).dt.date
    return df

try:
    df = load_default_data()
except Exception as e:
    st.error(f"데이터 파일('merged_data.parquet')을 읽어오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 5. 헤더 영역
st.markdown('<div class="dashboard-header">💳 QR플레이트 사업자계좌 입금거래 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">실시간 검색, 금액별/일자별 필터링 및 시각화 분석 리포트</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. 엑셀 파일 업로드 창
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

min_date = df['입금일자'].min() if '입금일자' in df.columns else None
max_date = df['입금일자'].max() if '입금일자' in df.columns else None

if min_date and max_date:
    date_range = st.sidebar.date_input(
        "📅 입금일자 범위",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    date_range = None

deposit_options = sorted(df['입금구분'].dropna().unique()) if '입금구분' in df.columns else []
deposit_type = st.sidebar.multiselect(
    "💵 입금금액 구분",
    options=deposit_options,
    default=deposit_options,
    placeholder="선택하세요"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 세부 항목 필터")

bank_options = sorted(df['입금은행'].dropna().unique()) if '입금은행' in df.columns else []
sido_options = sorted(df['시도'].dropna().astype(str).unique()) if '시도' in df.columns else []
category_options = sorted(df['업종구분'].dropna().astype(str).unique()) if '업종구분' in df.columns else []

selected_banks = st.sidebar.multiselect("🏛️ 입금은행", options=bank_options, placeholder="선택하세요")
selected_sido = st.sidebar.multiselect("🗺️ 지역(시/도)", options=sido_options, placeholder="선택하세요")
selected_category = st.sidebar.multiselect("🏢 업종구분", options=category_options, placeholder="선택하세요")

# --- 필터링 캐싱 적용 (속도 최적화) ---
@st.cache_data
def filter_dataframe(data, search_id, d_range, d_type, banks, sidos, cats):
    f_df = data.copy()
    if d_range and isinstance(d_range, (list, tuple)) and len(d_range) == 2:
        f_df = f_df[(f_df['입금일자'] >= d_range[0]) & (f_df['입금일자'] <= d_range[1])]
    if search_id.strip() and '판매점ID' in f_df.columns:
        f_df = f_df[f_df['판매점ID'].astype(str).str.contains(search_id.strip())]
    if d_type and '입금구분' in f_df.columns:
        f_df = f_df[f_df['입금구분'].isin(d_type)]
    if banks and '입금은행' in f_df.columns:
        f_df = f_df[f_df['입금은행'].isin(banks)]
    if sidos and '시도' in f_df.columns:
        f_df = f_df[f_df['시도'].isin(sidos)]
    if cats and '업종구분' in f_df.columns:
        f_df = f_df[f_df['업종구분'].isin(cats)]
    return f_df

filtered_df = filter_dataframe(df, search_store_id, date_range, deposit_type, selected_banks, selected_sido, selected_category)

# ---------------------------------------------------------
# 8. 상단 주요 지표 (KPI) 카드 영역
# ---------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_tx = len(filtered_df)
total_amount = int(filtered_df['입금금액'].sum()) if '입금금액' in filtered_df.columns else 0
avg_amount = int(filtered_df['입금금액'].mean()) if total_tx > 0 and '입금금액' in filtered_df.columns else 0
unique_stores = filtered_df['판매점ID'].nunique() if '판매점ID' in filtered_df.columns else 0

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
# 9. 시각화 차트 섹션
# ---------------------------------------------------------
st.markdown("<h2 class='section-bold-title' style='font-size: 1.55rem; margin-bottom: 12px;'>📊 거래 현황 다차원 시각화</h2>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏛️ 입금은행 점유율", "🗺️ 지역별 거래 현황", "🏢 업종별 분포"])

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
    
    if '입금은행' in filtered_df.columns and not filtered_df.empty:
        bank_df = filtered_df['입금은행'].value_counts().reset_index()
        bank_df.columns = ['입금은행', '거래건수']
        
        top10_bank_df = bank_df.head(10).copy()
        top8_bank_df = bank_df.head(8).copy()

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
    else:
        st.info("조회된 입금은행 데이터가 없습니다.")

# Tab 2: 지역별 거래 현황
with tab2:
    if '시도' in filtered_df.columns and not filtered_df.empty:
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
    else:
        st.info("조회된 지역 데이터가 없습니다.")

# Tab 3: 업종별 분포
with tab3:
    if '업종구분' in filtered_df.columns and not filtered_df.empty:
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
    else:
        st.info("조회된 업종 데이터가 없습니다.")

st.markdown("---")

# ---------------------------------------------------------
# 10. 상세 거래 내역 데이터 테이블 (속도 저하 없는 초고속 디스플레이)
# ---------------------------------------------------------
st.markdown(f"<h3 style='font-size:1.25rem;'>📋 상세 거래 내역 목록 <span style='font-size:0.95rem; color:#64748b; font-weight:500;'>(조회 결과: {len(filtered_df):,} 건)</span></h3>", unsafe_allow_html=True)

display_cols = [
    '최종거래일시', '판매점ID', '상호', '대표자', '명의자명', 
    '시도', '도로명주소', '업종구분', '입금은행', '입금자', '입금금액', '입금구분'
]

valid_cols = [col for col in display_cols if col in filtered_df.columns]

# --- 초고속 10개 단위 슬라이싱 및 세션 상태 페이지 조절 ---
items_per_page = 10
total_items = len(filtered_df)
total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1

if 'curr_page' not in st.session_state:
    st.session_state.curr_page = 1

# 페이지 번호 범위 제한
if st.session_state.curr_page > total_pages:
    st.session_state.curr_page = total_pages
if st.session_state.curr_page < 1:
    st.session_state.curr_page = 1

# 현재 페이지의 10개만 정확하게 슬라이싱
start_idx = (st.session_state.curr_page - 1) * items_per_page
end_idx = start_idx + items_per_page
page_data = filtered_df[valid_cols].iloc[start_idx:end_idx]

st.dataframe(
    page_data,
    use_container_width=True,
    height=390
)

# --- 요청하신 첨부 이미지와 동일한 콤팩트 페이지네이션 UI (1 2 3 4 5 6 7 8 9 10 > >>) ---
page_block_size = 10
start_p = ((st.session_state.curr_page - 1) // page_block_size) * page_block_size + 1
end_p = min(total_pages, start_p + page_block_size - 1)

page_range = list(range(start_p, end_p + 1))

# 버튼들을 촘촘하게 붙이기 위해 칼럼 너비 좁게 설정
btn_cols = st.columns([1] * len(page_range) + [1, 1] + [8])

for idx, p_num in enumerate(page_range):
    with btn_cols[idx]:
        b_type = "primary" if p_num == st.session_state.curr_page else "secondary"
        if st.button(f"{p_num}", key=f"p_btn_{p_num}", type=b_type):
            st.session_state.curr_page = p_num
            st.rerun()

# '>' 다음 10개 블록 이동
with btn_cols[len(page_range)]:
    if st.button("›", key="next_block", disabled=(end_p >= total_pages)):
        st.session_state.curr_page = min(total_pages, end_p + 1)
        st.rerun()

# '>>' 맨 끝 페이지 이동
with btn_cols[len(page_range) + 1]:
    if st.button("»", key="last_page", disabled=(st.session_state.curr_page == total_pages or total_pages == 0)):
        st.session_state.curr_page = total_pages
        st.rerun()
