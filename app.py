import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# 1. 페이지 레이아웃 및 기본 설정
st.set_page_config(
    page_title="QR플레이트 입금거래 통합 분석 대시보드", 
    page_icon="💳", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 전역 스타일 및 Custom CSS (Gmarket Sans 폰트, 반응형 캡슐 페이지네이션)
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

    body, p, label, select, .stMarkdown p {
        font-family: 'GmarketSans', -apple-system, sans-serif !important;
        font-weight: 500;
        color: #1e293b;
    }

    .main {
        background-color: #f8fafc;
    }
    
    .dashboard-header {
        font-family: 'GmarketSans', sans-serif !important;
        font-size: 2.2rem;
        font-weight: 700 !important;
        color: #0f172a;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .dashboard-subtitle {
        font-family: 'GmarketSans', sans-serif !important;
        color: #64748b;
        font-size: 0.98rem;
        font-weight: 500;
        margin-bottom: 20px;
    }

    .section-bold-title {
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 700 !important;
        color: #0f172a;
    }

    button[data-baseweb="tab"] div {
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
    }

    /* KPI 카드 디자인 */
    .metric-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 20px 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
        text-align: left;
    }
    .metric-title {
        font-family: 'GmarketSans', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        color: #475569;
        margin-bottom: 8px;
    }
    .metric-value {
        font-family: 'GmarketSans', sans-serif !important;
        font-size: 1.75rem;
        font-weight: 700 !important;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    .metric-unit {
        font-size: 0.95rem;
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

    /* 파일 업로더 내부 아이콘/텍스트 숨김 처리 */
    [data-testid="stFileUploader"] section > div:first-child {
        display: none !important;
    }
    [data-testid="stFileUploader"] section {
        padding: 14px 16px !important;
        background-color: #f1f5f9 !important;
        border: 1px dashed #cbd5e1 !important;
        border-radius: 8px !important;
        min-height: 48px !important;
    }

    /* 페이지네이션 버튼 디자인 (원형/캡슐형 & 줄바꿈 방지) */
    div[data-testid="stHorizontalBlock"] button[kind="secondary"],
    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        min-width: 36px !important;
        width: auto !important;
        height: 36px !important;
        min-height: 36px !important;
        border-radius: 18px !important;
        padding: 0 10px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-family: 'GmarketSans', sans-serif !important;
        font-size: 0.88rem !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #ffffff !important;
        color: #334155 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        margin: 0 auto !important;
    }

    div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        background-color: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
        color: #0f172a !important;
    }

    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-color: #1e293b !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(30, 41, 59, 0.25) !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 색상 팔레트 상수 정의
PASTEL_COLOR_SEQUENCE = [
    '#74B9FF', '#A29BFE', '#FFEAA7', '#81ECEC', '#FAB1A0', 
    '#55E6C1', '#70A1FF', '#81D4FA', '#A8E6CF', '#D6A2E8', 
    '#FBC531', '#4CD137', '#487EB0', '#E1B12C', '#E84118'
]
PASTEL_BLUE_PURPLE = ['#D6E4FF', '#ADC6FF', '#85A5FF', '#9254DE', '#F759AB']
PASTEL_MINT_PURPLE = ['#E6F7FF', '#BAE7FF', '#91D5FF', '#B37FEB', '#9254DE']

# 4. 데이터 로드 및 전처리 가공 함수
@st.cache_data
def load_and_preprocess_data():
    df = pd.read_parquet('merged_data.parquet')
    
    # 1) 입금일시 및 파생 시간 변수 생성
    date_col = None
    for col in ['최종거래일시', '입금일시', '거래일시', '입금일자', '거래일자']:
        if col in df.columns:
            date_col = col
            break
            
    if date_col:
        df['datetime_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
    else:
        df['datetime_parsed'] = pd.Timestamp.now()
        
    df['입금일자'] = df['datetime_parsed'].dt.date
    df['입금연월'] = df['datetime_parsed'].dt.strftime('%Y-%m')
    
    # 요일 파생 (0=월요일 ... 6=일요일) -> 한글 요일 매핑
    day_map = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
    df['요일'] = df['datetime_parsed'].dt.dayofweek.map(day_map)
    df['요일순서'] = df['datetime_parsed'].dt.dayofweek.map({6:0, 0:1, 1:2, 2:3, 3:4, 4:5, 5:6}) # 일요일부터 시작 정렬용

    # 2) 은행명 표준화
    if '입금은행' in df.columns:
        bank_rename_map = {
            '006': '006(국민은행(구 한국주택은행))',
            '030': '030(수협중앙회)',
            6: '006(국민은행(구 한국주택은행))',
            30: '030(수협중앙회)',
            '6': '006(국민은행(구 한국주택은행))',
            '30': '030(수협중앙회)'
        }
        df['입금은행'] = df['입금은행'].replace(bank_rename_map).fillna('미분류')

    # 3) 업체상태 -> 통합 상태구분(정상 / 해지) 생성
    status_col = None
    for sc in ['업체상태', '상태구분', '상태', '영업상태']:
        if sc in df.columns:
            status_col = sc
            break
            
    if status_col:
        def categorize_status(val):
            val_str = str(val).strip()
            if any(k in val_str for k in ['정상', '일시정지', '벌칙']):
                return '정상'
            elif any(k in val_str for k in ['해지', '폐업', '중단']):
                return '해지'
            return '정상'  # 기본값
        df['통합상태구분'] = df[status_col].apply(categorize_status)
    else:
        df['통합상태구분'] = '정상'

    # 4) 세부 입금구분 확장 (000단위, 리워드/보상금, 일반/기타)
    def categorize_deposit_detail(row):
        amt = row.get('입금금액', 0)
        memo = str(row.get('입금자', '')) + " " + str(row.get('입금구분', ''))
        
        # 1. 리워드/보상금 키워드 검출
        if any(keyword in memo for keyword in ['보상', '리워드', '캐시', '이벤트', '환급', '포인트']):
            return '리워드/보상금 입금'
        
        # 2. 금액 단위 검출
        try:
            amt_int = int(amt)
            if amt_int > 0 and amt_int % 1000 == 0:
                return '소비자 정액입금(000단위)'
            elif amt_int > 0:
                return '일반/기타 소액입금'
        except:
            pass
        return '기타 입금'

    df['세부입금구분'] = df.apply(categorize_deposit_detail, axis=1)

    return df

try:
    df = load_and_preprocess_data()
except Exception as e:
    st.error(f"데이터 파일('merged_data.parquet') 로딩 중 오류가 발생했습니다: {e}")
    st.stop()

# 5. 헤더 영역
st.markdown('<div class="dashboard-header">💳 QR플레이트 사업자계좌 입금거래 통합 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">실시간 필터링, 월별/요일별 다차원 통계 및 상세 거래 데이터 분석 리포트</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. 파일 업로드 섹션
# ---------------------------------------------------------
with st.expander("📂 신규 데이터 갱신 (엑셀/CSV 파일 업로드)", expanded=False):
    st.markdown("<p style='font-size:0.92rem; color:#475569;'>💡 신규 입금 거래 내역 파일 및 판매점 마스터 정보를 업로드하여 대시보드를 갱신할 수 있습니다.</p>", unsafe_allow_html=True)
    col_up1, col_up2 = st.columns(2)
    with col_up1:
        uploaded_daily = st.file_uploader("1. 일주일 / 일별 입금 내역 파일 (.xlsx, .csv)", type=["xlsx", "csv"], key="daily_uploader")
        if uploaded_daily: st.caption(f"✓ 업로드됨: `{uploaded_daily.name}`")
    with col_up2:
        uploaded_weekly = st.file_uploader("2. 주별 / 월별 통합 내역 파일 (.xlsx, .csv)", type=["xlsx", "csv"], key="weekly_uploader")
        if uploaded_weekly: st.caption(f"✓ 업로드됨: `{uploaded_weekly.name}`")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. 사이드바 (필터링 컨트롤러)
# ---------------------------------------------------------
st.sidebar.markdown("### 🔍 검색 & 핵심 필터")
st.sidebar.markdown("---")

search_store_id = st.sidebar.text_input("🎯 판매점 ID / 상호 검색", value="", placeholder="판매점ID 또는 상호 입력...")

# 1) 판매점 상태 필터 (정상 / 해지)
status_options = ['전체'] + sorted(df['통합상태구분'].unique().tolist())
selected_status = st.sidebar.selectbox("🏷️ 판매점 상태구분", options=status_options, index=0)

# 2) 기간 선택 모드 (일자별 vs 월별)
period_mode = st.sidebar.radio("📅 기간 필터 모드", ["일자별 선택", "월별(연월) 선택"], horizontal=True)

min_date = df['입금일자'].min()
max_date = df['입금일자'].max()
all_months = sorted(df['입금연월'].unique().tolist())

if period_mode == "일자별 선택":
    date_range = st.sidebar.date_input("조회 기간 설정", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    selected_months = None
else:
    date_range = None
    selected_months = st.sidebar.multiselect("조회 연월 선택", options=all_months, default=all_months, placeholder="월을 선택하세요")

# 3) 세부 입금구분 필터
deposit_detail_options = sorted(df['세부입금구분'].unique())
selected_deposit_details = st.sidebar.multiselect(
    "💵 세부 입금금액 구분",
    options=deposit_detail_options,
    default=deposit_detail_options,
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

# --- 데이터 필터링 실행 ---
filtered_df = df.copy()

# 상태 필터
if selected_status != '전체':
    filtered_df = filtered_df[filtered_df['통합상태구분'] == selected_status]

# 기간 필터
if period_mode == "일자별 선택" and date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    filtered_df = filtered_df[(filtered_df['입금일자'] >= date_range[0]) & (filtered_df['입금일자'] <= date_range[1])]
elif period_mode == "월별(연월) 선택" and selected_months:
    filtered_df = filtered_df[filtered_df['입금연월'].isin(selected_months)]

# 검색 필터 (ID or 상호)
if search_store_id.strip():
    q = search_store_id.strip()
    id_cond = filtered_df['판매점ID'].astype(str).str.contains(q) if '판매점ID' in filtered_df.columns else False
    name_cond = filtered_df['상호'].astype(str).str.contains(q) if '상호' in filtered_df.columns else False
    filtered_df = filtered_df[id_cond | name_cond]

# 세부 입금구분 필터
if selected_deposit_details:
    filtered_df = filtered_df[filtered_df['세부입금구분'].isin(selected_deposit_details)]

# 다중 선택 필터
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
# 9. 다차원 시각화 차트 섹션 (월별/요일별/은행/지역/업종)
# ---------------------------------------------------------
st.markdown("<h2 class='section-bold-title' style='font-size: 1.55rem; margin-bottom: 12px;'>📊 거래 현황 다차원 시각화</h2>", unsafe_allow_html=True)

tab_month, tab_day, tab_bank, tab_sido, tab_cat = st.tabs([
    "📅 월별 입금 추이",
    "📆 요일별 거래 비중",
    "🏛️ 입금은행 점유율", 
    "🗺️ 지역별 거래 현황", 
    "🏢 업종별 분포"
])

def apply_chart_theme(fig):
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="GmarketSans, sans-serif", size=12, color="#334155"),
        title_font=dict(family="GmarketSans, sans-serif", size=15, color="#0f172a"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def get_korean_axis_ticks(max_val):
    if max_val <= 0: return [0], ["0"]
    step = max(10000, int(max_val // 4))
    step = int(math.ceil(step / 10000.0) * 10000)
    vals = list(range(0, int(max_val) + step, step))
    texts = ["0" if v == 0 else (f"{v//10000}만" if v >= 10000 else f"{v:,}") for v in vals]
    return vals, texts

# Tab 1: 월별 입금 추이 (신설)
with tab_month:
    if not filtered_df.empty:
        month_summary = filtered_df.groupby('입금연월').agg(
            거래건수=('입금금액', 'count'),
            총입금액=('입금금액', 'sum')
        ).reset_index().sort_values('입금연월')

        fig_month = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 거래건수 막대
        fig_month.add_trace(
            go.Bar(
                x=month_summary['입금연월'],
                y=month_summary['거래건수'],
                name="거래건수 (건)",
                marker_color='#85A5FF',
                text=month_summary['거래건수'],
                texttemplate='%{text:,.0f}',
                textposition='outside'
            ),
            secondary_y=False
        )

        # 총입금액 라인
        fig_month.add_trace(
            go.Scatter(
                x=month_summary['입금연월'],
                y=month_summary['총입금액'],
                name="총 입금액 (원)",
                mode='lines+markers+text',
                line=dict(color='#FA8C16', width=3),
                marker=dict(size=8),
                text=[f"{v//100000000}억 {abs(v)%100000000//10000}만" if v >= 100000000 else f"{v//10000}만원" for v in month_summary['총입금액']],
                textposition='top center'
            ),
            secondary_y=True
        )

        max_tx = month_summary['거래건수'].max() if not month_summary.empty else 100000
        t_vals_m, t_texts_m = get_korean_axis_ticks(max_tx * 1.15)

        fig_month.update_layout(
            title="<b>월별 거래건수 및 총 입금액 추이</b>",
            yaxis=dict(title="거래건수", tickmode='array', tickvals=t_vals_m, ticktext=t_texts_m),
            yaxis2=dict(title="총 입금액", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=420
        )
        fig_month = apply_chart_theme(fig_month)
        st.plotly_chart(fig_month, use_container_width=True)
    else:
        st.info("조회된 기간 내 데이터가 없습니다.")

# Tab 2: 요일별 거래 비중 (신설)
with tab_day:
    if not filtered_df.empty:
        col_d1, col_d2 = st.columns([1.1, 0.9])
        
        # 일요일~토요일 순 정렬
        day_order = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일']
        day_summary = filtered_df.groupby('요일').agg(
            거래건수=('입금금액', 'count'),
            총입금액=('입금금액', 'sum')
        ).reindex(day_order).fillna(0).reset_index()

        with col_d1:
            fig_day_bar = px.bar(
                day_summary,
                x='요일',
                y='거래건수',
                title="<b>요일별 거래건수 분포 (일~토)</b>",
                color='거래건수',
                color_continuous_scale=PASTEL_BLUE_PURPLE,
                text='거래건수'
            )
            fig_day_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            max_day_v = day_summary['거래건수'].max() if not day_summary.empty else 100000
            t_vals_d, t_texts_d = get_korean_axis_ticks(max_day_v * 1.15)
            fig_day_bar.update_layout(
                yaxis=dict(tickmode='array', tickvals=t_vals_d, ticktext=t_texts_d),
                coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_d, ticktext=t_texts_d),
                height=400
            )
            fig_day_bar = apply_chart_theme(fig_day_bar)
            st.plotly_chart(fig_day_bar, use_container_width=True)

        with col_d2:
            fig_day_pie = px.pie(
                day_summary,
                names='요일',
                values='거래건수',
                title="<b>요일별 거래건수 점유 비중</b>",
                hole=0.48,
                color_discrete_sequence=PASTEL_COLOR_SEQUENCE
            )
            fig_day_pie.update_traces(
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>거래건수: %{value:,.0f}건<br>비중: %{percent:.1%}",
                texttemplate='%{label}<br>%{percent:.1%}'
            )
            fig_day_pie.update_layout(height=400)
            fig_day_pie = apply_chart_theme(fig_day_pie)
            st.plotly_chart(fig_day_pie, use_container_width=True)
    else:
        st.info("조회된 요일 데이터가 없습니다.")

# Tab 3: 입금은행 점유율 (전체 / TOP 10 선택 + 컬러바)
with tab_bank:
    if '입금은행' in filtered_df.columns and not filtered_df.empty:
        col_ctrl1, col_ctrl2 = st.columns([1.5, 3])
        with col_ctrl1:
            view_mode = st.radio(
                "조회 범위 선택", 
                options=["전체 입금은행 보기", "TOP 10 입금은행 보기"], 
                horizontal=True,
                label_visibility="collapsed"
            )
        
        bank_df = filtered_df['입금은행'].value_counts().reset_index()
        bank_df.columns = ['입금은행', '거래건수']
        
        if view_mode == "TOP 10 입금은행 보기":
            display_bank_df = bank_df.head(10).copy()
            chart_title = "<b>TOP 10 입금은행 (거래건수)</b>"
        else:
            display_bank_df = bank_df.copy()
            chart_title = f"<b>전체 입금은행 거래건수 (총 {len(display_bank_df)}개 은행)</b>"

        col_c1, col_c2 = st.columns([1.2, 0.8])

        with col_c1:
            fig_bank_bar = px.bar(
                display_bank_df, 
                x='거래건수', 
                y='입금은행', 
                orientation='h',
                title=chart_title,
                color='거래건수',
                color_continuous_scale=PASTEL_BLUE_PURPLE,
                text='거래건수'
            )
            fig_bank_bar.update_traces(
                texttemplate='%{text:,.0f}', 
                textposition='inside',
                insidetextanchor='middle',
                textfont=dict(family="GmarketSans", size=11)
            )
            
            max_v = display_bank_df['거래건수'].max() if not display_bank_df.empty else 100000
            t_vals, t_texts = get_korean_axis_ticks(max_v)
            dynamic_height = max(400, len(display_bank_df) * 32)
            
            fig_bank_bar.update_layout(
                yaxis={'categoryorder': 'total ascending'}, 
                xaxis=dict(tickmode='array', tickvals=t_vals, ticktext=t_texts),
                coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals, ticktext=t_texts),
                height=dynamic_height
            )
            fig_bank_bar = apply_chart_theme(fig_bank_bar)
            st.plotly_chart(fig_bank_bar, use_container_width=True)
            
        with col_c2:
            top_pie_df = bank_df.head(8).copy()
            fig_bank_pie = px.pie(
                top_pie_df, 
                names='입금은행', 
                values='거래건수',
                title="<b>주요 은행별 점유 비중 (상위 8개)</b>", 
                hole=0.48,
                color_discrete_sequence=PASTEL_COLOR_SEQUENCE
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

# Tab 4: 지역별 거래 현황
with tab_sido:
    if '시도' in filtered_df.columns and not filtered_df.empty:
        sido_df = filtered_df['시도'].value_counts().reset_index()
        sido_df.columns = ['지역(시/도)', '거래건수']
        
        fig_sido = px.bar(
            sido_df, x='지역(시/도)', y='거래건수',
            title="<b>전국 시/도별 거래 분포</b>",
            color='거래건수', color_continuous_scale=PASTEL_BLUE_PURPLE,
            text='거래건수'
        )
        fig_sido.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont=dict(family="GmarketSans"))
        
        max_sido = sido_df['거래건수'].max() if not sido_df.empty else 100000
        t_vals_s, t_texts_s = get_korean_axis_ticks(max_sido * 1.1)
        
        fig_sido.update_layout(
            yaxis=dict(tickmode='array', tickvals=t_vals_s, ticktext=t_texts_s),
            coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_s, ticktext=t_texts_s),
            height=400
        )
        fig_sido = apply_chart_theme(fig_sido)
        st.plotly_chart(fig_sido, use_container_width=True)
    else:
        st.info("조회된 지역 데이터가 없습니다.")

# Tab 5: 업종별 분포
with tab_cat:
    if '업종구분' in filtered_df.columns and not filtered_df.empty:
        cat_df = filtered_df['업종구분'].value_counts().reset_index()
        cat_df.columns = ['업종구분', '거래건수']
        
        fig_cat = px.bar(
            cat_df.head(10), x='업종구분', y='거래건수',
            title="<b>TOP 10 업종 분포</b>",
            color='거래건수', color_continuous_scale=PASTEL_MINT_PURPLE,
            text='거래건수'
        )
        fig_cat.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont=dict(family="GmarketSans"))
        
        max_cat = cat_df['거래건수'].max() if not cat_df.empty else 100000
        t_vals_c, t_texts_c = get_korean_axis_ticks(max_cat * 1.1)
        
        fig_cat.update_layout(
            yaxis=dict(tickmode='array', tickvals=t_vals_c, ticktext=t_texts_c),
            coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_c, ticktext=t_texts_c),
            height=400
        )
        fig_cat = apply_chart_theme(fig_cat)
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("조회된 업종 데이터가 없습니다.")

st.markdown("---")

# ---------------------------------------------------------
# 10. 상세 거래 내역 데이터 테이블 (완벽 중앙 정렬 원형 버튼 페이징)
# ---------------------------------------------------------
st.markdown(f"<h3 style='font-size:1.25rem;'>📋 상세 거래 내역 목록 <span style='font-size:0.95rem; color:#64748b; font-weight:500;'>(조회 결과: {len(filtered_df):,} 건)</span></h3>", unsafe_allow_html=True)

display_cols = [
    '최종거래일시', '판매점ID', '상호', '대표자', '명의자명', '통합상태구분',
    '시도', '도로명주소', '업종구분', '입금은행', '입금자', '입금금액', '세부입금구분'
]

valid_cols = [col for col in display_cols if col in filtered_df.columns]

items_per_page = 10
total_items = len(filtered_df)
total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1

if 'curr_page' not in st.session_state:
    st.session_state.curr_page = 1

if st.session_state.curr_page > total_pages:
    st.session_state.curr_page = total_pages
if st.session_state.curr_page < 1:
    st.session_state.curr_page = 1

start_idx = (st.session_state.curr_page - 1) * items_per_page
end_idx = start_idx + items_per_page
page_data = filtered_df[valid_cols].iloc[start_idx:end_idx]

st.dataframe(
    page_data,
    use_container_width=True,
    height=390
)

# --------------------------------------------------
# 완벽 중앙 정렬 & 큰 숫자 줄바꿈 방지 버튼 페이징 (1 2 3 ... › »)
# --------------------------------------------------
page_block_size = 10
start_p = ((st.session_state.curr_page - 1) // page_block_size) * page_block_size + 1
end_p = min(total_pages, start_p + page_block_size - 1)

page_range = list(range(start_p, end_p + 1))
total_btns = len(page_range) + 2

side_spacer = max(1, (24 - total_btns * 2) // 2)
col_structure = [side_spacer] + [1.8] * total_btns + [side_spacer]
btn_cols = st.columns(col_structure)

# 1. 숫자 원형/캡슐 버튼들
for idx, p_num in enumerate(page_range):
    with btn_cols[idx + 1]:
        b_type = "primary" if p_num == st.session_state.curr_page else "secondary"
        if st.button(f"{p_num:,}", key=f"p_btn_{p_num}", type=b_type):
            st.session_state.curr_page = p_num
            st.rerun()

# 2. '›' 다음 10개 블록 이동
with btn_cols[len(page_range) + 1]:
    if st.button("›", key="next_block", disabled=(end_p >= total_pages)):
        st.session_state.curr_page = min(total_pages, end_p + 1)
        st.rerun()

# 3. '»' 맨 끝 이동
with btn_cols[len(page_range) + 2]:
    if st.button("»", key="last_page", disabled=(st.session_state.curr_page == total_pages or total_pages == 0)):
        st.session_state.curr_page = total_pages
        st.rerun()

# 페이지 정보 표기
st.markdown(
    f"<p style='text-align: center; color: #64748b; font-size: 0.9rem; margin-top: 14px; font-family: GmarketSans;'>"
    f"페이지 <b>{st.session_state.curr_page:,}</b> / {total_pages:,} (총 {total_items:,} 건)"
    f"</p>",
    unsafe_allow_html=True
)
