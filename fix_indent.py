app_py = "/workspace/whisper-diarization/app.py"
with open(app_py, "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 's_au = gr.Audio(type="filepath"' in line:
        # Force 28 spaces for this block since the previous line s_url was indented at 28 spaces
        new_lines.append(28 * " " + 's_au = gr.Audio(type="filepath", label="Upload Audio / Video")\n')
    elif 's_btn = gr.Button("✨ Start Transcription"' in line:
        new_lines.append(28 * " " + 's_btn = gr.Button("✨ Start Transcription", variant="primary", size="lg")\n')
    elif 's_url = gr.Textbox(' in line:
        new_lines.append(28 * " " + 's_url = gr.Textbox(label="Or provide a direct URL (e.g., S3 link)", placeholder="https://...")\n')
    else:
        new_lines.append(line)

with open(app_py, "w") as f:
    f.writelines(new_lines)

print("Indentation fixed.")
