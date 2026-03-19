import json
import os
from datetime import datetime, timedelta

DATA_FILE = "study_data.json"

def load_data() -> dict:
    """读取本地打卡数据（含自动补全逻辑，防止报错）"""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 🚀 兼容性修复：遍历所有日期，确保老记录也有 tasks 和 daily_log 字段
        for date_str in data:
            if "tasks" not in data[date_str]:
                data[date_str]["tasks"] = []  # 默认无任务
            if "daily_log" not in data[date_str]:
                data[date_str]["daily_log"] = "" # 默认无日记
        return data
    except Exception:
        return {}

def save_data(data: dict):
    """保存打卡数据到本地"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_record(leetcode_count: int, study_minutes: int, status: str, 
               tasks: list = None, daily_log: str = "", overwrite: bool = False):
    """
    升级版打卡：支持任务清单和每日随笔
    :param tasks: 格式示例 [{"desc": "写代码", "done": True}]
    :param daily_log: 随笔文本
    """
    data = load_data()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 准备新任务列表
    in_tasks = tasks if tasks is not None else []

    # 🧠 思路解析：
    if overwrite or today_str not in data:
        # 直接采用当前值
        new_leetcode = leetcode_count
        new_study_time = study_minutes
        new_status = status
        new_tasks = in_tasks
        new_log = daily_log
    else:
        # 走累加逻辑
        existing = data.get(today_str, {})
        new_leetcode = existing.get("leetcode_count", 0) + leetcode_count
        new_study_time = existing.get("study_minutes", 0) + study_minutes
        new_status = f"{existing.get('status', '')} | {status}".strip(" | ")
        
        # 任务处理：如果本次传了任务就用新的，没传就保留旧的
        new_tasks = in_tasks if in_tasks else existing.get("tasks", [])
        
        # 日记处理：换行追加内容，保护之前的灵感
        old_log = existing.get("daily_log", "")
        new_log = f"{old_log}\n{daily_log}".strip() if daily_log else old_log

    # 判断是否完成
    completed = (new_leetcode >= 1) or (new_study_time >= 30)
    
    data[today_str] = {
        "date": today_str,
        "leetcode_count": new_leetcode,
        "study_minutes": new_study_time,
        "status": new_status,
        "tasks": new_tasks,   # 🚀 新增
        "daily_log": new_log, # 🚀 新增
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
        
        if i == 0 and date_str not in data:
            continue
            
        record = data.get(date_str)
        if record and record.get("completed", False):
            streak += 1
        else:
            break 
    return streak

def get_weekly_stats() -> dict:
    """获取最近7天的统计数据（含任务和日记）"""
    data = load_data()
    today = datetime.now().date()
    total_lc = 0
    total_time = 0
    
    recent_data = [] 
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