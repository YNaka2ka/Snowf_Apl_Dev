import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Enhanced Dashboard", layout="wide")
st.title("📈 強化されたダッシュボード")

session = st.connection('snowflake').session()

# 新機能：グラフの追加
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 データテーブル")
    sample_data = session.create_dataframe(
        [["Product A", 100], ["Product B", 150], ["Product C", 80]],
        schema=["PRODUCT", "SALES"]
    ).to_pandas()
    st.dataframe(sample_data)

with col2:
    st.subheader("📈 売上グラフ")
    fig = px.bar(sample_data, x="PRODUCT", y="SALES", 
                 title="製品別売上")
    st.plotly_chart(fig, use_container_width=True)

st.success("✨ 新機能追加：インタラクティブグラフ機能")