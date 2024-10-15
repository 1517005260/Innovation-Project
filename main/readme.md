# 基于GraphRAG的问答

[参考仓库](https://github.com/NanGePlus/GraphragTest)

1. oneapi的安装

直接在wsl中：

```bash
docker run --name one-api -d --restart always -p 13000:3000 -e TZ=Asia/Shanghai -v /home/ubuntu/data/one-api:/data justsong/one-api
```

2. 大模型的选择：本地+在线api

本地采用ollama中转，在线api采用[阿里云-通义千问](https://bailian.console.aliyun.com/#/efm/model_experience_center/text)

3. 环境安装，见requirements.txt

```bash
conda create -n graphrag
conda activate graphrag
pip insatll -r requirements.txt
## 如果报错“no module named 'past'"，需要 pip install future
```

4. GraphRAG构建
- 进入graphrag文件夹中，建立文件夹`input,inputs,cache`
- 准备txt文件，放入input文件夹下
- 初始化GraphRAG，`python -m graphrag.index --init --root ./`
- 进入`.env`文件修改oneapi对接的配置，`settiings.yaml`需要有多处修改，主要是修改对接openapi的模型配置和api-base的配置
- 优化提示词，`python -m graphrag.prompt_tune --config ./settings.yaml --root ./ --no-entity-types --language Chinese --output ./prompts`
- 索引构建，`python -m graphrag.index --root ./`，需要较长时间

5. 对GraphRAG的构建初步测试
- 新建文件夹`utils`，在其中测试即可

1） 启动`main.py`，让后台服务在端口8012监听前端问题请求，如果没有问题，会有如下提示

```bash
2024-10-13 13:32:42,158 - __main__ - INFO - 在端口 8012 上启动服务器
INFO:     Started server process [3755525]
INFO:     Waiting for application startup.
2024-10-13 13:32:42,169 - __main__ - INFO - 正在初始化搜索引擎和问题生成器...
2024-10-13 13:32:42,169 - __main__ - INFO - 正在设置LLM和嵌入器
2024-10-13 13:32:42,774 - __main__ - INFO - LLM和嵌入器设置完成
2024-10-13 13:32:42,774 - __main__ - INFO - 正在加载上下文数据
[2024-10-13T05:32:43Z WARN  lance::dataset] No existing dataset at /home/ggg/project/Innovation-Project/main/graphrag/utils/../inputs/artifacts/lancedb/entity_description_embeddings.lance, it will be created
2024-10-13 13:32:43,549 - __main__ - INFO - 声明记录数: 112
2024-10-13 13:32:43,549 - __main__ - INFO - 上下文数据加载完成
2024-10-13 13:32:43,550 - __main__ - INFO - 正在设置搜索引擎
2024-10-13 13:32:43,550 - __main__ - INFO - 搜索引擎设置完成
2024-10-13 13:32:43,550 - __main__ - INFO - 初始化完成
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8012 (Press CTRL+C to quit)

```

2） 启动`apiTest.py`，在其中修改提问方式（global/local）、提问内容。此时可以观察`main.py`的后台推理过程。

6. 安装neo4j
- 详见`docker-compose`文件以及`neo4j`文件夹，注意一定要有apoc插件，否则之后会报错
- 直接`docker compose up`即可，neo4j的用户名和登录密码可以在`docker-compose`文件中修改
- neo4j的数据会存在data/下

7. 知识图谱可视化
- 进入`graphrag/utils`文件夹，运行neo4jTest.py即可
- 登录Neo4j，即可查看可视化图谱

7.1 使用[这份代码](./graphrag/utils/my_visualize.py)进行知识图谱可视化，最后可以在本地的某个端口（例如 http://127.0.0.1:44465）访问