import os
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = os.path.join(os.getcwd(), "chroma_db")

def get_embeddings():
    """获取通义千问 Embedding 模型"""
    # 需要在环境变量中配置 DASHSCOPE_API_KEY
    return DashScopeEmbeddings(model="text-embedding-v1")

def get_vector_store():
    """初始化或获取本地 Chroma 向量数据库"""
    embeddings = get_embeddings()
    # 使用持久化目录保存向量数据
    vectordb = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
    return vectordb

def process_and_add_document(file_path: str, file_type: str):
    """处理文档并存入向量库"""
    # 1. 加载文档
    if file_type == "txt":
        loader = TextLoader(file_path, encoding='utf-8')
    elif file_type == "md":
        loader = UnstructuredMarkdownLoader(file_path)
    else:
        raise ValueError("不支持的文件格式")
        
    documents = loader.load()
    
    # 2. 文本切分 (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,     # 每个块最大字符数
        chunk_overlap=50    # 块之间重叠字符，保证上下文连贯
    )
    chunks = text_splitter.split_documents(documents)
    
    # 3. 存入 Chroma 数据库
    vectordb = get_vector_store()
    vectordb.add_documents(chunks)
    vectordb.persist() # 持久化到本地
    
    return len(chunks)