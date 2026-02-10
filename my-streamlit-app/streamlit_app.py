import streamlit as st

# ページ設定
st.set_page_config(page_title="My First Snowflake App", layout="wide")

# タイトル
st.title("🚀 Streamlit in Snowflake with Git")

# Snowflake接続
session = st.connection('snowflake').session()

# サイドバー
st.sidebar.write("## アプリ情報")
st.sidebar.write("このアプリはGitで管理されています")

# メインコンテンツ
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 データ表示")
    
    # サンプルデータの作成
    sample_data = session.create_dataframe(
        [["Product A", 100], ["Product B", 150], ["Product C", 80]],
        schema=["PRODUCT", "SALES"]
    ).to_pandas()
    
    st.dataframe(sample_data, use_container_width=True)

with col2:
    st.subheader("📈 グラフ")
    st.bar_chart(data=sample_data, x="PRODUCT", y="SALES")

# Git情報表示
st.info("✅ このアプリはGitリポジトリから管理されています")
