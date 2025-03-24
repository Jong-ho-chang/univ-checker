import streamlit as st
import pandas as pd
import os

# 현재 파일 기준 경로 설정
base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, "합불데이터.xlsx")

# 데이터 불러오기
df = pd.read_excel(file_path)

st.set_page_config(page_title="대학 지원 가능성 조회", layout="wide")
st.title("🎓 대학 지원 가능성 조회 프로그램")

# 사용자 성적 입력
user_score = st.number_input("본인의 학생부 성적(등급)을 입력하세요 (예: 1.8)", min_value=0.0, max_value=9.0, step=0.01)

# 필터 옵션
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

# 성적 조건 적용
result_df = filtered_df[filtered_df['성적'] >= user_score]

# 위험도 컬럼 추가
result_df = result_df.copy()
result_df['위험도'] = result_df['성적'] - user_score
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