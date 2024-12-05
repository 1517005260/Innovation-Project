# Tool 4 谷歌联网搜索

1. 服务启动时需要vpn

2. 在prompts.py中新增提示词：

```python
SEARCH_PROMPT_TPL = '''
请根据以下检索结果，回答用户问题，不要发散和联想内容。
检索结果中没有相关信息时，回复“不知道”。
----------
检索结果：{query_result}
----------
用户问题：{query}
'''
```

3. agent.py中新增：

```python
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
```

# Agent 串联所有tools

在agent.py中收集我们写的所有tools，封装为langchain的tool：

```python
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
```