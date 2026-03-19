import streamlit as st

def render_task_system():
    st.subheader("✅ 今日任务清单")
    
    # 使用 session_state 暂存还没提交的任务
    if "temp_tasks" not in st.session_state:
        st.session_state.temp_tasks = []

    t_col1, t_col2 = st.columns([3, 1])
    new_task = t_col1.text_input("添加新任务", placeholder="比如：改完 RAG Bug", label_visibility="collapsed")
    if t_col2.button("➕ 添加"):
        if new_task:
            st.session_state.temp_tasks.append({"desc": new_task, "done": False})
            st.rerun()

    # 渲染任务列表
    updated_tasks = []
    for i, task in enumerate(st.session_state.temp_tasks):
        is_done = st.checkbox(task["desc"], value=task["done"], key=f"task_{i}")
        updated_tasks.append({"desc": task["desc"], "done": is_done})
    
    st.session_state.temp_tasks = updated_tasks

    st.divider()
    st.subheader("📝 每日随笔")
    log_content = st.text_area("记录今日感悟或技术难点", placeholder="今天学到了什么？", height=100)
    
    return st.session_state.temp_tasks, log_content