from utils import *
from prompt import *
from tools import cql_graph_func, local_search, global_search

import os
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, LLMRequestsChain
from langchain.agents import ZeroShotAgent, AgentExecutor, Tool
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma


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
            'url': 'https://www.google.com/search?q=' + query.replace(' ', '+')
        }
        return llm_request_chain.run(inputs)

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
                description='用于回答优秀学生评选、推免研究生（保研）等相关问题',
            ),
            Tool.from_function(
                name='graph_local_search',
                func=self.graph_local_search,
                description='用于回答奖学金评选、违纪处分等相关问题',
            ),
            Tool.from_function(
                name='graph_global_search',
                func=self.graph_global_search,
                description='用于回答与学生政策相关，且需要复杂推理的问题',
            ),
            Tool.from_function(
                name='google_search',
                func=self.google_search,
                description='其他工具没有正确答案时，通过搜索引擎，回答通用类问题',
            ),
        ]

        prefix = """请用中文回答当前问题。你有以下工具可以使用。必须严格按照如下格式回答：

        Thought: 分析当前问题需要使用什么工具
        Action: 选择使用的工具名称（必须是上述工具之一）
        Action Input: 输入给工具的内容
        Observation: 工具返回的结果
        Final Answer: 根据 Observation 给出的最终答案

        注意：
        1. 请参考历史对话，保持回答的连贯性
        2. 必须按照上述格式逐步输出
        3. 每个标签必须单独成行"""

        suffix = """历史对话：
        {chat_history}

        当前问题: {input}
        {agent_scratchpad}"""

        agent_prompt = ZeroShotAgent.create_prompt(
            tools=tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=['input', 'chat_history', 'agent_scratchpad']
        )

        llm_chain = LLMChain(llm=get_llm_model(), prompt=agent_prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain)

        memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True,
            output_key='output'
        )

        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=os.getenv('VERBOSE'),
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="force"
        )

        try:
            result = agent_chain.run({'input': query})
            return result
        except Exception as e:
            print(f"Error during execution: {str(e)}")
            return "抱歉，处理您的问题时出现了错误，请重试。"


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
    # print(agent.query('Taylor Swift最近有什么动态？'))

    # 连续对话测试
    print(agent.query("国家奖学金的申请条件是什么？"))
    print(agent.query("这些条件中，成绩要求具体是多少？"))
    print(agent.query("如果我成绩没有达到前10%，还有机会申请吗？"))