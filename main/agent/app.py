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