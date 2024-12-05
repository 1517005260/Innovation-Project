from main.agent.utils import *
from main.agent.config import *
from main.agent.prompt import *

import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

load_dotenv(dotenv_path='../.env')


def cql_func(query):
    # 命名实体识别
    response_schemas = [
        ResponseSchema(type='list', name='award', description='奖学金、奖励类实体'),
        ResponseSchema(type='list', name='amount', description='金额、数字实体'),
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
        Document(page_content=template['question'], metadata=template) for template in graph_templates
    ]
    db = FAISS.from_documents(graph_documents, get_embeddings_model())
    graph_documents_filter = db.similarity_search_with_relevance_scores(query, k=3)

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
    exit()
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
