import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

# --- 1. 使用 cache_resource 保持連線物件，避免重複建立 ---
@st.cache_resource
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

conn = get_connection()

def load_data():
    # 如果 session_state 裡還沒有資料，或者我們想強制更新
    if 'attendance_data' not in st.session_state:
        # 只在第一次或手動觸發時連接 Google
        st.session_state.attendance_data = conn.read(ttl=0) 
    return st.session_state.attendance_data

def save_data(df):
    # 寫入雲端
    conn.update(data=df)
    # 更新本地暫存，這樣下次 get_data 就會直接拿這份，不用重連
    st.session_state.attendance_data = df
    st.toast("雲端同步完成！")
    st.cache_data.clear() # 強制刷新畫面

# --- 介面導航 ---
st.set_page_config(page_title="Logistic Community Sharing點名管理系統", layout="wide")

st.title("🎓 現場自主簽到")
df = load_data()

with st.form("checkin", clear_on_submit=True):
    name = st.text_input("輸入您的信箱")
    btn = st.form_submit_button("送出")
    if btn:
        if name in df['信箱'].values:
            idx = df[df['信箱'].str.lower() == name].index[0]
            now = datetime.now().strftime("%H:%M")
            
            if pd.isna(df.at[idx, '簽到時間']):
                df.at[idx, '簽到時間'] = now
                df.at[idx, 'Mode']="OFFLINE"
                st.success(f"{name} 簽到成功！")
                save_data(df)
            else:
                st.info(f"{name} 已簽到，不需重複簽到") 
            
        else:
            st.error("名單中無此信箱")