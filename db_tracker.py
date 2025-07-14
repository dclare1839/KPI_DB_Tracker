import streamlit as st
import pandas as pd
from io import BytesIO


def load_data():

    old_file = st.file_uploader("Upload old CSV file", type=["xlsx"])
    new_file = st.file_uploader("Upload new CSV file", type=["xlsx"])

    if old_file is not None and new_file is not None:
        old_df = pd.read_excel(old_file)
        new_df = pd.read_excel(new_file)
        old_df.columns = column_names
        new_df.columns = column_names
        old_df['_Source'] = 'Old'
        new_df['_Source'] = 'New'

        return old_df, new_df
    else:
        st.warning("Please upload both files.")
        return None, None
    
def new_db(old_df, new_df):
    newly_created = new_df[~new_df['Record ID'].isin(old_df['Record ID'])].reset_index(drop=True)

    return newly_created

def comparison(old_df, new_df, key_column):

    comparison_df = pd.concat((old_df, new_df), axis=0)
    comparison_df.drop_duplicates(subset=('Record ID',key_column), inplace=True, keep=False)
    comparison_df['_Indicator'] = f'Changed {key_column}'
    
    comparison_df = comparison_df[~comparison_df['Record ID'].isin(newly_created['Record ID'])]
    comparison_df = comparison_df[comparison_df['_Source'] == 'New'].reset_index(drop=True)

    return comparison_df


column_names = ['Record ID', 'Company name', 'Company Owner', 'Create Date', 'Last Activity Date', 'Industry', 'First Deal Created Date', 'Country', 'Lifecycle Stage', 'Company Field', 'Geo', 'Bridge', 'Building']
old_df, new_df = load_data()


if old_df is not None and new_df is not None:
    newly_created = new_db(old_df, new_df)
    
    Lifecycle_db = comparison(old_df,new_df, 'Lifecycle Stage')
    Bridge_db = comparison(old_df,new_df, 'Bridge')
    Geo_db = comparison(old_df,new_df, 'Geo')
    Building_db = comparison(old_df,new_df, 'Building')

    st.title("Lifecycle Tracker")
    st.subheader("Newly Created Records")
    st.dataframe(newly_created['Country'].value_counts().reset_index().rename(columns={'index': 'Country', 'Country': 'Count'}), width=800)

    st.subheader("Lifecycle Stage Changes")
    st.dataframe(Lifecycle_db.groupby(['Country', 'Lifecycle Stage']).size().reset_index(name='Count').sort_values(by=['Country', 'Lifecycle Stage'], ascending=[False, True]).reset_index(drop=True), width=800)

    st.subheader("Bridge Changes")
    st.dataframe(Bridge_db.groupby(['Country', 'Bridge']).size().reset_index(name='Count').sort_values(by=['Country', 'Bridge'], ascending=[False, True]).reset_index(drop=True),width=800)

    st.subheader("Geo Changes")
    st.dataframe(Geo_db.groupby(['Country', 'Geo']).size().reset_index(name='Count').sort_values(by=['Country', 'Geo'], ascending=[False, True]).reset_index(drop=True), width=800)

    st.subheader("Building Changes")
    st.dataframe(Building_db.groupby(['Country', 'Building']).size().reset_index(name='Count').sort_values(by=['Country', 'Building'], ascending=[False, True]).reset_index(drop=True), width=800)

    combined_df = pd.concat([newly_created, Lifecycle_db, Bridge_db, Geo_db, Building_db], ignore_index=True)
    # export_button = st.button("Export Data")
    # if export_button:
    #     combined_df.to_csv('DB_Tracker.csv', index=False)

    csv_data = combined_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    st.download_button(
        label="DB_Tracker.csv 다운로드", # 버튼에 표시될 텍스트
        data=csv_data,                    # 다운로드할 데이터 (바이트 형태)
        file_name="DB_Tracker.csv",       # 다운로드될 파일 이름
        mime="text/csv"                   # 파일의 MIME 타입 (필수 아님, 하지만 명시하는 것이 좋음)
    )