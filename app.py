import streamlit as st
import pandas as pd

# 데이터 불러오기
df = pd.read_excel("univ_data.xlsx")

st.set_page_config(page_title="대학 지원 가능성 조회", layout="wide")
st.title("🎓 대학 지원 가능성 조회 프로그램")

# 검색 모드 선택
mode = st.radio("검색 방식 선택", ["내 점수로 조회", "성적 구간으로 조회"])

# 공통 필터 옵션 구성
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

# 점수 기반 필터링
if mode == "내 점수로 조회":
    user_score = st.number_input("본인의 학생부 성적(등급)을 입력하세요 (예: 1.8)", min_value=0.0, max_value=9.0, step=0.01)
    result_df = filtered_df[filtered_df['성적'] >= user_score]

# 성적 구간 기반 필터링
else:
    min_score, max_score = st.slider(
        "성적 범위를 설정하세요 (예: 1.0 ~ 2.5)",
        min_value=0.0, max_value=9.0, value=(1.0, 2.5), step=0.05
    )
    lower_bound = min_score * 0.95
    upper_bound = max_score * 1.05
    st.write(f"±5% 적용된 실제 검색 범위: {lower_bound:.2f} ~ {upper_bound:.2f}")
    result_df = filtered_df[
        (filtered_df['성적'] >= lower_bound) &
        (filtered_df['성적'] <= upper_bound)
    ]

# 결과 표시
st.subheader("📋 조회 결과")
st.write(f"총 {len(result_df)}개 전형이 조회되었습니다.")
st.dataframe(result_df[['지역', '대학', '모집단위', '전형구분', '전형', '성적']])

# 다운로드 기능
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8-sig')

csv = convert_df(result_df[['지역', '대학', '모집단위', '전형구분', '전형', '성적']])
st.download_button(
    label="결과 CSV 다운로드",
    data=csv,
    file_name='지원가능대학결과.csv',
    mime='text/csv'
)