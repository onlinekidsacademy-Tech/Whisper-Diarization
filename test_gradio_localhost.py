import gradio as gr
def greet(name):
    return "Hello " + name + "!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
# Set a timeout for the share link
demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
