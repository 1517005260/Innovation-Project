# 大创寒假安排

**干不完不要急，大创结题半年至一年半，最好一年左右，学不完不要着急，能看多少看多少。**
所有的内容在B站都可以搜到

## 1. 基础线-AI

1.1 上次发的那本书《大规模语言模型：从理论到实践》可以大概看看，当作字典（有数学内容），不接受电子书的可以上京东，50块一本

1.2 Python入门
   - 有C语言基础2天就能看完语法，大概有个印象就行，不放心的可以上各种刷题网站写点语法题

1.3 PyTorch入门
   - 选了个尽可能短的视频 [链接](https://www.bilibili.com/video/BV1aT41147p2/?spm_id_from=333.999.0.0)

大模型入门就看PyTorch和Transformer，学的时候要有目录意识，东西太多了，先大概搭个框架，知道大模型、机器学习、深度学习、NLP有哪些内容即可，不要每个知识点学过去，效率太低了。建议先做项目，不会就查，我们只要知道要查的知识点是什么即可。项目可以上Github找，或者在B站、油管上找“动手微调大模型”等视频看看

现在GLM4已经发布，可以自行体验。如果没有GPT4的话就用这个，个人用下来反正中文能力肯定比GPT3.5强 [链接](https://chatglm.cn/main/alltoolsdetail)  
不嫌麻烦翻的且有Google账号的，可以上字节跳动搭的网站 [www.coze.com](www.coze.com) 用GPT4助手
GPT4 共享网站 [链接](https://chat-shared3.zhile.io/shared.html?v=2)  带黄光的是4，其他是3.5 免翻
上述学下来有问题（尤其是计算机相关）先问AI，大概率就能解决

如果想系统学理论（个人不推荐，因为太慢了，但是觉得像上面这么学不扎实的可参考）上阿里天池 [链接](https://tianchi.aliyun.com/course?spm=a2c22.27080692.J_3941670930.8.31fe5699DDrQrf)

## 2. 基础线-工程能力-搭网站

搭项目的常见框架（后端）:
- Python: Django   
- Java: SpringBoot

这两个框架选一个先学着就行，但是大家要统一学一个

前端搭网站：先学HTML，CSS，JavaScript三个语言。这三个语言没有难度，所见即所得，大家可以先用前端入工程的门，比较简单，框架如Vue和React可以放在后面学。

这两个B站一搜一大堆视频，挑个顺眼的看就行
一定要自己动手，动手优先级比听课高

## 3. 项目线

**有任何报错问AI**

### Ⅰ 动手前确保
1. 网络环境
2. 显存 >= 6G 
   - 查看方式
     - <win>+R
     - cmd
     - nvidia-smi
   - 看到“6144MiB”等字样就是显存，6144MiB = 6G左右

如果没有相关环境，租显卡网站:
1. AutoDL: 缺点是人太多了，抢不到GPU，而且之后会发现http的请求是无法访问的，比较麻烦，推荐用于微调模型用，优点是便宜
2. [https://featurize.cn/vm/available](https://featurize.cn/vm/available): 最近发现的，还没用过，可以试试
3. [http://gpu.ai-galaxy.cn/store?application=AI%E4%BA%91%E4%B8%BB%E6%9C%BA](http://gpu.ai-galaxy.cn/store?application=AI%E4%BA%91%E4%B8%BB%E6%9C%BA): 优点是有Windows镜像，如果不熟悉Linux可以用，缺点是一次性租用。当你要把关掉的主机再次启动时，需要付至少30块

### Ⅱ 部署模型（非C盘）

虽然之前大创上报的是ChatGLM3-6B，但是后来发现有更小的模型（而且GLM4貌似不会开源了），对显存的需求更低，这里推荐通义千问的模型，模型参数只有1.8B 
现在Qwen据说马上要出第二代了，出了之后模型可以更新
猎户座Orion-14B昨天发布了，可以在云平台部署，如果显存够的话可以部署int4版本在本地。可以上GitHub参考 [链接](https://github.com/OrionStarAI/Orion?tab=readme-ov-file)
体验网址 [链接](https://modelscope.cn/studios/OrionStarAI/Orion-14B-App-Demo/summary)
模型权重基本都可以在Hugging Face上下载到，用不了git clone就手动

下载，实在不行找我我网盘分享给你
如果网络环境不佳，可以选择到国内网站下载，不去Hugging Face：[https://modelscope.cn](https://modelscope.cn)

### Ⅲ 本机WSL + 配环境

（不用本地部署的可以略去这一步  云平台上应该提供了配好的Linux环境   云平台的直接跳转到第8步）
WSL即Windows下的Linux虚拟主机
WSL安装：这个视频发行版不一样，建议新手换成Ubuntu：[链接](https://www.bilibili.com/video/BV1Fx4y1j7yy/?spm_id_from=333.337.search-card.all.click&vd_source=b6823bc44ae781b7c43717114fe04aad)
装完之后记得迁移到非C盘
然后Python解释器，上官网即可 [链接](https://www.bilibili.com/video/BV1ok4y1t7XC/?spm_id_from=333.337.search-card.all.click&vd_source=b6823bc44ae781b7c43717114fe04aad)
视频不一定都是OK的，有任何不会的一定要问AI，记得开AI的联网功能
Docker安装：直接在官网下Windows桌面版即可：[链接](https://docs.docker.com/desktop/install/windows-install/)
最后开始装深度学习的环境
1. Miniconda：[链接](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)
2. 下载VSCode
3. 进入WSL的界面
4. `pip install` 各种包
   - 各种包 = scikit-learn，numpy，pandas ，tqdm，lightgbm ，nibabel，pillow
   - 下载的时候要VPN
5. `nvidia-smi`查看CUDA版本号，这代表你的电脑所支持的最高版本号，下载的时候只能选<=这个数字的CUDA
   - [链接](https://www.bilibili.com/video/BV1dd4y1k7Ru/?spm_id_from=333.337.search-card.all.click&vd_source=b6823bc44ae781b7c43717114fe04aad)
6. PyTorch：[链接](https://pytorch.org/get-started/locally/)
7. 飞桨：[链接](https://www.paddlepaddle.org.cn)
8. 验证：
   - 命令行中键入：`python3`
   - `import paddle`
   - `paddle.utils.run_check()`
     - 应输出：`PaddlePaddle works well on 1 GPU. PaddlePaddle is installed successfully! Let's start deep learning with PaddlePaddle now.`
   - `import torch`
   - `torch.cuda.is_available()`
     - 应输出：`True`

### Ⅳ 接入微信

项目部署 [链接](https://github.com/zhayujie/chatgpt-on-wechat)
命令行新建Python环境 
```
cd chatgpt-on-wechat
pip3 install -r requirements.txt
pip3 install -r requirements-optional.txt
```
FastGPT官网 [链接](https://fastgpt.run/?hiId=64e84f9a1d45b666f8994d56)
注册后进入“应用”-“新建一个应用”-配置AI-“外部使用”-“API密钥”-“新建”
你会有类似：`https://fastgpt.run/api/v1` 的中转网址
`fastgpt-3r49exfPS5aPQZB5SrZqLKB***`的API-key
修改项目配置文件（config.json文件），
我的配置：
```json
{
  "channel_type": "wx",
  "model": "",
  "open_ai_api_key": "fastgpt-8ZIoDM7ePSUZH5VjidNCb0yhJkvwkL***",
  "text_to_image": "dall-e-2",
  "voice_to_text": "openai",
  "text_to_voice": "openai",
  "proxy": "",
  "open_ai_api_base":"https://ai.fastgpt.in/api/v1",  ##中转网址
  "hot_reload": false,
  "single_chat_prefix": [
    ""
  ],
  "single_chat_reply_prefix": "[AI] ",
  "group_chat_prefix": [
    "@bot"
  ],
  "group_name_white_list": [
    "填入机器人触发的白名单群组"（填all则对所有在群里@的消息都会进行回复）
  ],
  "group_chat_in_one_session": [ ##允许上下文联想
    "ALL_GROUP"
  ],
  "image_create_prefix": [
    "画",
    "看",
    "找"
  ],
  "speech_recognition": false,
  "group_speech_recognition": false,
  "voice_reply_voice": false,
  "conversation_max_tokens": 2000,
  "expires_in_seconds": 3600,
  "character_desc": "你是ChatGPT, 一个由OpenAI训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。",
  "temperature": 0.7,
  "top_p": 1,
  "subscribe_msg": "感谢您的关注！\n这里是ChatGPT，可以自由对话。\n支持语音对话。\n支持图片输入。\n支持图片输出，画字开头的消息将按要求创作图片。\n支持tool、角色扮演和文字冒险等丰富的插件。\n输入{trigger_prefix}#help 查看详细指令。",
  "use_linkai": false,
  "linkai_api_key": "",
  "linkai_app_code": ""
}    
```

部署完成后在命令行运行
```
python app.py
```
之后扫码即可
会顶掉你在电脑上的登录状态

### Ⅴ RAG应用制作

先学习Langchain和llama index两个Python包的使用，可以在FastGPT的“知识库”部分先试试
