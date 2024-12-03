# 基于GraphRAG的问答

[参考仓库](https://github.com/NanGePlus/GraphRAGTestV040)

1. oneapi的安装

直接在wsl中：

```bash
docker run --name one-api -d --restart always -p 13000:3000 -e TZ=Asia/Shanghai -v /home/ubuntu/data/one-api:/data justsong/one-api
```

2. 大模型的选择：本地+在线api

本地采用ollama中转，在线api采用[阿里云-通义千问](https://bailian.console.aliyun.com/#/efm/model_experience_center/text)，主分支采用api，ollama请参见ollama分支

3. 环境安装，见requirements.txt

```bash
conda create -n graphrag python==3.11
conda activate graphrag
pip insatll -r requirements.txt
## 如果报错“no module named 'past'"，需要 pip install future
```

4. GraphRAG构建
- 进入graphrag文件夹中，建立文件夹`input`
- 准备txt文件，放入input文件夹下
- 初始化GraphRAG，`graphrag init --root ./`（如果已经构建完成请忽略此步）
- 进入`.env`文件修改oneapi对接的配置，`settiings.yaml`需要有多处修改，主要是修改对接openapi的模型配置和api-base的配置
  - entity_types 也要针对不同文件进行修改，我这里为：`[award, amount, condition, department, duration, honor, organization, process, punishment, violation]`
- 优化提示词，`python -m graphrag prompt-tune --config ./settings.yaml --root ./ --language Chinese --output ./prompts`
- 索引构建，`graphrag index --root ./`，需要较长时间

5. 对GraphRAG的构建初步测试

**5.1** 新建文件夹`utils`，在其中测试即可

需要修改的配置：LLM-Model，Embedding-Model，文件路径

1） 启动`main.py`，让后台服务在端口8012监听前端问题请求，如果没有问题，会有如下提示

```bash
/home/ggg/miniconda3/bin/conda run -n graphrag --no-capture-output python /home/ggg/project/new/Innovation-Project/main/graphrag/graphrag/utils/main.py 
2024-11-25 18:04:06,751 - __main__ - INFO - 在端口 8012 上启动服务器
INFO:     Started server process [950920]
INFO:     Waiting for application startup.
2024-11-25 18:04:06,763 - __main__ - INFO - 正在初始化搜索引擎和问题生成器...
2024-11-25 18:04:06,763 - __main__ - INFO - 正在设置LLM和嵌入器
2024-11-25 18:04:07,511 - __main__ - INFO - LLM和嵌入器设置完成
2024-11-25 18:04:07,511 - __main__ - INFO - 正在加载上下文数据
2024-11-25 18:04:07,788 - __main__ - INFO - 声明记录数: 72
2024-11-25 18:04:07,789 - __main__ - INFO - 上下文数据加载完成
2024-11-25 18:04:07,791 - __main__ - INFO - 正在设置搜索引擎
2024-11-25 18:04:07,791 - __main__ - INFO - 搜索引擎设置完成
2024-11-25 18:04:07,791 - __main__ - INFO - 初始化完成
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8012 (Press CTRL+C to quit)
```

2） 启动`apiTest.py`，在其中修改提问方式（global/local）、提问内容。此时可以观察`main.py`的后台推理过程。

**5.2** 命令行测试：

```bash
graphrag query --root ./ --method global --query "{你的问题}"
graphrag query --root ./ --method local --query "{你的问题}"
graphrag query --root ./ --method drift --query "{你的问题}"
```

6. 安装neo4j

**docker安装**
- 详见`docker-compose`文件以及`neo4j`文件夹，注意一定要有apoc插件，否则之后会报错
- 直接`docker compose up -d`即可，neo4j的用户名和登录密码可以在`docker-compose`文件中修改
- neo4j的数据会存在`./data/`下

**本地安装community版本**：参考此[教程](https://github.com/1517005260/ai-learning/tree/master/langchain/graph)

7. 知识图谱可视化
- 进入`graphrag/utils`文件夹，运行neo4jTest.py即可
- 登录Neo4j，即可查看可视化图谱

查询示例：

```cypher
MATCH (n:__Entity__)
WHERE n.name CONTAINS '唐僧'
RETURN n LIMIT 25;
```

select *：

```cypher
MATCH (n) RETURN n;
```

清空节点：

```cypher
MATCH (n)
DETACH DELETE n;
```

8. 增量更新：

修改graphrag/input下的文件，修改setting.yaml:

```yaml
update_index_storage: # Storage to save an updated index (for incremental indexing). Enabling this performs an incremental index run
   type: file # or blob 
   base_dir: "update_output"  # 打开这两行被注释的代码
  # connection_string: <azure_blob_storage_connection_string>
  # container_name: <azure_blob_storage_container_name>
```

继续：`graphrag index --root ./`

可视化脚本中修改：

```python
# 指定Parquet文件路径
# 首次更新
# GRAPHRAG_FOLDER="../output"
# 增量更新
GRAPHRAG_FOLDER="../update_output"
```