import streamlit as st

st.set_page_config(page_title="Enhanced Dashboard", layout="wide")
st.title("📈 強化されたダッシュボード")

session = st.connection('snowflake').session()

# サンプルデータ作成
sample_data = session.create_dataframe(
    [["Product A", 100], ["Product B", 150], ["Product C", 80]],
    schema=["PRODUCT", "SALES"]
).to_pandas()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 データテーブル")
    st.dataframe(sample_data, use_container_width=True)

with col2:
    st.subheader("📈 売上グラフ")
    # Streamlitネイティブの美しいバーチャート
    st.bar_chart(sample_data.set_index('PRODUCT'), 
                use_container_width=True)

# その他のかっこいいグラフ
st.subheader("📊 追加の可視化")
col3, col4 = st.columns(2)

with col3:
    # 線グラフ
    import pandas as pd
    chart_data = pd.DataFrame({
        '売上': [100, 150, 80, 120, 90],
        '利益': [20, 45, 15, 35, 25]
    })
    st.line_chart(chart_data, use_container_width=True)

with col4:
    # エリアチャート
    st.area_chart(chart_data, use_container_width=True)

st.success("✨ Streamlitネイティブグラフで十分かっこいい！")