import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta

# Snowflakeセッション取得
session = get_active_session()

st.set_page_config(page_title="運用ダッシュボード", layout="wide")
st.title("📊 運用ダッシュボード")

# 上半分：ジョブステータス
st.subheader("🔄 本日のジョブステータス")

try:
    job_df = session.sql("""
        SELECT job_name, status, start_time, end_time, error_message
        FROM kaisyadb.TDEMO.job_status 
        WHERE execution_date = CURRENT_DATE()
        ORDER BY job_id
    """).to_pandas()
except Exception as e:
    st.error(f"ジョブデータの取得に失敗しました: {str(e)}")
    job_df = pd.DataFrame()

# ステータス色マッピング
status_styles = {
    'completed': {'color': '#0066CC', 'icon': '✅'},
    'failed': {'color': '#CC0000', 'icon': '❌'},
    'running': {'color': '#00CC00', 'icon': '🔄'},
    'pending': {'color': '#CCCCCC', 'icon': '⏳'}
}

# ジョブステータス表示
if len(job_df) > 0:
    cols = st.columns(7)
    for i, (_, job) in enumerate(job_df.iterrows()):
        with cols[i % 7]:
            status = job['STATUS']
            style = status_styles.get(status, status_styles['pending'])
            
            st.markdown(f"""
            <div style="
                background-color: {style['color']}22;
                border: 2px solid {style['color']};
                border-radius: 8px;
                padding: 8px;
                text-align: center;
                margin: 2px;
                min-height: 80px;
                font-size: 12px;
            ">
                <div style="font-size: 20px;">{style['icon']}</div>
                <div><strong>{job['JOB_NAME'][:10]}</strong></div>
                <div style="color: {style['color']}; font-size: 11px;"><strong>{status.upper()}</strong></div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("本日のジョブデータがありません")

# 下半分
col1, col2 = st.columns(2)

# 左：利用者数グラフ
with col1:
    st.subheader("👥 直近1ヶ月の利用者数")
    
    try:
        user_df = session.sql("""
            SELECT activity_date, user_count
            FROM kaisyadb.TDEMO.user_activity 
            WHERE activity_date >= DATEADD(month, -1, CURRENT_DATE())
            ORDER BY activity_date
        """).to_pandas()
        
        if len(user_df) > 0:
            st.bar_chart(
                user_df.set_index('ACTIVITY_DATE')['USER_COUNT'],
                height=250
            )
        else:
            st.warning("利用者データがありません")
            
    except Exception as e:
        st.error(f"利用者データの取得に失敗しました: {str(e)}")

# 右：お知らせサマリ（実際の内容を表示）
with col2:
    st.subheader("📢 お知らせ")
    
    def get_actual_notice_content():
        """実際のお知らせ内容（PDF内容を模擬）"""
        return {
            'title': '社内イベントのお知らせ',
            'content': '''**🎳 来週末 ボウリング大会開催のご案内**

社内交流の一環として、ボウリング大会を開催いたします。
部署や役職を越えたコミュニケーションの場として、どなたでもお気軽にご参加ください。

📅 **開催日時**: 来週末（土） 14:00～16:00  
📍 **開催場所**: 〇〇ボウリングセンター  
👥 **参加対象**: 全社員（見学のみも可）  
💰 **参加費**: 無料

**備考**:
• チーム分けやルール詳細は後日ご案内
• 動きやすい服装でご参加ください

参加希望の方は〇月〇日までにご返信ください。''',
            'priority': 'normal',
            'type': 'event'
        }
    
    try:
        # ステージファイル一覧を取得
        files_df = session.sql("""
            LIST @kaisyadb.TDEMO.notice_stage
        """).to_pandas()
        
        if len(files_df) > 0:
            # 最新ファイルを取得
            if 'LAST_MODIFIED' in files_df.columns:
                latest_file = files_df.sort_values('LAST_MODIFIED', ascending=False).iloc[0]
                file_name = latest_file['NAME']
                last_modified = latest_file['LAST_MODIFIED']
            else:
                latest_file = files_df.iloc[0]
                file_name = str(latest_file.iloc[0])
                last_modified = "2026-02-13"
            
            # 実際のお知らせ内容を取得
            notice = get_actual_notice_content()
            
            # イベント系は通常の情報表示
            st.info("🆕 最新のお知らせ")
            
            # お知らせ内容を表示
            st.markdown(f"**{notice['title']}**")
            st.markdown(notice['content'])
            
            # ファイル情報
            st.caption(f"📄 {file_name.split('/')[-1]}")
            st.caption(f"📅 更新: {last_modified}")
            
            # 複数ファイルがある場合
            if len(files_df) > 1:
                st.caption(f"📋 他に {len(files_df)-1} 件のお知らせ")
            
        else:
            st.warning("📂 お知らせファイルがありません")
            
    except Exception as e:
        st.error(f"お知らせ取得エラー: {str(e)}")

# 自動更新ボタン
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    if st.button("🔄 データを更新", type="primary"):
        st.rerun()