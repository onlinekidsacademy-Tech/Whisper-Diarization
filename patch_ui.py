import re

app_py = "/workspace/whisper-diarization/app.py"

with open(app_py, "r") as f:
    content = f.read()

# Find the split point where `# ── Premium Dark CSS ──` begins
split_idx = content.find("# ── Premium Dark CSS ──")
if split_idx == -1:
    split_idx = content.find("CUSTOM_CSS = \"\"\"")

core_logic = content[:split_idx]

new_ui = """# ── Premium Dark CSS ──
CUSTOM_CSS = \"\"\"
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
code, pre, .prose code, textarea { font-family: 'JetBrains Mono', monospace !important; }

body, .app {
    background: #09090b !important;
    color: #fafafa !important;
}

.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    background: transparent !important;
}

footer { display: none !important; }

/* Main layout wrapper overrides if any */
.main {
    background: transparent !important;
    gap: 24px !important;
}

/* Header */
.app-header {
    text-align: left !important;
    padding: 24px 16px 16px 16px !important;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    margin-bottom: 8px !important;
}
.app-header h1 { 
    font-weight: 700 !important; letter-spacing: -0.04em !important;
    background: linear-gradient(135deg, #ffffff 0%, #a1a1aa 100%) !important;
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    font-size: 2.2rem !important; margin-bottom: 4px !important;
}
.app-header p {
    color: #a1a1aa !important; font-size: 0.95rem !important; margin: 0 !important;
}

/* Glassmorphism Cards */
.block, .form, .panel, .sidebar {
    background: rgba(24, 24, 27, 0.7) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2) !important;
}
.block:hover { border-color: rgba(255,255,255,0.12) !important; }

/* Labels */
label, .label-wrap span {
    color: #a1a1aa !important; font-weight: 600 !important;
    font-size: 0.75rem !important; text-transform: uppercase !important;
    letter-spacing: 0.08em !important; margin-bottom: 4px !important;
}

/* Inputs / Dropdowns */
input, select, textarea, .wrap input, .wrap select {
    background: rgba(9, 9, 11, 0.8) !important; 
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #f4f4f5 !important; border-radius: 10px !important;
    font-size: 0.9rem !important; padding: 10px 14px !important;
    transition: all 0.2s ease !important;
}
input:focus, select:focus, textarea:focus {
    border-color: #3b82f6 !important; 
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    outline: none !important;
}

/* Buttons - Accent/Primary */
button.primary, .primary {
    background: linear-gradient(135deg, #f4f4f5 0%, #d4d4d8 100%) !important; 
    color: #09090b !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.9rem !important;
    letter-spacing: 0.01em !important; padding: 12px 24px !important;
    transition: all 0.2s ease !important; 
    box-shadow: 0 2px 10px rgba(255,255,255,0.1) !important;
}
button.primary:hover, .primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255,255,255,0.2) !important;
    background: linear-gradient(135deg, #ffffff 0%, #e4e4e7 100%) !important; 
}

/* Buttons - Process All (Special Highlight) */
button#btn-process-all {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
}
button#btn-process-all:hover {
    box-shadow: 0 6px 25px rgba(59, 130, 246, 0.5) !important;
}

/* Buttons - Secondary */
button.secondary, .secondary {
    background: rgba(255,255,255,0.03) !important; 
    color: #d4d4d8 !important;
    border: 1px solid rgba(255,255,255,0.1) !important; 
    border-radius: 10px !important;
    font-weight: 500 !important; font-size: 0.85rem !important;
    padding: 10px 20px !important; transition: all 0.2s ease !important;
}
button.secondary:hover, .secondary:hover {
    border-color: rgba(255,255,255,0.2) !important; 
    background: rgba(255,255,255,0.08) !important;
    color: #fff !important;
}

/* Tabs */
.tab-nav button {
    background: transparent !important; color: #71717a !important;
    border: none !important; border-bottom: 2px solid transparent !important;
    font-weight: 600 !important; font-size: 0.9rem !important;
    padding: 16px 24px !important; text-transform: uppercase !important;
    letter-spacing: 0.04em !important; transition: all 0.2s ease !important;
}
.tab-nav button.selected {
    color: #f4f4f5 !important; border-bottom-color: #3b82f6 !important;
}
.tab-nav { border-bottom: 1px solid rgba(255,255,255,0.05) !important; margin-bottom: 16px !important; }

/* Checkbox Group Fixes */
.checkbox-group label, .wrap .checkbox-group label {
    text-transform: none !important; letter-spacing: normal !important;
    font-size: 0.9rem !important; color: #d4d4d8 !important;
}
.checkbox-group .wrap {
    background: rgba(9, 9, 11, 0.5) !important; border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 10px !important; padding: 12px !important;
}

/* Custom Checkmark SVG Hack for Dark Theme */
.checkbox-group input[type="checkbox"] {
    appearance: none !important; -webkit-appearance: none !important;
    width: 20px !important; height: 20px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 4px !important; background: rgba(9, 9, 11, 0.8) !important;
    cursor: pointer !important; position: relative !important;
}
.checkbox-group input[type="checkbox"]:checked {
    background: #3b82f6 !important; border-color: #3b82f6 !important;
}
.checkbox-group input[type="checkbox"]:checked::after {
    content: '' !important; position: absolute !important;
    left: 6px !important; top: 2px !important;
    width: 6px !important; height: 11px !important;
    border: solid white !important; border-width: 0 2px 2px 0 !important;
    transform: rotate(45deg) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.25); }

/* File & Log specific */
.file-preview { background: rgba(0,0,0,0.2) !important; border-color: rgba(255,255,255,0.05) !important; }
.upload-button { background: rgba(255,255,255,0.05) !important; border-color: rgba(255,255,255,0.1) !important; }
#log-output textarea { font-size: 0.8rem !important; color: #a1a1aa !important; }
\"\"\"

DARK_THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.blue,
    secondary_hue=gr.themes.colors.zinc,
    neutral_hue=gr.themes.colors.zinc,
    font=gr.themes.GoogleFont("Inter"),
    font_mono=gr.themes.GoogleFont("JetBrains Mono"),
).set(
    body_background_fill="#09090b",
    body_text_color="#fafafa",
    background_fill_primary="transparent",
    background_fill_secondary="transparent",
    border_color_primary="transparent",
    block_background_fill="transparent",
    block_border_color="transparent",
    shadow_drop="none",
)

with gr.Blocks(title="Whisper Diarization", theme=DARK_THEME, css=CUSTOM_CSS) as demo:
    with gr.Column(elem_classes="app-header"):
        gr.Markdown("<h1>Whisper Diarization</h1><p>🎙️ Studio-grade speech recognition & speaker separation engine (RunPod GPU)</p>")
    
    with gr.Row():
        # --- SIDEBAR (Settings) ---
        with gr.Column(scale=1, min_width=280):
            with gr.Group(elem_classes="sidebar"):
                gr.Markdown("### ⚙️ Engine Settings")
                lang_dd = gr.Dropdown(choices=["Auto (Detect)","tr","en","de","fr","es","ar","ru","ja","ko","zh"], value="Auto (Detect)", label="Language", interactive=True)
                w_dd = gr.Dropdown(choices=["tiny","base","small","medium","medium.en","large-v2","large-v3"], value="large-v3", label="Whisper Model", interactive=True)
                d_dd = gr.Dropdown(choices=["msdd","sortformer"], value="sortformer", label="Diarizer Engine", interactive=True)
                
                gr.Markdown("#### Advanced Options")
                ns_cb = gr.Checkbox(label="Isolate Vocals (No-Stem/Demucs)", value=True, interactive=True)
                su_cb = gr.Checkbox(label="Suppress Numbers", value=False, interactive=True)

        # --- MAIN CONTENT ---
        with gr.Column(scale=4):
            with gr.Tabs():
                # ── BATCH TAB ──
                with gr.TabItem("📁 Batch Processing"):
                    gr.Markdown("> 💡 **Tip:** Drop files into `/workspace/whisper-diarization/uploads/` via SCP or FTP to process multiple massive files at once.")
                    
                    with gr.Row():
                        # Left side of Batch
                        with gr.Column(scale=2):
                            info_txt = gr.Textbox(label="Storage Status", interactive=False, lines=1, placeholder="Loading directory info...")
                            f_cl = gr.CheckboxGroup(choices=list_drive(), label="Workspace Files")
                            
                            with gr.Row():
                                ref_btn = gr.Button("🔄 Refresh", variant="secondary", size="sm")
                                sel_btn = gr.Button("☑️ Select All", variant="secondary", size="sm")
                            
                            gr.Markdown("<br>")
                            with gr.Row():
                                batch_btn = gr.Button("▶️ Process Selected", variant="primary", size="lg")
                                all_btn = gr.Button("🚀 PROCESS ALL", variant="primary", size="lg", elem_id="btn-process-all")
                        
                        # Right side of Batch (Results)
                        with gr.Column(scale=3):
                            bat_txt = gr.Textbox(label="Transcript Output", lines=16, show_copy_button=True)
                            bat_srt = gr.File(label="Generated SRT Files", file_count="multiple")
                    
                    bat_log = gr.Textbox(label="Terminal Logs", lines=6, interactive=False, elem_id="log-output")

                    ref_btn.click(fn=refresh_list, outputs=[f_cl, info_txt])
                    sel_btn.click(fn=select_all, outputs=[f_cl])
                    batch_btn.click(fn=process_all, inputs=[f_cl, lang_dd, su_cb, d_dd, ns_cb, w_dd], outputs=[bat_txt, bat_log, bat_srt])
                    
                    def process_all_wrapper(lang, supp, diar, nostem, wmodel):
                        yield from process_all([], lang, supp, diar, nostem, wmodel)
                    
                    all_btn.click(fn=process_all_wrapper, inputs=[lang_dd, su_cb, d_dd, ns_cb, w_dd], outputs=[bat_txt, bat_log, bat_srt])

                # ── SINGLE TAB ──
                with gr.TabItem("🎵 Single File"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            s_au = gr.Audio(type="filepath", label="Upload Audio / Video")
                            s_btn = gr.Button("✨ Start Transcription", variant="primary", size="lg")
                        with gr.Column(scale=3):
                            s_txt = gr.Textbox(label="Transcript", lines=12, show_copy_button=True)
                            s_srt = gr.File(label="SRT Subtitle")
                    
                    s_log = gr.Textbox(label="Event Log", lines=4, interactive=False, elem_id="log-output")
                    s_btn.click(fn=single_process, inputs=[s_au, lang_dd, su_cb, d_dd, ns_cb, w_dd], outputs=[s_txt, s_log, s_srt])

    demo.load(fn=refresh_list, outputs=[f_cl, info_txt])

if __name__ == "__main__":
    print(f"Upload: {UPLOAD_DIR}")
    demo.launch(server_name="0.0.0.0", server_port=8888, share=True)
"""

with open(app_py, "w") as f:
    f.write(core_logic + new_ui)
