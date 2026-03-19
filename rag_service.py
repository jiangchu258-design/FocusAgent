import os
import json
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from vector_store import get_vector_store

load_dotenv()
API_KEY = os.getenv("QWEN_API_KEY")

# ================= 模式一：严格学情分析 (原生 Request 封装) =================
def get_ai_feedback(study_data: dict) -> str:
    """调用千问 API 分析最近学习情况"""
    prompt = f"""
    你是 FocusAgent，一个严格的个人 AI 学习导师。
    以下是用户最近7天的学习打卡数据（JSON格式）：
    {json.dumps(study_data, ensure_ascii=False)}
    
    要求：
    1. 总体字数严格控制在 150 字以内，言简意赅。
    2. 语气稍显严厉，不要过度夸奖。
    3. 给出：学习总结、指出的最大问题、一条改进建议。
    """
    
    # 降级预案：如果没配 Key 或出错，使用 Mock 数据保证程序不死
    if not API_KEY or API_KEY == "your_api_key_here":
        return _mock_feedback()
        
    try:
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "qwen-plus",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"API调用失败: {e}")
        return _mock_feedback()

def _mock_feedback():
    return "【AI 导师评价】\n数据不佳或网络断开。若这是真实表现：你近期的学习极度缺乏连贯性！问题在于只看不练。建议：立刻放下手机，手写一道算法题代码！"

# ================= 模式二：RAG 知识问答 (LangChain 封装) =================
def get_rag_chain(memory: ConversationBufferMemory):
    """构建带有记忆的 RAG 检索对话链"""
    # 借助兼容 OpenAI 的接口调用通义千问，极大地简化了 LangChain 适配
    llm = ChatOpenAI(
        api_key=API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-plus"
    )
    
    vectordb = get_vector_store()
    retriever = vectordb.as_retriever(search_kwargs={"k": 3}) # 检索最相关的 3 个文档块
    
    # ConversationalRetrievalChain 会自动处理上下文并携带历史记忆
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        verbose=False
    )
    return qa_chain