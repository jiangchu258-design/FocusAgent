import streamlit as st
import os
import tempfile
from vector_store import process_and_add_document

st.set_page_config(page_title="知识库管理", page_icon="📚")
st.title("📚 个人知识库构建")
st.markdown("在此上传你的技术笔记、错题本（支持 .txt 和 .md 格式）。AI 将自动学习这些资料，以便在对话中为你解答！")

uploaded_file = st.file_uploader("选择文档", type=["txt", "md"])

if uploaded_file is not None:
    # 获取文件类型
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if st.button("🚀 注入 AI 记忆"):
        with st.spinner("切分文档并生成向量中..."):
            try:
                # Streamlit 上传的是内存对象，需暂存为临时文件才能被 LangChain loader 读取
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # 调用核心处理逻辑
                chunks_count = process_and_add_document(tmp_file_path, file_extension)
                
                # 删除临时文件
                os.remove(tmp_file_path)
                
                st.success(f"✅ 知识注入成功！文档已被切分为 {chunks_count} 个记忆片段。返回主页进行 RAG 问答吧！")
            except Exception as e:
                st.error(f"处理失败: {e}")