import json
import os
from datetime import datetime, timedelta

DATA_FILE = "study_data.json"

def load_data() -> dict:
    """读取本地打卡数据"""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data: dict):
    """保存打卡数据到本地"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_record(leetcode_count: int, study_time: int, status: str):
    """添加或更新今日打卡记录"""
    data = load_data()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 判断是否完成：刷题>=1 或 时长>=30分钟
    completed = (leetcode_count >= 1) or (study_time >= 30)
    
    data[today_str] = {
        "date": today_str,
        "leetcode_count": leetcode_count,
        "study_time": study_time,
        "status": status,
        "completed": completed
    }
    save_data(data)
    return completed

def calculate_streak() -> int:
    """计算连续打卡天数 (Streak)"""
    data = load_data()
    streak = 0
    today = datetime.now().date()
    
    for i in range(365):
        check_date = today - timedelta(days=i)
        date_str = check_date.strftime("%Y-%m-%d")
        
        # 如果是今天且还没打卡，允许跳过，不中断 streak
        if i == 0 and date_str not in data:
            continue
            
        record = data.get(date_str)
        if record and record.get("completed", False):
            streak += 1
        else:
            break # 一旦中断，停止计算
            
    return streak

def get_weekly_stats() -> dict:
    """获取最近7天的统计数据"""
    data = load_data()
    today = datetime.now().date()
    total_lc = 0
    total_time = 0
    
    recent_data = {}
    for i in range(7):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if date_str in data:
            recent_data[date_str] = data[date_str]
            total_lc += data[date_str].get("leetcode_count", 0)
            total_time += data[date_str].get("study_time", 0)
            
    return {
        "total_leetcode": total_lc,
        "total_time": total_time,
        "recent_data": recent_data # 用于喂给 AI 做分析
    }