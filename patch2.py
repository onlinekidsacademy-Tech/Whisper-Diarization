import re

app_py = "/workspace/whisper-diarization/app.py"
with open(app_py, "r") as f:
    content = f.read()

# Remove the broken custom checkbox CSS
content = re.sub(r'input\[type="checkbox"\].*?transform: rotate\(45deg\) !important;\n\}', '', content, flags=re.DOTALL)

# Fix the @import warning (Move it or remove it, Gradio doesn't like generic @import in CSS string, we can use theme fonts instead which we already do)
content = content.replace("@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');", "")

# Ensure the File upload component is rendered correctly and visible.
content = content.replace('height=100', '')

# add allowed_paths to launch() if needed
content = content.replace("demo.launch(server_name=", "demo.launch(allowed_paths=['/workspace/whisper-diarization/uploads'], server_name=")

with open(app_py, "w") as f:
    f.write(content)
