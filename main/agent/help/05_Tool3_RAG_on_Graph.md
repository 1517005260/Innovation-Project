# Tool 3: 基于知识图谱的RAG

1. 知识图谱的创建，使用llm-graph-builder自动构建

2. 首先，增加prompt.py，我们需要先从用户的问题中抽取实体

```python
ENTITY_PROMPT_TPL = '''
1、从以下用户输入的句子中，提取实体内容。
2、注意：根据用户输入的事实抽取内容，不要推理，不要补充信息。

{format_instructions}
------------
用户输入：{query}
------------
输出：
'''
```

增加utils.py，新增抽取函数：

```python
def structured_output_parser(response_schemas):
    text = '''
    请从以下文本中，抽取出实体信息，并按json格式输出，json包含首尾的 "```json" 和 "```"。
    以下是字段含义和类型，要求输出json中，**必须包含下列所有字段**：\n
    '''
    for schema in response_schemas:
        text += schema.name + ' 字段，表示：' + schema.description + '，类型为：' + schema.type + '\n'
    return text
```

修改agent.py，新增处理json的函数：

```python
def graph_func(self, query):
    # 命名实体识别
    response_schemas = [
            ResponseSchema(type='list', name='award', description='奖学金、奖励类实体'),
            ResponseSchema(type='list', name='amount', description='金额、数值实体'),
            ResponseSchema(type='list', name='condition', description='获得奖励或处分的条件实体'),
            ResponseSchema(type='list', name='department', description='学校相关部门实体'),
            ResponseSchema(type='list', name='document', description='相关文件、规定实体'),
            ResponseSchema(type='list', name='duration', description='处分、奖励期限实体'),
            ResponseSchema(type='list', name='honor', description='荣誉称号实体'),
            ResponseSchema(type='list', name='organization', description='组织机构实体'),
            ResponseSchema(type='list', name='process', description='评定、处理流程实体'),
            ResponseSchema(type='list', name='punishment', description='处分类实体'),
            ResponseSchema(type='list', name='violation', description='违纪行为实体'),
        ]

    output_parser = StructuredOutputParser(response_schemas=response_schemas)
    format_instructions = structured_output_parser(response_schemas)

    entity_prompt = PromptTemplate(
        template=ENTITY_PROMPT_TPL,
        partial_variables={'format_instructions': format_instructions},
        input_variables=['query']
    )

    entity_chain = LLMChain(
        llm=get_llm_model(),
        prompt=entity_prompt,
        verbose=os.getenv('VERBOSE')
    )

    result = entity_chain.run({
        'query': query
    })

    entity_result = output_parser.parse(result)
    print(entity_result)
```

需要注意的是，不同的模型识别实体的能力就不一样，就个人测试而言，gpt-3.5-turbo > gpt-4o > qwen2:7b

因此，如果真的需要做产品，还是需要更大的本地模型或者直接调api

3. 接收大模型抽取的实体，填充模板CQL

在config.py中设置模板：

```python
GRAPH_TEMPLATE = {
    'award_desc': {
        'slots': ['award'],
        'question': '什么是%award%？/ %award%的具体内容是什么？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Award) 
            WHERE n.id='%award%'
            RETURN c.text AS RES
        """,
        'answer': '【%award%】的相关内容：%RES%',
    },
    'award_amount': {
        'slots': ['award'],
        'question': '%award%的金额是多少？/ %award%有多少钱？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Award) 
            WHERE n.id='%award%'
            OPTIONAL MATCH (n)-[:HAS_AMOUNT]->(m:Amount) 
            WITH n, m, c
            RETURN 
                CASE 
                    WHEN m IS NOT NULL THEN m.id
                    ELSE c.text
                END AS RES
        """,
        'answer': '【%award%】的相关信息：%RES%',
    },
    'award_condition': {
        'slots': ['award'],
        'question': '获得%award%需要满足什么条件？/ %award%怎么评定？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Award) 
            WHERE n.id='%award%'
            OPTIONAL MATCH (n)-[:REQUIRES]->(m:Condition)
            WITH n, m, c
            RETURN 
                CASE 
                    WHEN m IS NOT NULL THEN m.id
                    ELSE c.text
                END AS RES
        """,
        'answer': '【%award%】的相关信息：%RES%',
    },
    'punishment_desc': {
        'slots': ['punishment'],
        'question': '什么是%punishment%？/ %punishment%的具体内容是什么？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Punishment) 
            WHERE n.id='%punishment%'
            RETURN c.text AS RES
        """,
        'answer': '【%punishment%】的相关内容：%RES%',
    },
    'punishment_duration': {
        'slots': ['punishment'],
        'question': '%punishment%的处分期限是多久？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Punishment) 
            WHERE n.id='%punishment%'
            OPTIONAL MATCH (n)-[:HAS_DURATION]->(m:Duration)
            WITH n, m, c
            RETURN 
                CASE 
                    WHEN m IS NOT NULL THEN m.id
                    ELSE c.text
                END AS RES
        """,
        'answer': '【%punishment%】的相关信息：%RES%',
    },
    'violation_desc': {
        'slots': ['violation'],
        'question': '什么是%violation%？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Violation) 
            WHERE n.id='%violation%'
            RETURN c.text AS RES
        """,
        'answer': '【%violation%】的相关内容：%RES%',
    },
    'violation_punishment': {
        'slots': ['violation'],
        'question': '%violation%会受到什么处分？/ %violation%怎么处理？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Violation) 
            WHERE n.id='%violation%'
            OPTIONAL MATCH (n)-[:LEADS_TO]->(m:Punishment)
            WITH n, m, c
            RETURN 
                CASE 
                    WHEN m IS NOT NULL THEN m.id
                    ELSE c.text
                END AS RES
        """,
        'answer': '【%violation%】的相关信息：%RES%',
    },
    'department_desc': {
        'slots': ['department'],
        'question': '%department%是做什么的？/ %department%的职责是什么？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Department) 
            WHERE n.id='%department%'
            RETURN c.text AS RES
        """,
        'answer': '【%department%】的相关内容：%RES%',
    },
    'process_desc': {
        'slots': ['process'],
        'question': '%process%的流程是什么？/ %process%怎么操作？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Process) 
            WHERE n.id='%process%'
            RETURN c.text AS RES
        """,
        'answer': '【%process%】的相关内容：%RES%',
    },
    'honor_desc': {
        'slots': ['honor'],
        'question': '什么是%honor%？/ %honor%是什么荣誉？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Honor) 
            WHERE n.id='%honor%'
            RETURN c.text AS RES
        """,
        'answer': '【%honor%】的相关内容：%RES%',
    },
    'honor_condition': {
        'slots': ['honor'],
        'question': '获得%honor%需要满足什么条件？/ 怎么才能获得%honor%？',
        'cypher': """
            MATCH (c:Chunk)-[:HAS_ENTITY]->(n:Honor) 
            WHERE n.id='%honor%'
            OPTIONAL MATCH (n)-[:REQUIRES]->(m:Condition)
            WITH n, m, c
            RETURN 
                CASE 
                    WHEN m IS NOT NULL THEN m.id
                    ELSE c.text
                END AS RES
        """,
        'answer': '【%honor%】的相关信息：%RES%',
    }
}
```

先针对以上代码的`%xxx%`占位符，在utils.py中新增文本处理函数：

```python
# 更换词槽的 %%
def replace_token_in_string(string, slots):
    for key, value in slots:
        string = string.replace('%' + key + '%', value)
    return string
```

在agent.py修改：

```python
def graph_func(self, query):
    # 命名实体识别
    response_schemas = [
            ResponseSchema(type='list', name='award', description='奖学金、奖励类实体'),
            ResponseSchema(type='list', name='amount', description='金额、数值实体'),
            ResponseSchema(type='list', name='condition', description='获得奖励或处分的条件实体'),
            ResponseSchema(type='list', name='department', description='学校相关部门实体'),
            ResponseSchema(type='list', name='document', description='相关文件、规定实体'),
            ResponseSchema(type='list', name='duration', description='处分、奖励期限实体'),
            ResponseSchema(type='list', name='honor', description='荣誉称号实体'),
            ResponseSchema(type='list', name='organization', description='组织机构实体'),
            ResponseSchema(type='list', name='process', description='评定、处理流程实体'),
            ResponseSchema(type='list', name='punishment', description='处分类实体'),
            ResponseSchema(type='list', name='violation', description='违纪行为实体'),
        ]

    output_parser = StructuredOutputParser(response_schemas=response_schemas)
    format_instructions = structured_output_parser(response_schemas)

    entity_prompt = PromptTemplate(
        template=ENTITY_PROMPT_TPL,
        partial_variables={'format_instructions': format_instructions},
        input_variables=['query']
    )

    entity_chain = LLMChain(
        llm=get_llm_model(),
        prompt=entity_prompt,
        verbose=os.getenv('VERBOSE')
    )

    result = entity_chain.run({
        'query': query
    })

    entity_result = output_parser.parse(result)
    print(entity_result)

    # 实体填充模板
    graph_templates = []
    for key, template in GRAPH_TEMPLATE.items():
        slot = template['slots'][0]
        slot_values = entity_result[slot]
        for value in slot_values:
            graph_templates.append({
                'question': replace_token_in_string(template['question'], [[slot, value]]),
                'cypher': replace_token_in_string(template['cypher'], [[slot, value]]),
                'answer': replace_token_in_string(template['answer'], [[slot, value]]),
            })
    if not graph_templates:
        return

    # 筛选相关问题
    graph_documents = [  # 用替换完的问题进行筛选
        Document(page_content=template['question'], metadata=template)  for template in graph_templates
    ]
    db = FAISS.from_documents(graph_documents, get_embeddings_model())
    graph_documents_filter = db.similarity_search_with_relevance_scores(query, k=3)
```

4. 有了CQL之后，我们就可以对neo4j进行查询了

首先修改.env文件：

```env
NEO4J_URI='neo4j://localhost:7687'
NEO4J_USERNAME='neo4j'
NEO4J_PASSWORD='12345678'
```

其次在utils.py中增加连接neo4j的代码：

```python
def get_neo4j_conn():
    return Graph(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
```

接下来，可以让agent执行CQL了：

```python
def graph_func(self, query):
    # ... 以上省略
    # 拿到Document.meta.cypher，执行CQL
    query_result = []
    neo4j_conn = get_neo4j_conn()
    for document in graph_documents_filter:
        question = document[0].page_content
        cypher = document[0].metadata['cypher']
        answer = document[0].metadata['answer']
        try:
            result = neo4j_conn.run(cypher).data()
            if result and any(value for value in result[0].values()):
                answer_str = replace_token_in_string(answer, list(result[0].items()))
                query_result.append(f'问题：{question}\n答案：{answer_str}')
        except:
            pass
```

现在我们得到了CQL的执行结果，可以继续让大模型总结回答：

```python
# propmt.py
GRAPH_PROMPT_TPL = '''
请根据以下检索结果，回答用户问题，不要发散和联想内容。
检索结果中没有相关信息时，回复“不知道”。
----------
检索结果：
{query_result}
----------
用户问题：{query}
'''
```

```python
# agent.py
def graph_func(self, query):
    # 得到CQL查询结构后回答
    prompt = PromptTemplate.from_template(GRAPH_PROMPT_TPL)
    graph_chain = LLMChain(
        llm=get_llm_model(),
        prompt=prompt,
        verbose=os.getenv('VERBOSE')
    )
    inputs = {
        'query': query,
        'query_result': '\n\n'.join(query_result) if len(query_result) else '没有查到'
    }
    return graph_chain.run(inputs)
```