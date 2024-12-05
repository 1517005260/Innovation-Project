# 用户消息的补全和总结

在收到用户消息的时候，需要先做一步总结归纳，归纳出用户的真实问题

首先我们新增提示词:

```python
SUMMARY_PROMPT_TPL = '''
请结合以下历史对话信息，和用户消息，总结出一个简洁的用户消息。
直接给出总结好的消息，不需要其他信息，注意适当补全句子中的主语等信息。
如果和历史对话消息没有关联，直接输出用户原始消息。
历史对话：
{chat_history}
-----------
用户消息：{query}
-----------
总结后的用户消息：
'''
```

新建message_process:

```python
from prompt import *
from utils import *
from agent import *

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


class Service():
    def __init__(self):
        self.agent = Agent()

    def get_summary_message(slef, message, history):
        llm = get_llm_model()
        prompt =  PromptTemplate.from_template(SUMMARY_PROMPT_TPL)
        llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=os.getenv('VERBOSE'))
        chat_history = ''
        for q, a in history[-2:]:  # 取最近两轮历史记录进行总结
            chat_history += f'问题:{q}, 答案:{a}\n'
        return llm_chain.run(query=message, chat_history=chat_history)

    def answer(self, message, history):
        if history:
            message = self.get_summary_message(message, history)
        return self.agent.query(message)


if __name__ == '__main__':
    service = Service()
    # print(service.answer('你好', []))
    print(service.answer('优秀学生的申请条件?', [
        ['你好', '你好，有什么可以帮到您的吗？']
    ]))
```

# Gradio界面

app.py:

```python
import gradio as gr
from message_process import Service
import shutup

shutup.please()


def bot(message, history):
    service = Service()
    # 获取助手的回复
    response = service.answer(message, history)
    # 将当前对话加入历史
    return history + [(message, response)]


# 自定义主题
theme = gr.themes.Default(
    spacing_size="sm",
    radius_size="sm",
    text_size="md",
    font=["'Helvetica Neue'", "sans-serif"]
)

# 自定义样式
css = """
.container {
    max-width: 850px !important;
    margin: 20px auto !important;
}
.message {
    padding: 10px !important;
    font-size: 14px !important;
}
"""

with gr.Blocks(theme=theme, css=css) as demo:
    gr.Markdown("# 华东理工大学政务问答小助手")

    chatbot = gr.Chatbot(
        height=400,
        bubble_full_width=False,
        show_label=False,
        container=True
    )

    with gr.Row():
        txt = gr.Textbox(
            placeholder="在此输入您的问题",
            container=False,
            scale=7,
            show_label=False
        )
        submit_btn = gr.Button("提交", variant="primary")

    with gr.Row():
        clear_btn = gr.Button("清空记录")

    examples = [
        "你好，你是谁？",
        "优秀学生的申请条件是什么?",
        "国家奖学金的申请标准是什么?",
        "旷课会有什么处罚?"
    ]
    gr.Examples(
        examples=examples,
        inputs=txt
    )

    # 设置事件处理
    submit_btn.click(
        fn=bot,
        inputs=[txt, chatbot],
        outputs=chatbot,
        api_name="predict"
    ).then(
        fn=lambda: "",
        outputs=txt
    )

    # 清空按钮将历史设置为空列表
    clear_btn.click(lambda: [], None, chatbot, queue=False)

    # 支持回车发送
    txt.submit(
        fn=bot,
        inputs=[txt, chatbot],
        outputs=chatbot
    ).then(
        fn=lambda: "",
        outputs=txt
    )

if __name__ == "__main__":
    demo.launch(share=True)
```