import re

app_py = "/workspace/whisper-diarization/app.py"

with open(app_py, "r") as f:
    content = f.read()

content = content.replace(", show_copy_button=True", "")

with open(app_py, "w") as f:
    f.write(content)
