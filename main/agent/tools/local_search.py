import os
from main.agent.prompt import INDEX_QUERY, RETRIEVAL_QUERY
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.neo4jvector import Neo4jVectorStore
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

EMBED_DIM = 1536
TOP_CHUNKS = 3
TOP_COMMUNITIES = 3
TOP_OUTSIDE_RELS = 10
TOP_INSIDE_RELS = 10
TOP_ENTITIES = 10

def setup_search_engine():
    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_base="http://localhost:13000/v1"
    )
    llm = OpenAI(
        api_base="http://localhost:13000/v1",
        model="gpt-4o"
    )

    neo4j_vector = Neo4jVectorStore(
        NEO4J_USERNAME,
        NEO4J_PASSWORD,
        NEO4J_URI,
        EMBED_DIM,
        index_name="entity",
        retrieval_query=RETRIEVAL_QUERY,
        index_query=INDEX_QUERY,
    )

    return VectorStoreIndex.from_vector_store(neo4j_vector).as_query_engine(
        similarity_top_k=TOP_ENTITIES,
        embed_model=embed_model,
        llm=llm
    )


if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "sk-6n3IuwDfeMEZggn2A61a818dC722474292D929C27004Fe82"
    os.environ["OPENAI_BASE_URL"] = "http://localhost:13000/v1"

    search_engine = setup_search_engine()
    response = search_engine.query("国家奖学金的申请条件？")
    print(response)