from utils import *
from config import *
from prompt import *

import os
from langchain.chains import LLMChain, LLMRequestsChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores.faiss import FAISS
from langchain.schema import Document
from langchain.agents import ZeroShotAgent, AgentExecutor, Tool
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import ResponseSchema, StructuredOutputParser


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
        # 命名实体识别
        response_schemas = [
            ResponseSchema(type='list', name='award', description='奖学金、奖励类实体，例如[国家奖学金]'),
            ResponseSchema(type='list', name='amount', description='金额、数字实体，例如[80分，100元]'),
            ResponseSchema(type='list', name='condition', description='获得奖励或处分的条件实体，例如[考得90分以上]'),
            ResponseSchema(type='list', name='department', description='学校相关部门实体，例如[教务处]'),
            ResponseSchema(type='list', name='document', description='相关文件、规定实体，例如[xxx文件]，尤其附带了书名号'),
            ResponseSchema(type='list', name='duration', description='处分、奖励期限实体，例如[6个月]'),
            ResponseSchema(type='list', name='honor', description='荣誉称号实体，例如[优秀学生]'),
            ResponseSchema(type='list', name='organization', description='组织机构实体，例如[评审委员会]'),
            ResponseSchema(type='list', name='process', description='评定、处理流程实体，例如[德育素质考核]'),
            ResponseSchema(type='list', name='punishment', description='处分类实体，例如[记过，警告]'),
            ResponseSchema(type='list', name='violation', description='违纪行为实体，例如[打架斗殴]'),
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


if __name__ == '__main__':
    agent = Agent()
    # print(agent.generic_func("你是谁？"))
    # print(agent.retrival_func('优秀学生申请条件？'))
    # print(agent.retrival_func('应该怎么联系教务处领导？'))
    print(agent.graph_func('优秀学生是什么'))
