import streamlit as st

# ページ関数の定義
def home():
    st.title("🏠 ホームページ")
    st.write("マルチページアプリのメインページです")
    
    session = st.connection('snowflake').session()
    st.subheader("📊 概要データ")
    sample_data = session.create_dataframe(
        [["Product A", 100], ["Product B", 150], ["Product C", 80]],
        schema=["PRODUCT", "SALES"]
    ).to_pandas()
    st.dataframe(sample_data)

def analytics():
    st.title("📈 分析ページ")
    st.write("詳細な分析とグラフを表示")
    
    session = st.connection('snowflake').session()
    sample_data = session.create_dataframe(
        [["Product A", 100], ["Product B", 150], ["Product C", 80]],
        schema=["PRODUCT", "SALES"]
    ).to_pandas()
    
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(sample_data.set_index('PRODUCT'))
    with col2:
        st.line_chart(sample_data.set_index('PRODUCT'))

def settings():
    st.title("⚙️ 設定ページ")
    st.write("アプリケーション設定")
    
    # 設定オプション
    st.selectbox("テーマ選択", ["ライト", "ダーク", "自動"])
    st.slider("更新間隔（秒）", 5, 60, 30)
    st.checkbox("自動更新を有効にする")

# ナビゲーション設定
pages = {
    "ホーム": home,
    "分析": analytics,
    "設定": settings
}

# ナビゲーション実行
page = st.navigation({
    "メインメニュー": [
        st.Page(home, title="ホーム", icon="🏠"),
        st.Page(analytics, title="分析", icon="📈"),
        st.Page(settings, title="設定", icon="⚙️")
    ]
})

page.run()
