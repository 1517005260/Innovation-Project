from utils import *
import os
from glob import glob  # 遍历文件夹下的所有文件
from langchain.vectorstores.chroma import Chroma
from langchain.document_loaders import CSVLoader, PyMuPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def doc2vec():
    # 文档分块设置
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    # 读取并分割文件
    dir_path = os.path.join(os.path.dirname(__file__), './data/inputs/')

    documents = []
    for file_path in glob(dir_path + '*.*'):
        loader = None
        if '.csv' in file_path:
            loader = CSVLoader(file_path, encoding='utf-8')
        if '.pdf' in file_path:
            loader = PyMuPDFLoader(file_path)
        if '.txt' in file_path:
            loader = TextLoader(file_path, encoding='utf-8')
        if '.docx' in file_path:
            loader = UnstructuredWordDocumentLoader(file_path, encoding='utf-8')
        if loader:
            documents += loader.load_and_split(text_splitter)

    # 向量化存储
    if documents:
        vdb = Chroma.from_documents(
            documents=documents,
            embedding=get_embeddings_model(),
            persist_directory=os.path.join(os.path.dirname(__file__), './data/vector_db/')
        )
        vdb.persist()


if __name__ == '__main__':
    doc2vec()
