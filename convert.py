import pandas as pd

print("1. 엑셀 파일을 읽는 중입니다... (약 10~20초 소요)")
# 자금거래 엑셀 불러오기
df_tx = pd.read_excel('자금거래.xlsx')

# 판매점 기본정보 불러오기
df_store = pd.read_excel('판매점_판매점기본정보_20260824.xlsx')

# 판매점기본정보 첫 줄이 컬럼명인 경우 정제
if '판매점_판매점기본정보' in df_store.columns:
    df_store.columns = df_store.iloc[0]
    df_store = df_store[1:].reset_index(drop=True)

print("2. 데이터 가공 및 결합 중...")
# 날짜 컬럼 형변환
df_tx['최종거래일시'] = pd.to_datetime(df_tx['최종거래일시'])
df_tx['입금일자'] = df_tx['최종거래일시'].dt.date

# 매칭에 필요한 핵심 컬럼만 추출 (용량 줄이기)
store_cols = ['판매점ID', '상호', '명의자명', '도로명주소', '시도', '업종구분']
# 판매점ID 타입 통일
df_tx['판매점ID'] = df_tx['판매점ID'].astype(str)
df_store['판매점ID'] = df_store['판매점ID'].astype(str)

df_store_sub = df_store[store_cols].drop_duplicates(subset=['판매점ID'])

# 64만건 데이터 합치기 (LEFT JOIN)
df_merged = pd.merge(df_tx, df_store_sub, on='판매점ID', how='left')

# 입금금액 필터용 기준 컬럼 생성 (000 단위 구분)
df_merged['입금구분'] = df_merged['입금금액'].apply(
    lambda x: '소비자 입금(000단위)' if x % 1000 == 0 and x > 0 else '개인 입출금(기타)'
)

print("3. 초고속 압축 데이터(parquet)로 저장 중...")
df_merged.to_parquet('merged_data.parquet', index=False)
print("🎉 성공! merged_data.parquet 파일이 생성되었습니다.")