from typing import List, Dict
from main.agent.prompt import MAP_SYSTEM_PROMPT, REDUCE_SYSTEM_PROMPT
import os
from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

llm = ChatOpenAI(model="gpt-4o")

map_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            MAP_SYSTEM_PROMPT,
        ),
        (
            "human",
            "{question}",
        ),
    ]
)

map_chain = map_prompt | llm | StrOutputParser()

reduce_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            REDUCE_SYSTEM_PROMPT,
        ),
        (
            "human",
            "{question}",
        ),
    ]
)
reduce_chain = reduce_prompt | llm | StrOutputParser()

graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    refresh_schema=False,
)

response_type: str = "multiple paragraphs"


def global_retriever(query: str, level: int, response_type: str = response_type) -> str:
    community_data = graph.query(
        """
    MATCH (c:__Community__)
    WHERE c.level = $level
    RETURN c.full_content AS output
    """,
        params={"level": level},
    )
    intermediate_results = []
    for community in tqdm(community_data, desc="Processing communities"):
        intermediate_response = map_chain.invoke(
            {"question": query, "context_data": community["output"]}
        )
        intermediate_results.append(intermediate_response)
    # 综合每片回答
    final_response = reduce_chain.invoke(
        {
            "report_data": intermediate_results,
            "question": query,
            "response_type": response_type,
        }
    )
    return final_response


if __name__ == "__main__":
    print(global_retriever("国家奖学金的评选条件是什么？", 2))