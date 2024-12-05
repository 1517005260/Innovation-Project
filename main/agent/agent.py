from utils import *
from config import *
from prompt import *
from tools import cql_graph_func, local_search, global_search

import os
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain.chains import LLMChain, LLMRequestsChain
from langchain.agents import ZeroShotAgent, AgentExecutor, Tool
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_community.vectorstores import Chroma, FAISS


class Agent:
    def __init__(self):
        # 加载缓存好的向量文件
        self.vdb = Chroma(
            persist_directory=os.path.join(os.path.dirname(__file__), './data/vector_db'),
            embedding_function=get_embeddings_model()
        )

    def generic_func(self, query):
        prompt = PromptTemplate.from_template(GENERIC_PROMPT_TPL)
        llm_chain = LLMChain(
            llm=get_llm_model(),
            prompt=prompt,
            verbose=os.getenv('VERBOSE')
        )
        return llm_chain.run(query)

    def retrival_func(self, query):
        documents = self.vdb.similarity_search_with_relevance_scores(query, k=5)  # 召回
        query_result = [doc[0].page_content for doc in documents if doc[1] < 0.4]  # 过滤， [0]是内容，[1]是分数

        # 填充提示词并总结答案
        prompt = PromptTemplate.from_template(RETRIVAL_PROMPT_TPL)
        retrival_chain = LLMChain(
            llm=get_llm_model(),
            prompt=prompt,
            verbose=os.getenv('VERBOSE')
        )
        inputs = {
            'query': query,
            'query_result': '\n\n'.join(query_result) if len(query_result) else '没有查到'
        }
        return retrival_chain.run(inputs)

    def graph_func(self, query):
        return cql_graph_func.cql_func(query)

    def graph_local_search(self, query):
        engine = local_search.setup_search_engine()
        return engine.query(query)

    def graph_global_search(self, query):
        return global_search.global_retriever(query,level=2)


if __name__ == '__main__':
    agent = Agent()
    # print(agent.generic_func("你是谁？"))
    # print(agent.retrival_func('优秀学生申请条件？'))
    # print(agent.retrival_func('应该怎么联系教务处领导？'))
    # print(agent.graph_func('优秀学生怎么申请'))
    # print(agent.graph_local_search("国家奖学金的申请条件？"))
    print(agent.graph_global_search("国家奖学金的申请条件？"))
