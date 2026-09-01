import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import datetime
import io

# 1. 페이지 설정
st.set_page_config(
    page_title="QR플레이트 입금거래 대시보드", 
    page_icon="💳", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 토스(Toss) 스타일 프리미엄 UI CSS
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

    html, body, [class*="css"], .stMarkdown p, label, select {
        font-family: 'GmarketSans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #191F28;
    }

    .main { background-color: #F2F4F6; }

    .toss-header {
        font-size: 2.2rem;
        font-weight: 700 !important;
        color: #191F28;
        margin-bottom: 4px;
        letter-spacing: -0.6px;
    }

    .toss-subtitle {
        color: #8B95A1;
        font-size: 1.0rem;
        font-weight: 500;
        margin-bottom: 20px;
    }

    .toss-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 22px 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(0, 0, 0, 0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .toss-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }

    .toss-card-title {
        font-size: 0.95rem;
        font-weight: 500;
        color: #6B7684;
        margin-bottom: 8px;
    }

    .toss-card-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #191F28;
        letter-spacing: -0.5px;
    }

    .toss-card-unit {
        font-size: 1.05rem;
        font-weight: 500;
        color: #8B95A1;
        margin-left: 2px;
    }

    .toss-insight-box {
        background: linear-gradient(135deg, #E8F3FF 0%, #F4F7FF 100%);
        border-radius: 16px;
        padding: 16px 20px;
        border: 1px solid #D0E4FF;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    button[data-baseweb="tab"] {
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.0rem !important;
        color: #6B7684 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #3182F6 !important;
    }

    [data-testid="stFileUploader"] section > div:first-child { display: none !important; }
    [data-testid="stFileUploader"] section {
        padding: 14px 16px !important;
        background-color: #FFFFFF !important;
        border: 1px dashed #D1D6DB !important;
        border-radius: 14px !important;
    }

    div[data-testid="stDownloadButton"] button {
        border-radius: 12px !important;
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        padding: 6px 16px !important;
        border: none !important;
        background-color: #E8F3FF !important;
        color: #1B64DA !important;
        transition: all 0.2s;
    }
    div[data-testid="stDownloadButton"] button:hover {
        background-color: #D0E4FF !important;
        color: #0E49B5 !important;
    }

    div[data-testid="stHorizontalBlock"] button[kind="secondary"],
    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        min-width: 38px !important;
        width: auto !important;
        height: 38px !important;
        min-height: 38px !important;
        border-radius: 19px !important;
        padding: 0 10px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-family: 'GmarketSans', sans-serif !important;
        font-size: 0.88rem !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        border: 1px solid #E5E8EB !important;
        background-color: #FFFFFF !important;
        color: #4E5968 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        margin: 0 auto !important;
    }

    div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        background-color: #F2F4F6 !important;
        color: #191F28 !important;
    }

    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background-color: #3182F6 !important;
        color: #FFFFFF !important;
        border-color: #3182F6 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 10px rgba(49, 130, 246, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# 테마 컬러
TOSS_BLUE = '#3182F6'
TOSS_GRADIENT_BLUES = ['#E8F3FF', '#B8D7FF', '#74ABFF', '#3182F6', '#1B64DA']
TOSS_PASTEL_SEQUENCE = ['#3182F6', '#20C997', '#FFB300', '#F06595', '#845EF7', '#339AF0', '#51CF66', '#FCC419', '#FF922B']

def convert_df_to_excel(df_to_export):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_export.to_excel(writer, index=False, sheet_name='데이터')
    return output.getvalue()

# 3. 데이터 로딩 및 전처리
@st.cache_data
def get_clean_data():
    df = pd.read_parquet('merged_data.parquet')

    date_col = next((c for c in ['최종거래일시', '입금일시', '거래일시', '입금일자', '거래일자'] if c in df.columns), None)
    if date_col:
        dt = pd.to_datetime(df[date_col], errors='coerce')
        dt_valid = dt.dropna()
        def_date = dt_valid.iloc[0] if len(dt_valid) > 0 else pd.Timestamp.now()
        dt = dt.fillna(def_date)
        
        df['입금일자_dt'] = dt.dt.date
        df['입금연월'] = dt.dt.strftime('%Y년 %m월')
        
        day_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        df['요일'] = dt.dt.dayofweek.map(lambda x: day_names[int(x)] if pd.notnull(x) else '월요일')
    else:
        now_d = datetime.date.today()
        df['입금일자_dt'] = now_d
        df['입금연월'] = now_d.strftime('%Y년 %m월')
        df['요일'] = '월요일'

    if '입금은행' in df.columns:
        bank_map = {
            '006': '006(국민은행(구 한국주택은행))', '030': '030(수협중앙회)',
            6: '006(국민은행(구 한국주택은행))', 30: '030(수협중앙회)',
            '6': '006(국민은행(구 한국주택은행))', '30': '030(수협중앙회)'
        }
        df['입금은행'] = df['입금은행'].astype(str).replace(bank_map).fillna('미분류')
    else:
        df['입금은행'] = '미분류'

    status_col = next((c for c in ['업체상태', '상태구분', '상태', '영업상태'] if c in df.columns), None)
    if status_col:
        is_cancel = df[status_col].astype(str).str.contains('해지|폐업|중단', regex=True, na=False)
        df['통합상태구분'] = np.where(is_cancel, '해지', '정상')
    else:
        df['통합상태구분'] = '정상'

    if '입금금액' in df.columns:
        df['입금금액'] = pd.to_numeric(df['입금금액'], errors='coerce').fillna(0).astype('int64')
    else:
        df['입금금액'] = 0

    df['금액규모구분'] = np.where(df['입금금액'] > 100000, '10만원 초과', '10만원 이하')
    df['정액단위구분'] = np.where((df['입금금액'] > 0) & (df['입금금액'] % 1000 == 0), '000단위 정액입금', '000단위 아님')

    conds = [
        (df['입금금액'] > 0) & (df['입금금액'] % 1000 == 0),
        (df['입금금액'] == 1),
        (df['입금금액'] > 0) & (df['입금금액'] % 1000 != 0)
    ]
    choices = [
        '000단위 정액입금',
        '리워드 입금 (1원)',
        '일반 비정액 소액입금'
    ]
    df['세부입금구분'] = np.select(conds, choices, default='기타 입금')

    for col in ['시도', '업종구분']:
        if col in df.columns:
            df[col] = df[col].fillna('기타').astype(str)

    return df

try:
    df = get_clean_data()
except Exception as e:
    st.error(f"데이터 파일 읽기 오류: {e}")
    st.stop()

# 4. 헤더 영역
st.markdown('<div class="toss-header">💳 QR플레이트 사업자계좌 입금거래 통합 리포트</div>', unsafe_allow_html=True)
st.markdown('<div class="toss-subtitle">실시간 검색, 월별/요일별 다차원 통계 및 상세 거래 데이터 분석 리포트</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. 사이드바 검색 및 계층형 필터
# ---------------------------------------------------------
st.sidebar.markdown("### 🔍 검색 & 기본 필터")
st.sidebar.markdown("---")

search_store_id = st.sidebar.text_input("🎯 판매점 ID / 상호 검색", value="", placeholder="판매점ID 또는 상호 입력...")
status_options = ['전체', '정상', '해지']
selected_status = st.sidebar.selectbox("🏷️ 판매점 상태구분", options=status_options, index=0)

period_mode = st.sidebar.radio("📅 기간 필터 모드", ["일자별 선택", "월별(연월) 선택"], horizontal=True)

min_d = df['입금일자_dt'].min()
max_d = df['입금일자_dt'].max()
all_months = sorted(list(df['입금연월'].unique()))

if period_mode == "일자별 선택":
    date_range = st.sidebar.date_input("조회 기간 설정", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    selected_months = None
else:
    date_range = None
    selected_months = st.sidebar.multiselect("조회 연월 선택", options=all_months, default=all_months, placeholder="월을 선택하세요")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💵 금액 규모 & 단위별 필터")

selected_scale = st.sidebar.radio("1️⃣ 금액 규모 선택", ["전체 금액", "10만원 초과만", "10만원 이하만"], horizontal=True)
selected_unit = st.sidebar.radio("2️⃣ 금액 단위 선택", ["전체 단위", "000단위 정액입금", "000단위 아님"], horizontal=True)

if selected_unit == "000단위 아님":
    reward_option = st.sidebar.selectbox(
        "↳ 세부 구분 (리워드/비정액)",
        ["전체 (000단위 아님)", "리워드 입금 (1원)", "일반 비정액 소액입금 (1원 제외)"]
    )
else:
    reward_option = None

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 세부 항목 필터")

bank_options = sorted(list(df['입금은행'].unique())) if '입금은행' in df.columns else []
sido_options = sorted(list(df['시도'].unique())) if '시도' in df.columns else []
category_options = sorted(list(df['업종구분'].unique())) if '업종구분' in df.columns else []

selected_banks = st.sidebar.multiselect("🏛️ 입금은행", options=bank_options, placeholder="선택하세요")
selected_sido = st.sidebar.multiselect("🗺️ 지역(시/도)", options=sido_options, placeholder="선택하세요")
selected_category = st.sidebar.multiselect("🏢 업종구분", options=category_options, placeholder="선택하세요")

# --- 필터링 실행 ---
filtered_df = df.copy()

if selected_status != '전체':
    filtered_df = filtered_df[filtered_df['통합상태구분'] == selected_status]

if period_mode == "일자별 선택" and date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    filtered_df = filtered_df[(filtered_df['입금일자_dt'] >= date_range[0]) & (filtered_df['입금일자_dt'] <= date_range[1])]
elif period_mode == "월별(연월) 선택" and selected_months:
    filtered_df = filtered_df[filtered_df['입금연월'].isin(selected_months)]

if search_store_id.strip():
    q = search_store_id.strip()
    id_cond = filtered_df['판매점ID'].astype(str).str.contains(q, na=False) if '판매점ID' in filtered_df.columns else False
    name_cond = filtered_df['상호'].astype(str).str.contains(q, na=False) if '상호' in filtered_df.columns else False
    filtered_df = filtered_df[id_cond | name_cond]

if selected_scale == "10만원 초과만":
    filtered_df = filtered_df[filtered_df['금액규모구분'] == '10만원 초과']
elif selected_scale == "10만원 이하만":
    filtered_df = filtered_df[filtered_df['금액규모구분'] == '10만원 이하']

if selected_unit == "000단위 정액입금":
    filtered_df = filtered_df[filtered_df['정액단위구분'] == '000단위 정액입금']
elif selected_unit == "000단위 아님":
    filtered_df = filtered_df[filtered_df['정액단위구분'] == '000단위 아님']
    if reward_option == "리워드 입금 (1원)":
        filtered_df = filtered_df[filtered_df['세부입금구분'] == '리워드 입금 (1원)']
    elif reward_option == "일반 비정액 소액입금 (1원 제외)":
        filtered_df = filtered_df[filtered_df['세부입금구분'] == '일반 비정액 소액입금']

if selected_banks:
    filtered_df = filtered_df[filtered_df['입금은행'].isin(selected_banks)]
if selected_sido:
    filtered_df = filtered_df[filtered_df['시도'].isin(selected_sido)]
if selected_category:
    filtered_df = filtered_df[filtered_df['업종구분'].isin(selected_category)]

# ---------------------------------------------------------
# 6. 상단 토스형 KPI 카드 영역
# ---------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_tx = len(filtered_df)
total_amount = int(filtered_df['입금금액'].sum()) if total_tx > 0 else 0
avg_amount = int(total_amount / total_tx) if total_tx > 0 else 0
unique_stores = filtered_df['판매점ID'].nunique() if '판매점ID' in filtered_df.columns and total_tx > 0 else 0

with kpi1:
    st.markdown(f'''
        <div class="toss-card">
            <div class="toss-card-title">총 거래 건수</div>
            <div class="toss-card-value">{total_tx:,}<span class="toss-card-unit"> 건</span></div>
        </div>
    ''', unsafe_allow_html=True)

with kpi2:
    st.markdown(f'''
        <div class="toss-card">
            <div class="toss-card-title">총 입금 금액</div>
            <div class="toss-card-value" style="color:#3182F6;">{total_amount:,}<span class="toss-card-unit"> 원</span></div>
        </div>
    ''', unsafe_allow_html=True)

with kpi3:
    st.markdown(f'''
        <div class="toss-card">
            <div class="toss-card-title">건당 평균 입금액</div>
            <div class="toss-card-value" style="color:#20C997;">{avg_amount:,}<span class="toss-card-unit"> 원</span></div>
        </div>
    ''', unsafe_allow_html=True)

with kpi4:
    st.markdown(f'''
        <div class="toss-card">
            <div class="toss-card-title">조회 판매점 수</div>
            <div class="toss-card-value" style="color:#FFB300;">{unique_stores:,}<span class="toss-card-unit"> 곳</span></div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. 스마트 브리핑 배너
# ---------------------------------------------------------
if total_tx > 0:
    reward_cnt = len(filtered_df[filtered_df['세부입금구분'] == '리워드 입금 (1원)'])
    over100k_cnt = len(filtered_df[filtered_df['금액규모구분'] == '10만원 초과'])
    st.markdown(f"""
        <div class="toss-insight-box">
            <span style="font-size:1.3rem;">💡</span>
            <span style="font-size:0.95rem; color:#1B64DA; line-height:1.4;">
                현재 조건에서 <b>10만원 초과 고액 거래는 {over100k_cnt:,}건</b>이며, <b>1원 리워드 입금은 {reward_cnt:,}건</b>입니다.
            </span>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. 다차원 시각화 차트 섹션
# ---------------------------------------------------------
st.markdown("<h2 class='section-bold-title' style='font-size: 1.45rem; margin-bottom: 12px;'>📊 거래 현황 다차원 시각화</h2>", unsafe_allow_html=True)
tab_month, tab_day, tab_amount, tab_bank, tab_sido, tab_cat = st.tabs([
    "📅 월별 입금 추이", 
    "📆 요일별 거래 비중", 
    "💵 금액구분/단위 분석",
    "🏛️ 입금은행 점유율", 
    "🗺️ 지역별 거래 현황", 
    "🏢 업종별 분포"
])

def apply_toss_theme(fig):
    fig.update_layout(
        plot_bgcolor="#FFFFFF", 
        paper_bgcolor="#FFFFFF",
        font=dict(family="GmarketSans, sans-serif", size=12, color="#4E5968"),
        title_font=dict(family="GmarketSans, sans-serif", size=15, color="#191F28"),
        margin=dict(l=20, r=20, t=45, b=20),
        hoverlabel=dict(bgcolor="#191F28", font_size=12, font_family="GmarketSans", font_color="#FFFFFF")
    )
    return fig

def get_korean_axis_ticks(max_val):
    if max_val <= 0: return [0], ["0"]
    step = max(10000, int(max_val // 4))
    step = int(math.ceil(step / 10000.0) * 10000)
    vals = list(range(0, int(max_val) + step, step))
    texts = ["0" if v == 0 else (f"{v//10000}만" if v >= 10000 else f"{v:,}") for v in vals]
    return vals, texts

def get_korean_amount_ticks(max_val):
    if max_val <= 0: return [0], ["0원"]
    step = max(100000000, int(max_val // 4))
    step = int(math.ceil(step / 100000000.0) * 100000000)
    vals = list(range(0, int(max_val) + step, step))
    texts = ["0원" if v == 0 else f"{v//100000000}억원" for v in vals]
    return vals, texts

# Tab 1: 월별 입금 추이
with tab_month:
    if total_tx > 0:
        m_df = filtered_df.groupby('입금연월').agg(거래건수=('입금금액', 'count'), 총입금액=('입금금액', 'sum')).reset_index().sort_values('입금연월')
        
        col_m_head1, col_m_head2 = st.columns([4, 1])
        with col_m_head2:
            excel_m = convert_df_to_excel(m_df)
            st.download_button(
                label="📥 월별 집계 엑셀",
                data=excel_m,
                file_name="월별_입금거래_집계.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="down_btn_month"
            )

        fig_m = make_subplots(specs=[[{"secondary_y": True}]])
        fig_m.add_trace(
            go.Bar(
                x=m_df['입금연월'].astype(str), 
                y=m_df['거래건수'], 
                name="거래건수 (건)", 
                marker=dict(color='#74ABFF', line=dict(color='#3182F6', width=1.5)),
                text=m_df['거래건수'], 
                texttemplate='%{text:,.0f}건', 
                textposition='outside',
                width=0.45
            ), 
            secondary_y=False
        )
        fig_m.add_trace(
            go.Scatter(
                x=m_df['입금연월'].astype(str), 
                y=m_df['총입금액'], 
                name="총 입금액 (원)", 
                mode='lines+markers+text', 
                line=dict(color='#FF922B', width=3.5), 
                marker=dict(size=10, color='#FF922B', line=dict(color='#FFFFFF', width=2)), 
                text=[f"{v//100000000}억 {abs(v)%100000000//10000}만" if v >= 100000000 else f"{v//10000}만원" for v in m_df['총입금액']], 
                textposition='top center'
            ), 
            secondary_y=True
        )

        max_tx_v = m_df['거래건수'].max() if not m_df.empty else 100000
        t_vals_m, t_texts_m = get_korean_axis_ticks(max_tx_v * 1.25)
        max_amt_v = m_df['총입금액'].max() if not m_df.empty else 1000000000
        a_vals_m, a_texts_m = get_korean_amount_ticks(max_amt_v * 1.3)

        fig_m.update_layout(
            title="<b>월별 거래건수 및 총 입금액 추이</b>", 
            xaxis=dict(type='category', title=""),
            yaxis=dict(title="거래건수", tickmode='array', tickvals=t_vals_m, ticktext=t_texts_m, gridcolor="#F2F4F6"), 
            yaxis2=dict(title="총 입금액", tickmode='array', tickvals=a_vals_m, ticktext=a_texts_m, showgrid=False), 
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), 
            height=430
        )
        st.plotly_chart(apply_toss_theme(fig_m), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

# Tab 2: 요일별 거래 비중
with tab_day:
    if total_tx > 0:
        day_order = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일']
        d_df = filtered_df.groupby('요일').agg(거래건수=('입금금액', 'count'), 총입금액=('입금금액', 'sum')).reindex(day_order).fillna(0).reset_index()
        
        col_d_head1, col_d_head2 = st.columns([4, 1])
        with col_d_head2:
            excel_d = convert_df_to_excel(d_df)
            st.download_button(
                label="📥 요일별 집계 엑셀",
                data=excel_d,
                file_name="요일별_입금거래_집계.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="down_btn_day"
            )

        col_d1, col_d2 = st.columns([1.1, 0.9])
        with col_d1:
            fig_d = px.bar(d_df, x='요일', y='거래건수', title="<b>요일별 거래건수 분포</b>", color='거래건수', color_continuous_scale=TOSS_GRADIENT_BLUES, text='거래건수')
            fig_d.update_traces(texttemplate='%{text:,.0f}건', textposition='outside')
            max_d_v = d_df['거래건수'].max()
            t_vals_d, t_texts_d = get_korean_axis_ticks(max_d_v * 1.2)
            fig_d.update_layout(xaxis=dict(type='category'), yaxis=dict(tickmode='array', tickvals=t_vals_d, ticktext=t_texts_d, gridcolor="#F2F4F6"), coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_d, ticktext=t_texts_d), height=400)
            st.plotly_chart(apply_toss_theme(fig_d), use_container_width=True)

        with col_d2:
            fig_dp = px.pie(d_df, names='요일', values='거래건수', title="<b>요일별 점유 비중</b>", hole=0.55, color_discrete_sequence=TOSS_PASTEL_SEQUENCE)
            fig_dp.update_traces(textinfo='percent+label', texttemplate='%{label}<br>%{percent:.1%}', hovertemplate="<b>%{label}</b><br>거래건수: %{value:,.0f}건<br>비중: %{percent:.1%}")
            fig_dp.update_layout(height=400)
            st.plotly_chart(apply_toss_theme(fig_dp), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

# Tab 3: 금액구분/단위 분석
with tab_amount:
    if total_tx > 0:
        col_amt1, col_amt2 = st.columns(2)
        
        with col_amt1:
            scale_df = filtered_df['금액규모구분'].value_counts().reset_index()
            scale_df.columns = ['금액규모', '거래건수']
            fig_scale = px.pie(
                scale_df, 
                names='금액규모', 
                values='거래건수', 
                title="<b>10만원 초과 vs 10만원 이하 비중</b>", 
                hole=0.55,
                color_discrete_sequence=['#3182F6', '#B8D7FF']
            )
            fig_scale.update_traces(textinfo='percent+label', texttemplate='%{label}<br>%{percent:.1%}')
            fig_scale.update_layout(height=400)
            st.plotly_chart(apply_toss_theme(fig_scale), use_container_width=True)

        with col_amt2:
            detail_df = filtered_df['세부입금구분'].value_counts().reset_index()
            detail_df.columns = ['세부입금구분', '거래건수']
            fig_detail = px.bar(
                detail_df, 
                x='세부입금구분', 
                y='거래건수', 
                title="<b>정액(000단위) vs 리워드(1원) vs 비정액 분포</b>",
                color='세부입금구분',
                color_discrete_sequence=TOSS_PASTEL_SEQUENCE,
                text='거래건수'
            )
            fig_detail.update_traces(texttemplate='%{text:,.0f}건', textposition='outside')
            max_dt_v = detail_df['거래건수'].max()
            t_vals_dt, t_texts_dt = get_korean_axis_ticks(max_dt_v * 1.2)
            fig_detail.update_layout(xaxis=dict(type='category'), yaxis=dict(tickmode='array', tickvals=t_vals_dt, ticktext=t_texts_dt, gridcolor="#F2F4F6"), showlegend=False, height=400)
            st.plotly_chart(apply_toss_theme(fig_detail), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

# Tab 4: 입금은행 점유율
with tab_bank:
    if total_tx > 0 and '입금은행' in filtered_df.columns:
        b_df = filtered_df.groupby('입금은행').agg(거래건수=('입금금액', 'count'), 총입금액=('입금금액', 'sum')).reset_index().sort_values('거래건수', ascending=False)
        
        col_ctrl1, col_ctrl2 = st.columns([3, 1])
        with col_ctrl1:
            view_mode = st.radio("조회 범위", ["TOP 10 입금은행", "전체 입금은행"], horizontal=True, label_visibility="collapsed")
        with col_ctrl2:
            excel_b = convert_df_to_excel(b_df)
            st.download_button(
                label="📥 은행별 집계 엑셀",
                data=excel_b,
                file_name="입금은행별_거래집계.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="down_btn_bank"
            )

        disp_b = b_df.head(10) if view_mode == "TOP 10 입금은행" else b_df
        col_c1, col_c2 = st.columns([1.2, 0.8])
        with col_c1:
            fig_b = px.bar(disp_b, x='거래건수', y='입금은행', orientation='h', title=f"<b>{view_mode}별 거래건수</b>", color='거래건수', color_continuous_scale=TOSS_GRADIENT_BLUES, text='거래건수')
            fig_b.update_traces(texttemplate='%{text:,.0f}건', textposition='inside', insidetextanchor='middle')
            max_b_v = disp_b['거래건수'].max() if not disp_b.empty else 100000
            t_vals_b, t_texts_b = get_korean_axis_ticks(max_b_v)
            fig_b.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis=dict(tickmode='array', tickvals=t_vals_b, ticktext=t_texts_b, gridcolor="#F2F4F6"), coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_b, ticktext=t_texts_b), height=max(400, len(disp_b)*32))
            st.plotly_chart(apply_toss_theme(fig_b), use_container_width=True)

        with col_c2:
            fig_bp = px.pie(b_df.head(8), names='입금은행', values='거래건수', title="<b>주요 은행 점유 비중 (TOP 8)</b>", hole=0.55, color_discrete_sequence=TOSS_PASTEL_SEQUENCE)
            fig_bp.update_traces(textinfo='percent', texttemplate='%{percent:.1%}', hovertemplate="<b>%{label}</b><br>거래건수: %{value:,.0f}건<br>비중: %{percent:.1%}")
            fig_bp.update_layout(height=400)
            st.plotly_chart(apply_toss_theme(fig_bp), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

# Tab 5: 지역별 거래 현황
with tab_sido:
    if total_tx > 0 and '시도' in filtered_df.columns:
        s_df = filtered_df.groupby('시도').agg(거래건수=('입금금액', 'count'), 총입금액=('입금금액', 'sum')).reset_index().sort_values('거래건수', ascending=False)
        s_df.columns = ['지역(시/도)', '거래건수', '총입금액']
        
        col_s_head1, col_s_head2 = st.columns([4, 1])
        with col_s_head2:
            excel_s = convert_df_to_excel(s_df)
            st.download_button(
                label="📥 지역별 집계 엑셀",
                data=excel_s,
                file_name="지역별_입금거래_집계.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="down_btn_sido"
            )

        fig_s = px.bar(s_df, x='지역(시/도)', y='거래건수', title="<b>전국 시/도별 거래 분포</b>", color='거래건수', color_continuous_scale=TOSS_GRADIENT_BLUES, text='거래건수')
        fig_s.update_traces(texttemplate='%{text:,.0f}건', textposition='outside')
        max_s_v = s_df['거래건수'].max()
        t_vals_s, t_texts_s = get_korean_axis_ticks(max_s_v * 1.2)
        fig_s.update_layout(xaxis=dict(type='category'), yaxis=dict(tickmode='array', tickvals=t_vals_s, ticktext=t_texts_s, gridcolor="#F2F4F6"), coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_s, ticktext=t_texts_s), height=400)
        st.plotly_chart(apply_toss_theme(fig_s), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

# Tab 6: 업종별 분포
with tab_cat:
    if total_tx > 0 and '업종구분' in filtered_df.columns:
        c_df = filtered_df.groupby('업종구분').agg(거래건수=('입금금액', 'count'), 총입금액=('입금금액', 'sum')).reset_index().sort_values('거래건수', ascending=False)
        
        col_c_head1, col_c_head2 = st.columns([4, 1])
        with col_c_head2:
            excel_c = convert_df_to_excel(c_df)
            st.download_button(
                label="📥 업종별 집계 엑셀",
                data=excel_c,
                file_name="업종별_입금거래_집계.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="down_btn_cat"
            )

        fig_c = px.bar(c_df.head(10), x='업종구분', y='거래건수', title="<b>TOP 10 업종 분포</b>", color='거래건수', color_continuous_scale=TOSS_GRADIENT_BLUES, text='거래건수')
        fig_c.update_traces(texttemplate='%{text:,.0f}건', textposition='outside')
        max_c_v = c_df['거래건수'].max()
        t_vals_c, t_texts_c = get_korean_axis_ticks(max_c_v * 1.2)
        fig_c.update_layout(xaxis=dict(type='category'), yaxis=dict(tickmode='array', tickvals=t_vals_c, ticktext=t_texts_c, gridcolor="#F2F4F6"), coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_c, ticktext=t_texts_c), height=400)
        st.plotly_chart(apply_toss_theme(fig_c), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

st.markdown("---")

# ---------------------------------------------------------
# 9. 상세 거래 내역 데이터 테이블
# ---------------------------------------------------------
display_cols = ['최종거래일시', '판매점ID', '상호', '대표자', '명의자명', '통합상태구분', '금액규모구분', '시도', '도로명주소', '업종구분', '입금은행', '입금자', '입금금액', '세부입금구분']
valid_cols = [c for c in display_cols if c in filtered_df.columns]

col_tbl_head1, col_tbl_head2 = st.columns([3, 1.2])
with col_tbl_head1:
    st.markdown(f"<h3 style='font-size:1.25rem; margin-top:6px;'>📋 상세 거래 내역 목록 <span style='font-size:0.95rem; color:#8B95A1; font-weight:500;'>(조회 결과: {total_tx:,} 건)</span></h3>", unsafe_allow_html=True)

with col_tbl_head2:
    if total_tx > 0:
        csv_data = filtered_df[valid_cols].to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 필터 내역 CSV 다운로드",
            data=csv_data,
            file_name=f"상세거래내역_{datetime.date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="down_btn_table"
        )

items_per_page = 10
total_pages = math.ceil(total_tx / items_per_page) if total_tx > 0 else 1

if 'curr_page' not in st.session_state:
    st.session_state.curr_page = 1
if st.session_state.curr_page > total_pages:
    st.session_state.curr_page = total_pages
if st.session_state.curr_page < 1:
    st.session_state.curr_page = 1

start_idx = (st.session_state.curr_page - 1) * items_per_page
end_idx = start_idx + items_per_page

st.dataframe(filtered_df[valid_cols].iloc[start_idx:end_idx], use_container_width=True, height=390)

# 페이지네이션
page_block_size = 10
start_p = ((st.session_state.curr_page - 1) // page_block_size) * page_block_size + 1
end_p = min(total_pages, start_p + page_block_size - 1)
page_range = list(range(start_p, end_p + 1))
total_btns = len(page_range) + 2

side_spacer = max(1, (24 - total_btns * 2) // 2)
btn_cols = st.columns([side_spacer] + [1.8] * total_btns + [side_spacer])

for idx, p_num in enumerate(page_range):
    with btn_cols[idx + 1]:
        b_type = "primary" if p_num == st.session_state.curr_page else "secondary"
        if st.button(f"{p_num:,}", key=f"p_btn_{p_num}", type=b_type):
            st.session_state.curr_page = p_num
            st.rerun()

with btn_cols[len(page_range) + 1]:
    if st.button("›", key="next_block", disabled=(end_p >= total_pages)):
        st.session_state.curr_page = min(total_pages, end_p + 1)
        st.rerun()

with btn_cols[len(page_range) + 2]:
    if st.button("»", key="last_page", disabled=(st.session_state.curr_page == total_pages or total_pages == 0)):
        st.session_state.curr_page = total_pages
        st.rerun()

st.markdown(f"<p style='text-align: center; color: #8B95A1; font-size: 0.9rem; margin-top: 14px; font-family: GmarketSans;'>페이지 <b>{st.session_state.curr_page:,}</b> / {total_pages:,} (총 {total_tx:,} 건)</p>", unsafe_allow_html=True)
