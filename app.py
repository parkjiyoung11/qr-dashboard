import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import gc

# 1. 페이지 설정
st.set_page_config(
    page_title="QR플레이트 입금거래 대시보드", 
    page_icon="💳", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS
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

    .main { background-color: #f8fafc; }
    
    .dashboard-header {
        font-family: 'GmarketSans', sans-serif !important;
        font-size: 2.1rem;
        font-weight: 700 !important;
        color: #0f172a;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .dashboard-subtitle {
        font-family: 'GmarketSans', sans-serif !important;
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 18px;
    }

    .section-bold-title {
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 700 !important;
        color: #0f172a;
    }

    button[data-baseweb="tab"] div {
        font-family: 'GmarketSans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.02rem !important;
    }

    .metric-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 18px 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
        text-align: left;
    }
    .metric-title {
        font-family: 'GmarketSans', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        color: #475569;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'GmarketSans', sans-serif !important;
        font-size: 1.7rem;
        font-weight: 700 !important;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    .metric-unit {
        font-size: 0.92rem;
        font-weight: 500 !important;
        color: #64748b;
        margin-left: 2px;
    }

    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
    }

    hr { border-top: 1px solid #e2e8f0; margin: 18px 0; }

    [data-testid="stFileUploader"] section > div:first-child { display: none !important; }
    [data-testid="stFileUploader"] section {
        padding: 12px 14px !important;
        background-color: #f1f5f9 !important;
        border: 1px dashed #cbd5e1 !important;
        border-radius: 8px !important;
        min-height: 44px !important;
    }

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

PASTEL_COLOR_SEQUENCE = ['#74B9FF', '#A29BFE', '#FFEAA7', '#81ECEC', '#FAB1A0', '#55E6C1', '#70A1FF', '#81D4FA', '#A8E6CF', '#D6A2E8']
PASTEL_BLUE_PURPLE = ['#D6E4FF', '#ADC6FF', '#85A5FF', '#9254DE', '#F759AB']
PASTEL_MINT_PURPLE = ['#E6F7FF', '#BAE7FF', '#91D5FF', '#B37FEB', '#9254DE']

# 3. 데이터 로딩 및 초경량 캐싱
@st.cache_data(max_entries=1)
def get_dataset():
    df = pd.read_parquet('merged_data.parquet')
    
    date_col = next((c for c in ['최종거래일시', '입금일시', '거래일시', '입금일자', '거래일자'] if c in df.columns), None)
    if date_col:
        dt = pd.to_datetime(df[date_col], errors='coerce')
        df['입금일자_dt'] = dt.dt.date
        df['입금연월'] = dt.dt.strftime('%Y-%m').astype(str)
        
        day_names = np.array(['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'])
        day_idx = dt.dt.dayofweek.fillna(0).astype(int).values
        df['요일'] = day_names[day_idx]
    else:
        df['입금일자_dt'] = pd.Timestamp.now().date()
        df['입금연월'] = '2026-01'
        df['요일'] = '월요일'

    if '입금은행' in df.columns:
        bank_map = {
            '006': '006(국민은행(구 한국주택은행))', '030': '030(수협중앙회)',
            6: '006(국민은행(구 한국주택은행))', 30: '030(수협중앙회)',
            '6': '006(국민은행(구 한국주택은행))', '30': '030(수협중앙회)'
        }
        df['입금은행'] = df['입금은행'].replace(bank_map).fillna('미분류').astype(str)

    status_col = next((c for c in ['업체상태', '상태구분', '상태', '영업상태'] if c in df.columns), None)
    if status_col:
        st_arr = df[status_col].astype(str).values
        df['통합상태구분'] = np.where(np.char.find(st_arr, '해지') >= 0, '해지', '정상')
    else:
        df['통합상태구분'] = '정상'

    if '입금금액' in df.columns:
        df['입금금액'] = pd.to_numeric(df['입금금액'], errors='coerce').fillna(0).astype(np.int64)
    else:
        df['입금금액'] = np.int64(0)

    memo_str = df['입금자'].astype(str).values if '입금자' in df.columns else np.array([''] * len(df))
    is_rew = (np.char.find(memo_str, '보상') >= 0) | (np.char.find(memo_str, '리워드') >= 0) | (np.char.find(memo_str, '캐시') >= 0)
    is_th = (df['입금금액'].values > 0) & (df['입금금액'].values % 1000 == 0)

    conds = [is_rew, is_th, df['입금금액'].values > 0]
    choices = ['리워드/보상금 입금', '소비자 정액입금(000단위)', '일반/기타 소액입금']
    df['세부입금구분'] = np.select(conds, choices, default='기타 입금')

    for col in ['시도', '업종구분']:
        if col in df.columns:
            df[col] = df[col].fillna('기타').astype(str)

    gc.collect()
    return df

try:
    df = get_dataset()
except Exception as e:
    st.error(f"데이터 로딩 오류: {e}")
    st.stop()

# 4. 헤더
st.markdown('<div class="dashboard-header">💳 QR플레이트 사업자계좌 입금거래 통합 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">실시간 검색, 월별/요일별 다차원 통계 및 상세 거래 데이터 분석 리포트</div>', unsafe_allow_html=True)

# 5. 사이드바 필터
st.sidebar.markdown("### 🔍 검색 & 핵심 필터")
st.sidebar.markdown("---")

search_store_id = st.sidebar.text_input("🎯 판매점 ID / 상호 검색", value="", placeholder="판매점ID 또는 상호 입력...")
status_options = ['전체', '정상', '해지']
selected_status = st.sidebar.selectbox("🏷️ 판매점 상태구분", options=status_options, index=0)

period_mode = st.sidebar.radio("📅 기간 필터 모드", ["일자별 선택", "월별(연월) 선택"], horizontal=True)

all_valid_d = [d for d in df['입금일자_dt'].dropna().unique()]
min_d = min(all_valid_d) if all_valid_d else pd.Timestamp.now().date()
max_d = max(all_valid_d) if all_valid_d else pd.Timestamp.now().date()
all_months = sorted(list(set(df['입금연월'].dropna())))

if period_mode == "일자별 선택":
    date_range = st.sidebar.date_input("조회 기간 설정", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    selected_months = None
else:
    date_range = None
    selected_months = st.sidebar.multiselect("조회 연월 선택", options=all_months, default=all_months, placeholder="월을 선택하세요")

deposit_detail_options = sorted(list(set(df['세부입금구분'].dropna())))
selected_deposit_details = st.sidebar.multiselect("💵 세부 입금금액 구분", options=deposit_detail_options, default=deposit_detail_options, placeholder="선택하세요")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 세부 항목 필터")

bank_options = sorted(list(set(df['입금은행'].dropna()))) if '입금은행' in df.columns else []
sido_options = sorted(list(set(df['시도'].dropna()))) if '시도' in df.columns else []
category_options = sorted(list(set(df['업종구분'].dropna()))) if '업종구분' in df.columns else []

selected_banks = st.sidebar.multiselect("🏛️ 입금은행", options=bank_options, placeholder="선택하세요")
selected_sido = st.sidebar.multiselect("🗺️ 지역(시/도)", options=sido_options, placeholder="선택하세요")
selected_category = st.sidebar.multiselect("🏢 업종구분", options=category_options, placeholder="선택하세요")

# 6. 필터링 마스크
mask = np.ones(len(df), dtype=bool)

if selected_status != '전체':
    mask &= (df['통합상태구분'].values == selected_status)

if period_mode == "일자별 선택" and date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    mask &= (df['입금일자_dt'].values >= date_range[0]) & (df['입금일자_dt'].values <= date_range[1])
elif period_mode == "월별(연월) 선택" and selected_months:
    mask &= np.isin(df['입금연월'].values, selected_months)

if search_store_id.strip():
    q = search_store_id.strip()
    id_cond = df['판매점ID'].astype(str).str.contains(q).values if '판매점ID' in df.columns else False
    name_cond = df['상호'].astype(str).str.contains(q).values if '상호' in df.columns else False
    mask &= (id_cond | name_cond)

if selected_deposit_details:
    mask &= np.isin(df['세부입금구분'].values, selected_deposit_details)
if selected_banks:
    mask &= np.isin(df['입금은행'].values, selected_banks)
if selected_sido:
    mask &= np.isin(df['시도'].values, selected_sido)
if selected_category:
    mask &= np.isin(df['업종구분'].values, selected_category)

filtered_df = df[mask]

# 7. KPI 카드
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_tx = len(filtered_df)
total_amount = int(filtered_df['입금금액'].sum()) if total_tx > 0 else 0
avg_amount = int(total_amount / total_tx) if total_tx > 0 else 0
unique_stores = filtered_df['판매점ID'].nunique() if '판매점ID' in filtered_df.columns and total_tx > 0 else 0

with kpi1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">📊 총 거래 건수</div><div class="metric-value">{total_tx:,}<span class="metric-unit"> 건</span></div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">💰 총 입금 금액</div><div class="metric-value" style="color:#2563eb;">{total_amount:,}<span class="metric-unit"> 원</span></div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">📈 건당 평균 입금액</div><div class="metric-value" style="color:#059669;">{avg_amount:,}<span class="metric-unit"> 원</span></div></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">🏪 조회 판매점 수</div><div class="metric-value" style="color:#d97706;">{unique_stores:,}<span class="metric-unit"> 개소</span></div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 8. 시각화 탭
st.markdown("<h2 class='section-bold-title' style='font-size: 1.55rem; margin-bottom: 12px;'>📊 거래 현황 다차원 시각화</h2>", unsafe_allow_html=True)
tab_month, tab_day, tab_bank, tab_sido, tab_cat = st.tabs(["📅 월별 입금 추이", "📆 요일별 거래 비중", "🏛️ 입금은행 점유율", "🗺️ 지역별 거래 현황", "🏢 업종별 분포"])

def apply_chart_theme(fig):
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
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

with tab_month:
    if total_tx > 0:
        m_df = filtered_df.groupby('입금연월').agg(거래건수=('입금금액', 'count'), 총입금액=('입금금액', 'sum')).reset_index().sort_values('입금연월')
        fig_m = make_subplots(specs=[[{"secondary_y": True}]])
        fig_m.add_trace(go.Bar(x=m_df['입금연월'], y=m_df['거래건수'], name="거래건수 (건)", marker_color='#85A5FF', text=m_df['거래건수'], texttemplate='%{text:,.0f}', textposition='outside'), secondary_y=False)
        fig_m.add_trace(go.Scatter(x=m_df['입금연월'], y=m_df['총입금액'], name="총 입금액 (원)", mode='lines+markers+text', line=dict(color='#FA8C16', width=3), marker=dict(size=8), text=[f"{v//100000000}억 {abs(v)%100000000//10000}만" if v >= 100000000 else f"{v//10000}만원" for v in m_df['총입금액']], textposition='top center'), secondary_y=True)
        max_tx_v = m_df['거래건수'].max() if not m_df.empty else 100000
        t_vals_m, t_texts_m = get_korean_axis_ticks(max_tx_v * 1.15)
        fig_m.update_layout(title="<b>월별 거래건수 및 총 입금액 추이</b>", yaxis=dict(title="거래건수", tickmode='array', tickvals=t_vals_m, ticktext=t_texts_m), yaxis2=dict(title="총 입금액", showgrid=False), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=420)
        st.plotly_chart(apply_chart_theme(fig_m), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

with tab_day:
    if total_tx > 0:
        col_d1, col_d2 = st.columns([1.1, 0.9])
        day_order = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일']
        d_df = filtered_df.groupby('요일').agg(거래건수=('입금금액', 'count')).reindex(day_order).fillna(0).reset_index()
        with col_d1:
            fig_d = px.bar(d_df, x='요일', y='거래건수', title="<b>요일별 거래건수 분포 (일~토)</b>", color='거래건수', color_continuous_scale=PASTEL_BLUE_PURPLE, text='거래건수')
            fig_d.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            max_d_v = d_df['거래건수'].max()
            t_vals_d, t_texts_d = get_korean_axis_ticks(max_d_v * 1.15)
            fig_d.update_layout(yaxis=dict(tickmode='array', tickvals=t_vals_d, ticktext=t_texts_d), coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_d, ticktext=t_texts_d), height=400)
            st.plotly_chart(apply_chart_theme(fig_d), use_container_width=True)
        with col_d2:
            fig_dp = px.pie(d_df, names='요일', values='거래건수', title="<b>요일별 거래건수 점유 비중</b>", hole=0.48, color_discrete_sequence=PASTEL_COLOR_SEQUENCE)
            fig_dp.update_traces(textinfo='percent+label', texttemplate='%{label}<br>%{percent:.1%}')
            fig_dp.update_layout(height=400)
            st.plotly_chart(apply_chart_theme(fig_dp), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

with tab_bank:
    if total_tx > 0 and '입금은행' in filtered_df.columns:
        col_c1, col_c2 = st.columns([1.2, 0.8])
        b_df = filtered_df['입금은행'].value_counts().reset_index()
        b_df.columns = ['입금은행', '거래건수']
        with col_c1:
            view_mode = st.radio("조회 범위", ["전체 입금은행", "TOP 10 입금은행"], horizontal=True, label_visibility="collapsed")
            disp_b = b_df.head(10) if view_mode == "TOP 10 입금은행" else b_df
            fig_b = px.bar(disp_b, x='거래건수', y='입금은행', orientation='h', title="<b>입금은행별 거래건수</b>", color='거래건수', color_continuous_scale=PASTEL_BLUE_PURPLE, text='거래건수')
            fig_b.update_traces(texttemplate='%{text:,.0f}', textposition='inside', insidetextanchor='middle')
            max_b_v = disp_b['거래건수'].max() if not disp_b.empty else 100000
            t_vals_b, t_texts_b = get_korean_axis_ticks(max_b_v)
            fig_b.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis=dict(tickmode='array', tickvals=t_vals_b, ticktext=t_texts_b), coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_b, ticktext=t_texts_b), height=max(400, len(disp_b)*30))
            st.plotly_chart(apply_chart_theme(fig_b), use_container_width=True)
        with col_c2:
            fig_bp = px.pie(b_df.head(8), names='입금은행', values='거래건수', title="<b>주요 은행별 비중 (TOP 8)</b>", hole=0.48, color_discrete_sequence=PASTEL_COLOR_SEQUENCE)
            fig_bp.update_traces(textinfo='percent', texttemplate='%{percent:.1%}')
            fig_bp.update_layout(height=400)
            st.plotly_chart(apply_chart_theme(fig_bp), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

with tab_sido:
    if total_tx > 0 and '시도' in filtered_df.columns:
        s_df = filtered_df['시도'].value_counts().reset_index()
        s_df.columns = ['지역(시/도)', '거래건수']
        fig_s = px.bar(s_df, x='지역(시/도)', y='거래건수', title="<b>전국 시/도별 거래 분포</b>", color='거래건수', color_continuous_scale=PASTEL_BLUE_PURPLE, text='거래건수')
        fig_s.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        max_s_v = s_df['거래건수'].max()
        t_vals_s, t_texts_s = get_korean_axis_ticks(max_s_v * 1.1)
        fig_s.update_layout(yaxis=dict(tickmode='array', tickvals=t_vals_s, ticktext=t_texts_s), coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_s, ticktext=t_texts_s), height=400)
        st.plotly_chart(apply_chart_theme(fig_s), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

with tab_cat:
    if total_tx > 0 and '업종구분' in filtered_df.columns:
        c_df = filtered_df['업종구분'].value_counts().reset_index()
        c_df.columns = ['업종구분', '거래건수']
        fig_c = px.bar(c_df.head(10), x='업종구분', y='거래건수', title="<b>TOP 10 업종 분포</b>", color='거래건수', color_continuous_scale=PASTEL_MINT_PURPLE, text='거래건수')
        fig_c.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        max_c_v = c_df['거래건수'].max()
        t_vals_c, t_texts_c = get_korean_axis_ticks(max_c_v * 1.1)
        fig_c.update_layout(yaxis=dict(tickmode='array', tickvals=t_vals_c, ticktext=t_texts_c), coloraxis_colorbar=dict(title="거래건수", tickmode='array', tickvals=t_vals_c, ticktext=t_texts_c), height=400)
        st.plotly_chart(apply_chart_theme(fig_c), use_container_width=True)
    else:
        st.info("조회된 데이터가 없습니다.")

st.markdown("---")

# 9. 테이블 & 페이징
st.markdown(f"<h3 style='font-size:1.25rem;'>📋 상세 거래 내역 목록 <span style='font-size:0.95rem; color:#64748b; font-weight:500;'>(조회 결과: {total_tx:,} 건)</span></h3>", unsafe_allow_html=True)

display_cols = ['최종거래일시', '판매점ID', '상호', '대표자', '명의자명', '통합상태구분', '시도', '도로명주소', '업종구분', '입금은행', '입금자', '입금금액', '세부입금구분']
valid_cols = [c for c in display_cols if c in filtered_df.columns]

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

st.markdown(f"<p style='text-align: center; color: #64748b; font-size: 0.9rem; margin-top: 14px; font-family: GmarketSans;'>페이지 <b>{st.session_state.curr_page:,}</b> / {total_pages:,} (총 {total_tx:,} 건)</p>", unsafe_allow_html=True)
