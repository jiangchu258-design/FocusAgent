import streamlit as st

def render_timer_ui(mins, secs, is_running):
    if is_running:
        st.markdown(f"""
            <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #e0f2f1 0%, #e1f5fe 100%); border-radius: 20px; margin-top: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.05);">
                <h1 style="color: #006064; font-size: 60px; margin: 0;">{mins:02d}:{secs:02d}</h1>
                <p style="color: #00838f; margin-top: 10px;">✨ 沉浸在知识的海洋中...</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 30px; background-color: #f8f9fa; border-radius: 20px; margin-top: 15px;">
                <h1 style="color: #adb5bd; font-size: 60px; margin: 0;">00:00</h1>
                <p style="color: #adb5bd; margin-top: 10px;">☕ 蓄势待发，准备开启专注</p>
            </div>
        """, unsafe_allow_html=True)