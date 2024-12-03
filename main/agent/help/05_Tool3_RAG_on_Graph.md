# Tool 3: 基于知识图谱的RAG

## CQL 模板解决方案

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
    'award_requirements': {
        'slots': ['award'],
        'question': [
            '%award%的申请条件是什么？',
            '%award%有什么要求？',
            '想要申请%award%需要满足哪些条件？',
            '申请%award%的资格要求有哪些？',
            '%award%的评选标准是什么？',
            '谁可以申请%award%？',
            '%award%的准入条件是什么？'
        ],
        'cypher': "MATCH (n:Award)-[:REQUIRES]->(m:Condition) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的申请条件：%RES%'
    },
    'award_duration': {
        'slots': ['award'],
        'question': [
            '%award%的评选时间是什么时候？',
            '%award%什么时候开始评选？',
            '%award%的申请截止日期是？',
            '%award%评选周期是多久？',
            '%award%什么时候可以申请？',
            '%award%的发放时间是什么时候？'
        ],
        'cypher': "MATCH (n:Award)-[:HAS_DURATION]->(m:Duration) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的评选时间：%RES%'
    },
    'award_amount': {
        'slots': ['award'],
        'question': [
            '%award%的金额是多少？',
            '%award%每年发多少钱？',
            '%award%的奖励金额是多少？',
            '获得%award%可以拿到多少奖金？',
            '%award%的资助标准是多少？'
        ],
        'cypher': "MATCH (n:Award)-[:HAS_AMOUNT]->(m:Amount) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的金额：%RES%'
    },
    'award_supervisor': {
        'slots': ['award'],
        'question': [
            '%award%由哪个部门负责？',
            '%award%的主管部门是哪个？',
            '谁负责管理%award%？',
            '%award%的评审工作由谁负责？',
            '申请%award%要找哪个部门？',
            '%award%的评审机构是什么？'
        ],
        'cypher': "MATCH (n:Award)-[:SUPERVISED_BY]->(m:Department) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的负责部门：%RES%'
    },
    'violation_punishment': {
        'slots': ['violation'],
        'question': [
            '因为%violation%会受到什么处分？',
            '%violation%的处罚是什么？',
            '%violation%会有什么后果？',
            '%violation%要受到什么纪律处分？',
            '如果%violation%会怎么处理？'
        ],
        'cypher': "MATCH (n:Violation)-[:LEADS_TO]->(m:Punishment) WHERE n.id='%violation%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '因【%violation%】可能受到的处分：%RES%'
    },
    'punishment_duration': {
        'slots': ['punishment'],
        'question': [
            '%punishment%的期限是多久？',
            '%punishment%要多长时间？',
            '%punishment%持续多久？',
            '%punishment%什么时候能解除？',
            '%punishment%的处分期是多久？'
        ],
        'cypher': "MATCH (n:Punishment)-[:HAS_DURATION]->(m:Duration) WHERE n.id='%punishment%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%punishment%】的期限：%RES%'
    },
    'punishment_conditions': {
        'slots': ['punishment'],
        'question': [
            '什么情况下会受到%punishment%？',
            '哪些行为会导致%punishment%？',
            '为什么会被%punishment%？',
            '%punishment%的触发条件是什么？',
            '什么违纪行为会受到%punishment%？'
        ],
        'cypher': "MATCH (n:Punishment)<-[:LEADS_TO]-(m:Condition) WHERE n.id='%punishment%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '以下情况将受到【%punishment%】：%RES%'
    },
    'punishment_process': {
        'slots': ['punishment'],
        'question': [
            '%punishment%需要经过什么流程？',
            '%punishment%怎么执行？',
            '%punishment%的处理步骤是什么？',
            '%punishment%由谁来决定？',
            '如何实施%punishment%？'
        ],
        'cypher': "MATCH (n:Punishment)-[:REQUIRES]->(m:Process) WHERE n.id='%punishment%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%punishment%】的处理流程：%RES%'
    },
    'exclusive_awards': {
        'slots': ['award'],
        'question': [
            '%award%与哪些奖项互斥？',
            '获得%award%后还能申请什么奖？',
            '%award%和什么奖不能同时获得？',
            '申请了%award%还能申请其他奖项吗？',
            '%award%有什么相关限制？'
        ],
        'cypher': "MATCH (n:Award)-[:EXCLUSIVE_WITH]->(m:Award) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】与以下奖项互斥：%RES%'
    },
    'award_process': {
        'slots': ['award'],
        'question': [
            '%award%的评审流程是什么？',
            '%award%怎么申请？',
            '申请%award%需要准备什么材料？',
            '%award%的评选步骤是什么？',
            '怎么参加%award%的评选？'
        ],
        'cypher': "MATCH (n:Award)-[:CONSISTS_OF]->(m:Process) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的评审流程：%RES%'
    },
    'award_appeal': {
        'slots': ['award'],
        'question': [
            '%award%评选结果不满意怎么办？',
            '%award%的申诉途径是什么？',
            '对%award%结果有异议怎么处理？',
            '%award%的复议程序是什么？',
            '不服%award%评选结果找谁？'
        ],
        'cypher': "MATCH (n:Award)-[:CAN_APPEAL]->(m:Organization) WHERE n.id='%award%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%award%】的申诉渠道：%RES%'
    },
    'punishment_appeal': {
        'slots': ['punishment'],
        'question': [
            '%punishment%怎么申诉？',
            '对%punishment%不服怎么办？',
            '%punishment%的申诉程序是什么？',
            '收到%punishment%后如何上诉？',
            '%punishment%的复议渠道是什么？'
        ],
        'cypher': "MATCH (n:Punishment)-[:CAN_APPEAL]->(m:Organization) WHERE n.id='%punishment%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%punishment%】的申诉渠道：%RES%'
    },
    'condition_leads_to': {
        'slots': ['condition'],
        'question': [
            '%condition%会导致什么处分？',
            '%condition%会受到什么惩罚？',
            '%condition%的后果是什么？',
            '%condition%会有什么处理结果？',
            '如果%condition%会怎么处理？'
        ],
        'cypher': "MATCH (n:Condition)-[:LEADS_TO]->(m:Punishment) WHERE n.id='%condition%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%condition%】将导致：%RES%'
    },
    'department_manages': {
        'slots': ['department'],
        'question': [
            '%department%负责管理什么？',
            '%department%的职责是什么？',
            '%department%主管哪些事务？',
            '%department%有什么权限？',
            '%department%负责什么工作？'
        ],
        'cypher': "MATCH (n:Department)-[:MANAGES]->(m) WHERE n.id='%department%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%department%】负责管理：%RES%'
    },
    'department_evaluates': {
        'slots': ['department'],
        'question': [
            '%department%负责评估什么？',
            '%department%评价什么内容？',
            '%department%考核哪些方面？',
            '%department%评审什么？',
            '%department%如何进行评定？'
        ],
        'cypher': "MATCH (n:Department)-[:EVALUATES]->(m) WHERE n.id='%department%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%department%】负责评估：%RES%'
    },
    'organization_awards': {
        'slots': ['organization'],
        'question': [
            '%organization%有哪些奖项？',
            '%organization%设立了什么奖？',
            '%organization%颁发什么奖项？',
            '%organization%的奖励制度有哪些？',
            '%organization%评选什么奖？'
        ],
        'cypher': "MATCH (n:Organization)-[:AWARDS]->(m:Award) WHERE n.id='%organization%' RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.id) | s + '、' + x), 1) AS RES",
        'answer': '【%organization%】设立的奖项：%RES%'
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
    # ...
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

由于本方法太长，已拆分至tools包下[cql_graph_func](../tools/cql_graph_func.py)。

## LangChain解决方案

填充CQL模板的方案效果可能不是很好，这里我们让大模型自己生成CQL语句去查询数据库：

