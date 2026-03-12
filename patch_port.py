app_py = "/workspace/whisper-diarization/app.py"
with open(app_py, "r") as f: content = f.read()
content = content.replace("server_port=7860", "server_port=8888")
with open(app_py, "w") as f: f.write(content)
