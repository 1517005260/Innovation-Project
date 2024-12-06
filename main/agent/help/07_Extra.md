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
    return service.answer(message, history)


css = '''
.gradio-container {
    max-width: 850px !important;
    margin: 20px auto !important;
}
.message {
    padding: 10px !important;
    font-size: 14px !important;
}
.examples-row {
    margin-top: 10px !important;
}
'''

with gr.Blocks(theme=gr.themes.Default(
        spacing_size="sm",
        radius_size="sm",
        text_size="md",
        font=["'Helvetica Neue'", "sans-serif"]
)) as demo:
    gr.Markdown("# 华东理工大学政务问答小助手")

    chatbot = gr.Chatbot(
        height=400,
        bubble_full_width=False,
        show_label=False
    )

    with gr.Row():
        txt = gr.Textbox(
            placeholder="在此输入您的问题",
            container=False,
            scale=7,
            show_label=False
        )
        submit_btn = gr.Button("发送", variant="primary", scale=1)
        clear_btn = gr.Button("清空", scale=1)

    with gr.Row(elem_classes="examples-row"):
        gr.Examples(
            examples=[
                "你好，你是谁？",
                "优秀学生的申请条件是什么?",
                "国家奖学金的申请标准是什么?",
                "旷课会有什么处罚?"
            ],
            inputs=txt
        )


    def user_input(message, history):
        return "", history + [(message, None)]


    def bot_response(history):
        if not history or history[-1][1] is not None:
            return history

        message = history[-1][0]
        service = Service()
        response = service.answer(message, history[:-1])
        history[-1] = (message, response)
        return history


    submit_btn.click(
        user_input,
        [txt, chatbot],
        [txt, chatbot],
        queue=False
    ).then(
        bot_response,
        chatbot,
        chatbot
    )

    txt.submit(
        user_input,
        [txt, chatbot],
        [txt, chatbot],
        queue=False
    ).then(
        bot_response,
        chatbot,
        chatbot
    )

    clear_btn.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch()
```