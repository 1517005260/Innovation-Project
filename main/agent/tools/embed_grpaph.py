import os
from neo4j import GraphDatabase, Result
import pandas as pd
from typing import Dict, Any
import re
from tqdm import tqdm
import time
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
EMBED_DIM = 1536

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def db_query(cypher: str, params: Dict[str, Any] = {}) -> pd.DataFrame:
    return driver.execute_query(
        cypher, parameters_=params, result_transformer_=Result.to_df
    )


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    text = ' '.join(text.split())
    return text.strip()


def preprocess_embeddings(session, embed_model, max_retries=3):
    result = session.run("""
        MATCH (n:__Entity__)
        WHERE n.description_embedding IS NULL
        RETURN n.id as id, 
               CASE 
                   WHEN n.description IS NOT NULL AND n.description <> '' 
                   THEN n.description 
                   ELSE n.name 
               END as text
    """)
    records = list(result)
    total = len(records)
    failed_nodes = []

    if total > 0:
        print(f"开始为 {total} 个节点添加 embedding")
        pbar = tqdm(records, total=total, desc="处理进度")
        for record in pbar:
            retries = 0
            node_id = record["id"]

            text = clean_text(record["text"])
            if not text:
                print(f"\n节点 {node_id} 文本无效(description和name都为空)，跳过")
                failed_nodes.append((node_id, "文本无效"))
                continue

            while retries < max_retries:
                try:
                    embedding = embed_model.get_text_embedding(text)
                    session.run("""
                        MATCH (n:__Entity__ {id: $id})
                        SET n.description_embedding = $embedding
                    """, {"id": node_id, "embedding": embedding})
                    break
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        error_msg = str(e)
                        print(f"\n节点 {node_id} 处理失败: {error_msg[:100]}...")
                        failed_nodes.append((node_id, error_msg))
                    else:
                        time.sleep(2)

    if failed_nodes:
        print("\n处理失败的节点:")
        for node_id, error in failed_nodes:
            print(f"ID: {node_id}, 错误: {error[:100]}...")

    return total, len(failed_nodes)


def setup_vector_index(index_name="entity"):
    db_query(
        """
    CREATE VECTOR INDEX """
        + index_name
        + """ IF NOT EXISTS FOR (e:__Entity__) ON e.description_embedding
    OPTIONS {indexConfig: {
     `vector.dimensions`: 1536,
     `vector.similarity_function`: 'cosine'
    }}
    """
    )

    db_query(
        """
    MATCH (n:`__Community__`)<-[:IN_COMMUNITY]-()<-[:HAS_ENTITY]-(c)
    WITH n, count(distinct c) AS chunkCount
    SET n.weight = chunkCount"""
    )


if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "sk-6n3IuwDfeMEZggn2A61a818dC722474292D929C27004Fe82"
    os.environ["OPENAI_BASE_URL"] = "http://localhost:13000/v1"

    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.vector_stores.neo4jvector import Neo4jVectorStore

    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_base="http://localhost:13000/v1"
    )

    setup_vector_index()

    neo4j_vector = Neo4jVectorStore(
        NEO4J_USERNAME,
        NEO4J_PASSWORD,
        NEO4J_URI,
        EMBED_DIM,
        index_name="entity"
    )

    with neo4j_vector._driver.session() as session:
        total, failed = preprocess_embeddings(session, embed_model)
        print(f"\n处理完成: 共 {total} 个节点, 失败 {failed} 个")