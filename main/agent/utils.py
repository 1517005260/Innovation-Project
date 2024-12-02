from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from py2neo import Graph
from config import *

import os
from dotenv import load_dotenv

load_dotenv()


def get_embeddings_model():
    model = OpenAIEmbeddings(model=os.getenv('OPENAI_EMBEDDINGS_MODEL'))
    return model


def get_llm_model():
    model = ChatOpenAI(
        model=os.getenv('OPENAI_LLM_MODEL'),
        temperature=os.getenv('TEMPERATURE'),
        max_tokens=os.getenv('MAX_TOKENS'),
    )
    return model


# 测试
if __name__ == '__main__':
    llm = get_llm_model()
    print(llm.predict("你好"))
