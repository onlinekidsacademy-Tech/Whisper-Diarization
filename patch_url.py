import re

app_py = "/workspace/whisper-diarization/app.py"
with open(app_py, "r") as f:
    content = f.read()

# 1. Update single_process to accept a URL parameter
old_single_def = r"def single_process\((.*?)\):"
new_single_def = r"def single_process(\1, url=None):"
content = re.sub(old_single_def, new_single_def, content)

# 2. Add URL downloading logic at the start of single_process
old_logic = r"    if not s_au:\s*return \[.*?\]"
new_logic = """    import urllib.request
    import os
    import tempfile
    
    if url and url.strip():
        try:
            # Download the file from URL
            temp_dir = tempfile.mkdtemp()
            # Try to guess extension, default to mp4 since user example is mp4
            ext = ".mp4" if ".mp4" in url else ".wav"
            downloaded_file = os.path.join(temp_dir, f"downloaded_audio{ext}")
            urllib.request.urlretrieve(url.strip(), downloaded_file)
            s_au = downloaded_file
        except Exception as e:
            return ["", f"Error downloading from URL: {str(e)}", None]
            
    if not s_au:
        return ["", "No audio file or URL provided.", None]"""

content = re.sub(old_logic, new_logic, content)

# 3. Update the UI layout to include the URL textbox
old_ui = r"s_au = gr\.Audio\(type=\"filepath\", label=\"Upload Audio / Video\"\)\s*s_btn = gr\.Button\(\"✨ Start Transcription\""
new_ui = """                        s_url = gr.Textbox(label="Or provide a direct URL (e.g., S3 link)", placeholder="https://...")
                            s_au = gr.Audio(type="filepath", label="Upload Audio / Video")
                            s_btn = gr.Button("✨ Start Transcription", variant="primary", size="lg")"""
content = re.sub(old_ui, new_ui, content)

# 4. Update the click handler for single_process
old_click = r"s_btn\.click\(fn=single_process, inputs=\[s_au, lang_dd, su_cb, d_dd, ns_cb, w_dd\], outputs=\[s_txt, s_log, s_srt\]\)"
new_click = r"s_btn.click(fn=single_process, inputs=[s_au, lang_dd, su_cb, d_dd, ns_cb, w_dd, s_url], outputs=[s_txt, s_log, s_srt])"
content = re.sub(old_click, new_click, content)

with open(app_py, "w") as f:
    f.write(content)
print("URL input patch applied.")
