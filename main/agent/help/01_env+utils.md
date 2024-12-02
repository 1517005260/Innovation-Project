# 模型环境变量与模型获取函数

1. 环境配置：

参见[one-api解决方案](https://github.com/1517005260/ai-learning/tree/master/langchain)

```env
OPENAI_API_KEY = 'sk-6n3IuwDfeMEZggn2A61a818dC722474292D929C27004Fe82'
OPENAI_BASE_URL = 'http://localhost:13000/v1'

OPENAI_EMBEDDINGS_MODEL = 'm3e'
OPENAI_LLM_MODEL = 'qwen2:7b'

TEMPERATURE = 0
MAX_TOKENS = 2000

VERBOSE = True
```

2. python环境：[requirements.txt](../requiremets.txt)

3. 创建utils.py，定义模型获取函数

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

import os
from dotenv import load_dotenv

load_dotenv()


def get_embeddings_model():
    model = OpenAIEmbeddings(model=os.getenv('OPENAI_EMBEDDINGS_MODEL'))
    return model


def get_llm_model():
    model = ChatOpenAI(
        model=os.getenv('OPENAI_LLM_MODEL'),
        temperature=os.getenv('TEMPERATURE'),
        max_tokens=os.getenv('MAX_TOKENS'),
    )
    return model


# 测试
if __name__ == '__main__':
    llm = get_llm_model()
    print(llm.predict("你好"))
```