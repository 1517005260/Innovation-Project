# Langchain 版本升级

由于引入了graphrag相关组件，这里需要对langchain相关代码进行升级:

```python
# utlis.py
# 旧版本
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

# 新版本
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

# data_process.py
# 旧版本
from langchain.vectorstores.chroma import Chroma
from langchain.document_loaders import CSVLoader, PyMuPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 新版本
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import CSVLoader, PyMuPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# agent.py
# 旧版本
from langchain.chains import LLMChain, LLMRequestsChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores.faiss import FAISS
from langchain.schema import Document
from langchain.agents import ZeroShotAgent, AgentExecutor, Tool
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

# 新版本
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain.chains import LLMChain, LLMRequestsChain
from langchain.agents import ZeroShotAgent, AgentExecutor, Tool
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_community.vectorstores import Chroma, FAISS

# tools.cql_graph_func.py
# 旧版本
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores.faiss import FAISS
from langchain.schema import Document
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

# 新版本
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
```