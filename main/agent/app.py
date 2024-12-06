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