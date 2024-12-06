from utils import *
from prompt import *
from tools import cql_graph_func, local_search, global_search

import os
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, LLMRequestsChain
from langchain.agents import ZeroShotAgent, AgentExecutor, Tool, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma
from langchain import hub


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
        return llm_chain.invoke(query)['text']

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
        return retrival_chain.invoke(inputs)['text']

    def graph_func(self, query):
        return cql_graph_func.cql_func(query)

    def graph_local_search(self, query):
        engine = local_search.setup_search_engine()
        return engine.query(query)

    def graph_global_search(self, query):
        return global_search.global_retriever(query, level=2)

    def google_search(self, query):
        prompt = PromptTemplate.from_template(SEARCH_PROMPT_TPL)
        llm_chain = LLMChain(
            llm=get_llm_model(),
            prompt=prompt,
            verbose=os.getenv('VERBOSE')
        )
        llm_request_chain = LLMRequestsChain(
            llm_chain=llm_chain,
            requests_key='query_result'
        )
        inputs = {
            'query': query,
            # 'url': 'https://www.google.com/search?q=' + query.replace(' ', '+'),  # google搜索
            # 'url': 'https://www.so.com/s?q=' + query.replace(' ', '+'),   # 360 搜索，免翻墙
            'url': 'https://www.bing.com/search?q=' + query.replace(' ', '+'), # bing 搜索
        }
        return llm_request_chain.invoke(inputs)['output']

    def query(self, query):
        tools = [
            Tool.from_function(
                name='generic_func',
                func=self.generic_func,
                description='用于处理通用对话，如问候、感谢等。',
            ),
            Tool.from_function(
                name='retrival_func',
                func=self.retrival_func,
                description='用于回答优秀学生评选、推免研究生（保研）、教务处的联系方式、研究生院等相关问题',
            ),
            Tool.from_function(
                name='graph_local_search',
                func=self.graph_local_search,
                description='用于回答其他学生政策相关问题',
            ),
            # Tool.from_function(
            #     name='graph_global_search',
            #     func=self.graph_global_search,
            #     description='用于回答与学生政策相关，且需要复杂推理的问题',
            # ),
            Tool.from_function(
                name='google_search',
                func=self.google_search,
                description='其他工具没有正确答案时，通过搜索引擎，回答通用类问题',
            ),
        ]

        prompt = PromptTemplate.from_template(REACT_CHAT_PROMPT_TPL)
        prompt.template = '请用中文回答问题！Final Answer 必须尊重 Obversion 的结果，不能改变语义。\n\n' + prompt.template  # 拼一段中文
        llm_agent = create_react_agent(llm=get_llm_model(), tools=tools, prompt=prompt)
        memory = ConversationBufferMemory(memory_key='chat_history')
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=llm_agent,
            tools=tools,
            memory=memory,
            handle_parsing_errors=True,
            verbose=os.getenv('VERBOSE'),
            max_iterations=3,
        )
        return agent_executor.invoke({"input": query})['output']


if __name__ == '__main__':
    agent = Agent()
    # print(agent.generic_func("你是谁？"))
    # print(agent.retrival_func('优秀学生申请条件？'))
    # print(agent.retrival_func('应该怎么联系教务处领导？'))
    # print(agent.graph_func('优秀学生怎么申请'))
    # print(agent.graph_local_search("国家奖学金的申请条件？"))
    # print(agent.graph_global_search("国家奖学金的申请条件？"))
    # print(agent.google_search("双城之战2的主角是谁？"))
    # print(agent.query('你好，你是谁？'))
    # print(agent.query('优秀学生的申请条件？'))
    # print(agent.query('国家奖学金的申请条件？'))
    print(agent.query('周杰伦最近有什么动态？'))

    # 连续对话测试
    # print(agent.query("国家奖学金的申请条件是什么？"))
    # print(agent.query("这些条件中，成绩的具体要求是多少？"))
    # print(agent.query("如果我成绩没有达到前10%，还有机会申请吗？"))