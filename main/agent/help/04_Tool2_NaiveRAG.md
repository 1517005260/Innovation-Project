# Tool 2: 传统RAG

将data_process.py处理过的数据，召回后返回给大模型

1. prompt.py新增召回提示词：

```python
RETRIVAL_PROMPT_TPL = '''
请根据以下检索结果，回答用户问题，不需要补充和联想内容。
检索结果中没有相关信息时，回复“不知道”。
----------
检索结果：{query_result}
----------
用户问题：{query}
'''
```

2. agent.py修改：

```python
class Agent:
    def __init__(self):
        # 加载缓存好的向量文件
        self.vdb = Chroma(
            persist_directory=os.path.join(os.path.dirname(__file__), './data/vector_db'),
            embedding_function=get_embeddings_model()
        )
    
    def retrival_func(self, query):
        documents = self.vdb.similarity_search_with_relevance_scores(query, k=5)   # 召回
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
```