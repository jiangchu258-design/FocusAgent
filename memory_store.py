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

def add_record(leetcode_count: int, study_minutes: int, status: str, overwrite: bool = False):
    """
    添加或更新今日打卡记录
    :param overwrite: 为 True 时直接覆盖今日数据，为 False 时进行累加。
    """
    data = load_data()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 🧠 思路解析：
    # 如果是“修正模式”或者今天还没数据，直接采用当前输入的值
    if overwrite or today_str not in data:
        new_leetcode = leetcode_count
        new_study_time = study_minutes
        new_status = status
    else:
        # 否则，走原来的累加逻辑
        existing_record = data.get(today_str, {})
        new_leetcode = existing_record.get("leetcode_count", 0) + leetcode_count
        new_study_time = existing_record.get("study_minutes", 0) + study_minutes
        new_status = f"{existing_record.get('status', '')} | {status}".strip(" | ")

    # 重新判断达标状态
    completed = (new_leetcode >= 1) or (new_study_time >= 30)
    
    data[today_str] = {
        "date": today_str,
        "leetcode_count": new_leetcode,
        "study_minutes": new_study_time,
        "status": new_status,
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
        
        # 如果是今天还没打卡，不中断 streak，继续看昨天
        if i == 0 and date_str not in data:
            continue
            
        record = data.get(date_str)
        if record and record.get("completed", False):
            streak += 1
        else:
            break 
            
    return streak

def get_weekly_stats() -> dict:
    """获取最近7天的统计数据（用于图表展示）"""
    data = load_data()
    today = datetime.now().date()
    total_lc = 0
    total_time = 0
    
    recent_data = [] # 改为列表格式，方便 Pandas 读取
    for i in range(7):
        date_obj = today - timedelta(days=i)
        date_str = date_obj.strftime("%Y-%m-%d")
        
        if date_str in data:
            record = data[date_str]
            recent_data.append(record)
            total_lc += record.get("leetcode_count", 0)
            total_time += record.get("study_minutes", 0)
            
    return {
        "total_leetcode": total_lc,
        "total_time": total_time,
        "recent_data": recent_data 
    }