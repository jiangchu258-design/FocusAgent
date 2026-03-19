# 🎯 FocusAgent: 个人 AI 伴学智能体

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)

**FocusAgent** 是一款专为自律学习者打造的 Web 端 AI 伴学系统。它不仅能记录你的学习数据，更能通过 RAG 技术深度理解你的个人笔记与错题，提供个性化的复习指导。

## ✨ 核心亮点

- 🛡️ **行为分析系统**：实时追踪 LeetCode 刷题数与学习时长，集成 **Streak (连续打卡)** 激励机制。
- 🧠 **RAG 个人知识库**：基于 **ChromaDB** 与 **通义千问**，支持上传 `.txt/.md` 笔记，实现针对错题的深度问答。
- 🤖 **双模意图路由**：自动识别用户指令。
  - *分析模式*：严厉且精准的周度学情总结。
  - *问答模式*：基于本地知识库的检索增强生成。
- ⏱️ **专注计时器**：内置防误触逻辑的计时组件，自动关联打卡数据。

## 🛠️ 技术栈

- **Frontend**: Streamlit (Responsive Web Design)
- **LLM Framework**: LangChain
- **Vector DB**: ChromaDB
- **Model**: Qwen-Plus (Alibaba DashScope)
- **Storage**: Local JSON & SQLite

## 🚀 快速启动

1. **克隆项目**
   ```bash
   git clone [https://github.com/你的用户名/FocusAgent.git](https://github.com/你的用户名/FocusAgent.git)
   cd FocusAgent

2. 配置环境
创建 .env 文件并填入你的 API Key:
QWEN_API_KEY="your_api_key_here"
DASHSCOPE_API_KEY="your_api_key_here"

3. 安装依赖并运行
pip install -r requirements.txt
python -m streamlit run app_main.py

📅 后续计划 (Roadmap)
[ ] 📈 数据可视化：接入 Echarts 展示学习时长波动曲线。

[ ] 🔔 复习提醒：基于 Ebbinghaus 遗忘曲线自动推送错题复习。

[ ] 📄 格式扩展：支持 PDF、PDF 及 Web URL 的知识采集。

本项目由 JiangChu 开发，旨在探索个人 AI Agent 在垂直教育领域的应用落地。