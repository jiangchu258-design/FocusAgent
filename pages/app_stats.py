import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import calendar
from streamlit_echarts import st_echarts
from memory_store import load_data

st.set_page_config(page_title="FocusAgent | 深度看板", layout="wide")

# ==================== 1. 鲁棒数据加载 ====================
def load_data_safe():
    data = load_data()
    if not data: return pd.DataFrame()
    
    df = pd.DataFrame.from_dict(data, orient='index').reset_index()
    if 'index' in df.columns and 'date' not in df.columns:
        df = df.rename(columns={'index': 'date'})
    elif 'index' in df.columns:
        df = df.drop(columns=['index'], errors='ignore')

    df = df.loc[:, ~df.columns.duplicated()]
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        for col in ['study_minutes', 'leetcode_count']:
            if col not in df.columns: df[col] = 0
        return df.sort_values('date').fillna(0)
    return pd.DataFrame()

# 初始化数据
df = load_data_safe()

# 核心：确保月份状态存在
if 'sel_month' not in st.session_state:
    st.session_state.sel_month = datetime.now().month

# 获取当前要显示的月份数字
cur_m = st.session_state.sel_month

# ==================== 2. 侧边栏与标题 ====================
with st.sidebar:
    st.header("🎯 目标管理")
    weekly_target = st.number_input("本周刷题目标 (道)", min_value=1, value=10, step=1)
    st.divider()
    st.write(f"📅 当前查看：{cur_m} 月")

st.title("📈 学习数据深度看板")

if df.empty:
    st.info("💡 暂无数据，快去主页开启第一次专注吧！")
    st.stop()

# 暂时只保留前两个 Tab，避开报错的详情页
tab_week, tab_month = st.tabs(["📅 近 7 天深度报告", "🗓️ 月度宏观趋势"])

# ==================== 3. Tab 1: 周报 ====================
with tab_week:
    df_week = df.tail(7).copy()
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("🔥 专注时长连贯性")
        area_option = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "boundaryGap": False, "data": df_week['date'].dt.strftime('%m-%d').tolist()},
            "yAxis": {"type": "value", "name": "分钟"},
            "series": [{"name": "时长", "type": "line", "smooth": True, "areaStyle": {"opacity": 0.5, "color": "#e1f5fe"}, "itemStyle": {"color": "#3a7bd5"}, "data": [float(x) for x in df_week['study_minutes'].tolist()]}]
        }
        st_echarts(options=area_option, height="350px")
    with c2:
        st.subheader("🎯 刷题进度")
        week_lc = int(df_week['leetcode_count'].sum())
        gauge_option = { "series": [{"type": "gauge", "startAngle": 90, "endAngle": -270, "min": 0, "max": weekly_target, "progress": {"show": True, "width": 20, "itemStyle": {"color": "#FF4B4B"}}, "axisLine": {"lineStyle": {"width": 20, "color": [[1, "#f0f2f6"]]}}, "axisTick": {"show": False}, "splitLine": {"show": False}, "axisLabel": {"show": False}, "pointer": {"show": False}, "detail": {"valueAnimation": True, "offsetCenter": [0, "0%"], "fontSize": 35, "formatter": "{value}道"}, "data": [{"value": week_lc}]}] }
        st_echarts(options=gauge_option, height="350px")

# ==================== 4. Tab 2: 月报 (修复标题刷新问题) ====================
with tab_month:
    # 注入 CSS 美化按钮
    st.markdown("<style>.stButton button {height: 380px; width: 100%; border: none; font-size: 40px; background-color: rgba(0,0,0,0.02); color: #ccc; transition: 0.3s;} .stButton button:hover {background-color: rgba(0,0,0,0.08); color: #6c5ce7;}</style>", unsafe_allow_html=True)
    
    m_col_prev, m_col_chart1, m_col_chart2, m_col_next = st.columns([0.6, 5, 5, 0.6])

    with m_col_prev:
        st.write("##")
        if st.button("<", key="btn_prev"):
            st.session_state.sel_month = 12 if st.session_state.sel_month == 1 else st.session_state.sel_month - 1
            st.rerun()
            
    with m_col_next:
        st.write("##")
        if st.button(">", key="btn_next"):
            st.session_state.sel_month = 1 if st.session_state.sel_month == 12 else st.session_state.sel_month + 1
            st.rerun()

    # 重新锁定当前显示的月份
    df_m = df[df['date'].dt.month == cur_m].copy()
    
    with m_col_chart1:
        # 🚀 修正点：直接在 subheader 里使用最新的 cur_m
        st.subheader(f"🟩 {cur_m}月积极力热力分配")
        heatmap_data = [[d.strftime('%Y-%m-%d'), float(v)] for d, v in zip(df_m['date'], df_m['study_minutes'])]
        
        heatmap_option = {
            "visualMap": {
                "type": "piecewise", "orient": "horizontal", "left": "center", "top": 0,
                "pieces": [
                    {"min": 360, "label": "6-8h (暴走)", "color": "#1b5e20"},
                    {"min": 240, "max": 360, "label": "4-6h (高效)", "color": "#388e3c"},
                    {"min": 120, "max": 240, "label": "2-3h (稳定)", "color": "#81c784"},
                    {"min": 0.1, "max": 60, "label": "0-1h (起步)", "color": "#c8e6c9"},
                    {"value": 0, "label": "无记录", "color": "#ebedf0"}
                ]
            },
            "calendar": {"top": 80, "left": "center", "range": f"2026-{cur_m:02d}", "cellSize": [35, 35], "yearLabel": {"show": False}, "dayLabel": {"nameMap": 'cn'}},
            "series": {"type": "heatmap", "coordinateSystem": "calendar", "data": heatmap_data}
        }
        st_echarts(options=heatmap_option, height="380px")

    with m_col_chart2:
        # 🚀 修正点：直接在 subheader 里使用最新的 cur_m
        st.subheader(f"🍭 {cur_m}月刷题霓虹看板")
        last_day = calendar.monthrange(2026, cur_m)[1]
        x_axis_days = [f"{cur_m:02d}-{d:02d}" for d in range(1, last_day + 1)]
        y_map = {d.strftime('%m-%d'): v for d, v in zip(df_m['date'], df_m['leetcode_count'])}
        y_values = [float(y_map.get(day, 0)) for day in x_axis_days]

        lollipop_option = {
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "xAxis": {"type": "category", "data": x_axis_days, "axisLabel": {"interval": 4}},
            "yAxis": {"type": "value", "name": "道"},
            "series": [
                {"name": "刷题数", "type": "bar", "barWidth": 3, "itemStyle": {"color": "#a29bfe", "borderRadius": 5}, "data": y_values},
                {"name": "刷题数", "type": "scatter", "symbolSize": 15, "itemStyle": {"color": "#6c5ce7", "shadowBlur": 10, "shadowColor": "rgba(108, 92, 231, 0.8)"}, "data": y_values}
            ]
        }
        st_echarts(options=lollipop_option, height="380px")

st.markdown("---")
st.page_link("app_main.py", label="🏠 返回主空间")