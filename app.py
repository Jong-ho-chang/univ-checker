import streamlit as st
import pandas as pd

# 데이터 불러오기 (엑셀 파일은 저장소 루트에 있어야 함)
df = pd.read_excel("univ_data.xlsx")

st.set_page_config(page_title="대학 지원 가능성 조회", layout="wide")
st.title("🎓 대학 지원 가능성 조회 프로그램")

# 사용자 성적 구간 입력 (슬라이더 사용)
st.subheader("🎯 성적 범위 설정")
min_score, max_score = st.slider(
    "성적 범위를 설정하세요 (예: 1.0 ~ 2.5)",
    min_value=0.0, max_value=9.0, value=(1.0, 2.5), step=0.05
)

# ±5% 확장 범위 계산
lower_bound = min_score * 0.95
upper_bound = max_score * 1.05
st.write(f"±5% 적용된 실제 검색 범위: {lower_bound:.2f} ~ {upper_bound:.2f}")

# 필터 옵션 구성
df_sorted = df.sort_values(by='성적')
region_list = ["전체"] + sorted(df_sorted['지역'].dropna().unique().tolist())
type_list = ["전체"] + sorted(df_sorted['전형구분'].dropna().unique().tolist())
major_list = ["전체"] + sorted(df_sorted['모집단위'].dropna().unique().tolist())

selected_region = st.selectbox("지역 선택", region_list)
selected_type = st.selectbox("전형구분 선택", type_list)
selected_major = st.selectbox("모집단위 선택", major_list)

# 필터링 조건 적용
filtered_df = df.copy()
if selected_region != "전체":
    filtered_df = filtered_df[filtered_df['지역'] == selected_region]
if selected_type != "전체":
    filtered_df = filtered_df[filtered_df['전형구분'] == selected_type]
if selected_major != "전체":
    filtered_df = filtered_df[filtered_df['모집단위'] == selected_major]

# 성적 구간 조건 적용 (±5% 범위 포함)
result_df = filtered_df[
    (filtered_df['성적'] >= lower_bound) &
    (filtered_df['성적'] <= upper_bound)
]

# 위험도 컬럼 추가
result_df = result_df.copy()
avg_score = (min_score + max_score) / 2
result_df['위험도'] = result_df['성적'] - avg_score
result_df['지원 가능성'] = result_df['위험도'].apply(
    lambda x: '안정권' if x >= 0.3 else ('적정' if x >= 0.1 else '위험')
)

# 결과 표시
st.subheader("📋 지원 가능한 대학 리스트")
st.write(f"총 {len(result_df)}개 전형이 조회되었습니다.")
st.dataframe(result_df[['지역', '대학', '모집단위', '전형구분', '전형', '성적', '지원 가능성']])

# 다운로드 기능
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8-sig')

csv = convert_df(result_df)
st.download_button(
    label="결과 CSV 다운로드",
    data=csv,
    file_name='지원가능대학결과.csv',
    mime='text/csv'
)

