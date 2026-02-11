import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import io

# Snowflakeセッションの取得
session = get_active_session()

# USE文は削除（サポートされていないため）
# session.sql("USE DATABASE KAISYADB").collect()  # この行を削除
# session.sql("USE SCHEMA TDEMO").collect()       # この行を削除

st.title("企業情報検索システム 🏢")
st.markdown("企業コードで検索して、企業情報を参照・ダウンロードできます")

# サイドバーで検索機能
st.sidebar.header("検索条件")
company_code = st.sidebar.text_input("企業コード", placeholder="例: 7203")
search_button = st.sidebar.button("検索")

# メイン画面の検索結果表示
if search_button and company_code:
    try:
        # 完全修飾名でテーブルを指定（KAISYADB.TDEMO.テーブル名）
        query = f"""
        SELECT 
            company_code,
            company_name,
            industry,
            established_date,
            capital,
            employees,
            headquarters,
            website,
            description
        FROM KAISYADB.TDEMO.company_master
        WHERE company_code = '{company_code}'
        """
        
        # データ取得
        df = session.sql(query).to_pandas()
        
        if not df.empty:
            st.success(f"企業コード {company_code} の情報が見つかりました！")
            
            # 企業情報表示
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("基本情報")
                st.write(f"**企業名:** {df['COMPANY_NAME'].iloc[0]}")
                st.write(f"**業界:** {df['INDUSTRY'].iloc[0]}")
                st.write(f"**設立年:** {df['ESTABLISHED_DATE'].iloc[0]}")
                st.write(f"**資本金:** {df['CAPITAL'].iloc[0]:,} 円")
            
            with col2:
                st.subheader("詳細情報")
                st.write(f"**従業員数:** {df['EMPLOYEES'].iloc[0]:,} 人")
                st.write(f"**本社:** {df['HEADQUARTERS'].iloc[0]}")
                st.write(f"**ウェブサイト:** {df['WEBSITE'].iloc[0]}")
            
            # 企業説明
            st.subheader("企業概要")
            st.write(df['DESCRIPTION'].iloc[0])
            
            # データ表示
            st.subheader("詳細データ")
            st.dataframe(df)
            
            # ダウンロード機能
            # ダウンロード機能の部分を以下に置き換え
            st.subheader("ダウンロード")
            col1, col2 = st.columns(2)
            
            with col1:
                # CSVダウンロード
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📄 CSVでダウンロード",
                    data=csv,
                    file_name=f"company_{company_code}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Excelダウンロード（openpyxlを使用、またはCSVのみに変更）
                try:
                    # pandasのto_excel()でデフォルトエンジンを使用
                    buffer = io.BytesIO()
                    df.to_excel(buffer, sheet_name='企業情報', index=False, engine='openpyxl')
                    
                    st.download_button(
                        label="📊 Excelでダウンロード",
                        data=buffer.getvalue(),
                        file_name=f"company_{company_code}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except ImportError:
                    # Excelエンジンが利用できない場合は、CSV形式での代替ダウンロード
                    st.download_button(
                        label="📊 データダウンロード（CSV）",
                        data=csv,
                        file_name=f"company_{company_code}_data.csv",
                        mime="text/csv"
                    )
        else:
            st.error(f"企業コード {company_code} の情報が見つかりませんでした")
            
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")

# 売上推移グラフ
if search_button and company_code:
    st.subheader("📈 売上推移（直近3年間）")
    
    sales_query = f"""
    WITH sales_data AS (
        SELECT 
            YEAR(sales_date) as sales_year,
            MONTH(sales_date) as sales_month,
            SUM(sales_amount) as monthly_sales
        FROM KAISYADB.TDEMO.sales_history
        WHERE company_code = '{company_code}'
        AND sales_date >= DATEADD(year, -3, CURRENT_DATE())
        GROUP BY sales_year, sales_month
    )
    SELECT 
        sales_year || '-' || LPAD(sales_month, 2, '0') as year_month,
        monthly_sales,
        DATE_FROM_PARTS(sales_year, sales_month, 1) as sales_date
    FROM sales_data
    ORDER BY sales_date
    """
    
    try:
        sales_df = session.sql(sales_query).to_pandas()
        
        if not sales_df.empty:
            st.line_chart(
                sales_df.set_index('YEAR_MONTH')['MONTHLY_SALES'],
                use_container_width=True
            )
            
            with st.expander("売上データ詳細を表示"):
                st.dataframe(sales_df)
        else:
            st.info("売上データが見つかりませんでした")
            
    except Exception as e:
        st.error(f"売上データ取得エラー: {str(e)}")

# 企業一覧表示（オプション）
st.sidebar.markdown("---")
if st.sidebar.button("全企業一覧表示"):
    query_all = """
    SELECT company_code, company_name, industry
    FROM KAISYADB.TDEMO.company_master
    ORDER BY company_code
    LIMIT 100
    """
    df_all = session.sql(query_all).to_pandas()
    st.subheader("企業一覧（上位100件）")
    st.dataframe(df_all)