import os
import shutil

app_py = "/workspace/whisper-diarization/app.py"
with open(app_py, "r") as f:
    content = f.read()

# 1. Add handle_upload function before refresh_list
upload_func = """def list_drive():"""
upload_handler = """def handle_upload(files):
    if not files: return refresh_list()
    for f in files:
        if f is None: continue
        try:
            bn = os.path.basename(f.name if hasattr(f, 'name') else f)
            dest = os.path.join(UPLOAD_DIR, bn)
            shutil.copy(f.name if hasattr(f, 'name') else f, dest)
        except Exception as e:
            print("Upload error:", e)
    return refresh_list()

def list_drive():"""
content = content.replace(upload_func, upload_handler)

# 2. Fix Checkbox CSS
old_css = """.checkbox-group .wrap {
    border: 1px solid #1a1a1a !important;"""
new_css = """.checkbox-group .wrap {
    border: 1px solid #333 !important;
    background: #0d0d0d !important;
    border-radius: 8px !important;"""
content = content.replace(old_css, new_css)

old_check = """input[type="checkbox"] {
    width: 16px !important; height: 16px !important;"""
new_check = """input[type="checkbox"] {
    width: 18px !important; height: 18px !important;
    border: 2px solid #555 !important;
    border-radius: 4px !important;
    cursor: pointer !important;
    appearance: none !important;
    -webkit-appearance: none !important;
    background-color: #111 !important;
    position: relative !important;
}
input[type="checkbox"]:checked {
    background-color: #ffffff !important;
    border-color: #ffffff !important;
}
input[type="checkbox"]:checked::after {
    content: '' !important;
    position: absolute !important;
    left: 5px !important;
    top: 1px !important;
    width: 5px !important;
    height: 10px !important;
    border: solid #000 !important;
    border-width: 0 2px 2px 0 !important;
    transform: rotate(45deg) !important;"""
content = content.replace(old_check, new_check)

# 3. Add UI components
ui_old = """        with gr.TabItem("Batch"):
            gr.Markdown("> Dosyalari yuklemek icin: `scp dosya.mp4 sunucu:/workspace/whisper-diarization/uploads/`")
            with gr.Row():"""
ui_new = """        with gr.TabItem("Batch"):
            gr.Markdown("> Yeni dosyaları buraya sürükleyip bırakabilirsiniz veya listeden mevcut dosyaları seçebilirsiniz.")
            with gr.Row():
                upload_drop = gr.File(label="Drag & Drop Upload (MP4/WAV/MP3)", file_count="multiple", type="filepath", height=100)
            with gr.Row():"""
content = content.replace(ui_old, ui_new)

# 4. Add upload event listener
trigger_old = """            ref_btn.click(fn=refresh_list, outputs=[f_cl, info_txt])"""
trigger_new = """            upload_drop.upload(fn=handle_upload, inputs=[upload_drop], outputs=[f_cl, info_txt])
            ref_btn.click(fn=refresh_list, outputs=[f_cl, info_txt])"""
content = content.replace(trigger_old, trigger_new)

with open(app_py, "w") as f:
    f.write(content)
