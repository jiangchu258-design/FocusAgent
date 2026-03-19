import streamlit as st
import time
from memory_store import add_record, calculate_streak, get_weekly_stats
from rag_service import get_ai_feedback, get_rag_chain
from langchain.memory import ConversationBufferMemory

# 页面基础配置
st.set_page_config(page_title="FocusAgent | 伴学智能体", page_icon="🎯", layout="wide")
st.title("🎯 FocusAgent 个人伴学空间")

# ========== 核心防报错：会话状态初始化 ==========
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "study_minutes" not in st.session_state:
    st.session_state.study_minutes = 0
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "你好，我是你的严格伴学 AI。输入“点评”查看你的学情分析，或者向我询问你笔记库中的知识点！"}]

# ========== 侧边栏：UI导航与统计 ==========
with st.sidebar:
    st.header("📊 数据面板")
    streak = calculate_streak()
    st.metric(label="🔥 连续打卡 (Streak)", value=f"{streak} 天")
    
    stats = get_weekly_stats()
    st.write("---")
    st.write("📈 **本周统计**")
    st.write(f"- 刷题总数: {stats['total_leetcode']} 道")
    st.write(f"- 学习时长: {stats['total_time']} 分钟")
    st.write("---")
    st.page_link("pages/app_kb.py", label="📂 前往知识库管理", icon="📚")

# ========== 左侧：学习追踪与计时器 ==========
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⏱️ 专注计时器")
    
    # 定义回调函数，保证状态在 UI 渲染前就更新完毕
    def start_timer():
        st.session_state.start_time = time.time()
        st.session_state.timer_running = True
        
    def stop_timer():
        if st.session_state.start_time is not None: 
            elapsed_secs = time.time() - st.session_state.start_time
            st.session_state.study_minutes += int(elapsed_secs // 60)
            st.session_state.timer_running = False
            st.session_state.start_time = None

    btn_col1, btn_col2 = st.columns(2)
    
    # 通过 on_click 绑定回调函数
    if btn_col1.button("▶️ 开始专注", disabled=st.session_state.timer_running, on_click=start_timer):
        st.toast("🚀 计时开始，全神贯注！")
        
    if btn_col2.button("⏹ 结束专注", disabled=not st.session_state.timer_running, on_click=stop_timer):
        st.success(f"专注结束！已记录 {st.session_state.study_minutes} 分钟。")

    if st.session_state.timer_running:
        st.info("🕒 计时中，专心致志！(点击结束停止)")
        
    st.divider()
    
    st.subheader("📝 今日打卡")
    with st.form("study_form"):
        lc_count = st.number_input("力扣刷题数", min_value=0, value=0, step=1)
        study_time = st.number_input("学习时长 (分钟)", min_value=0, value=st.session_state.study_minutes, step=1)
        status = st.selectbox("今日状态", ["good", "normal", "bad"], index=1)
        
        submitted = st.form_submit_button("💾 提交今日记录")
        if submitted:
            is_completed = add_record(lc_count, study_time, status)
            if is_completed:
                st.success("✅ 打卡成功！Streak 已维持。")
                st.balloons()
            else:
                st.warning("⚠️ 打卡成功，但由于（时长<30且未刷题），今日算作未完成！Streak 会断哦！")

# ========== 右侧：AI 对话系统 (双模智能) ==========
with col2:
    st.subheader("🤖 智能伴学对话")
    
    # 渲染历史对话
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # 接收用户输入
    if prompt := st.chat_input("输入你的问题，或回复‘点评’..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("AI 思考中..."):
                if any(kw in prompt for kw in ["点评", "总结", "分析", "打卡"]):
                    stats = get_weekly_stats()
                    response_text = get_ai_feedback(stats["recent_data"])
                else:
                    try:
                        qa_chain = get_rag_chain(st.session_state.chat_memory)
                        result = qa_chain.invoke({"question": prompt})
                        response_text = result["answer"]
                    except Exception as e:
                        response_text = f"🚨 知识库检索失败，请检查 API Key 或确认是否已上传文档。错误详情：{str(e)}"
                
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})