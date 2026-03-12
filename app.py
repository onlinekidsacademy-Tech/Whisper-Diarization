"""
Whisper Diarization - Premium Dark UI
"""
import gradio as gr
import os, sys, re, time, traceback, shutil
import torch
import requests as http_requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback as tb_module
import numpy as np
import faster_whisper
from ctc_forced_aligner import (generate_emissions, get_alignments, get_spans,
    load_alignment_model, postprocess_results, preprocess_text)
from deepmultilingualpunctuation import PunctuationModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import (cleanup, find_numeral_symbol_tokens,
    get_realigned_ws_mapping_with_punctuation, get_sentences_speaker_mapping,
    get_speaker_aware_transcript, get_words_speaker_mapping, langs_to_iso,
    punct_model_langs, write_srt)
from diarization import MSDDDiarizer, SortformerDiarizer

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(PROJECT_DIR, "uploads")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MTYPES = {"cpu": "int8", "cuda": "float16"}

print("Loading models...")
t0 = time.time()
whisper_model_cache = {}
wm = faster_whisper.WhisperModel("large-v3", device=DEVICE, compute_type=MTYPES[DEVICE])
whisper_model_cache["large-v3"] = (wm, faster_whisper.BatchedInferencePipeline(wm))
alignment_model, alignment_tokenizer = load_alignment_model(DEVICE, dtype=torch.float16 if DEVICE == "cuda" else torch.float32)
punct_model = PunctuationModel(model="kredor/punctuate-all")
msdd_diarizer = MSDDDiarizer(device=DEVICE)
sortformer_diarizer = SortformerDiarizer(device=DEVICE)
import nltk; nltk.download("punkt_tab", quiet=True)
print(f"Models loaded in {time.time()-t0:.1f}s")

def get_whisper(n):
    if n not in whisper_model_cache:
        w = faster_whisper.WhisperModel(n, device=DEVICE, compute_type=MTYPES[DEVICE])
        whisper_model_cache[n] = (w, faster_whisper.BatchedInferencePipeline(w))
    return whisper_model_cache[n]

def get_diarizer(n):
    return sortformer_diarizer if n == "sortformer" else msdd_diarizer

AUDIO_EXT = {".mp3",".wav",".flac",".m4a",".ogg",".wma",".aac",".mp4",".mkv",".avi",".mov",".webm"}

def handle_upload(files):
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

def list_drive():
    files = []
    for f in sorted(os.listdir(UPLOAD_DIR)):
        if os.path.splitext(f)[1].lower() in AUDIO_EXT:
            sz = os.path.getsize(os.path.join(UPLOAD_DIR, f)) / (1024*1024)
            files.append(f"{f} ({sz:.1f} MB)")
    return files

def refresh_list():
    fl = list_drive()
    info = f"{len(fl)} dosya bulundu" if fl else "Dosya yok"
    return gr.CheckboxGroup(choices=fl, value=[]), info

def select_all():
    c = list_drive()
    return gr.CheckboxGroup(choices=c, value=c)

def run_pipeline(apath, lang, supp, diar, nostem, wmodel):
    yield "Vokal ayirma (Demucs) basliyor..."
    vt = apath
    tp = os.path.join(PROJECT_DIR, f"tmp_{os.getpid()}_{int(time.time())}")
    os.makedirs(tp, exist_ok=True)
    try:
        if not nostem:
            if os.system(f'python -m demucs.separate -n htdemucs --two-stems=vocals "{apath}" -o "{tp}" --device "{DEVICE}"') == 0:
                vt = os.path.join(tp, "htdemucs", os.path.splitext(os.path.basename(apath))[0], "vocals.wav")
        yield "Whisper modeli yukleniyor..."
        w, wp = get_whisper(wmodel)
        wav = faster_whisper.decode_audio(vt)
        st = find_numeral_symbol_tokens(w.hf_tokenizer) if supp else [-1]
        yield "Whisper deşifre (transcription) ediliyor..."
        segs, info = wp.transcribe(wav, lang, suppress_tokens=st, batch_size=8)
        ft = "".join(s.text for s in segs)
        dl = info.language
        yield "Hizalama (alignment) emisyonları olusturuluyor..."
        em, stride = generate_emissions(alignment_model, torch.from_numpy(wav).to(alignment_model.dtype).to(alignment_model.device), batch_size=8)
        ts, txts = preprocess_text(ft, romanize=True, language=langs_to_iso[dl])
        sg, sc, bt = get_alignments(em, ts, alignment_tokenizer)
        sp = get_spans(ts, sg, bt)
        wts = postprocess_results(txts, sp, stride, sc)
        yield f"Konuşmacı ayrımı ({diar}) basliyor..."
        dia = get_diarizer(diar)
        sts = dia.diarize(torch.from_numpy(wav).unsqueeze(0))
        wsm = get_words_speaker_mapping(wts, sts, "start")
        if dl in punct_model_langs:
            wl = [x["word"] for x in wsm]
            lw = punct_model.predict(wl, chunk_size=230)
            for wd, lt2 in zip(wsm, lw):
                w2 = wd["word"]
                if w2 and lt2[1] in ".?!" and (w2[-1] not in ".,;:!?"):
                    w2 += lt2[1]
                    if w2.endswith(".."): w2 = w2.rstrip(".")
                    wd["word"] = w2
        wsm = get_realigned_ws_mapping_with_punctuation(wsm)
        ssm = get_sentences_speaker_mapping(wsm, sts)
        bn = os.path.splitext(os.path.basename(apath))[0]
        tp2 = os.path.join(OUTPUT_DIR, f"{bn}.txt")
        sp2 = os.path.join(OUTPUT_DIR, f"{bn}.srt")
        with open(tp2, "w", encoding="utf-8-sig") as f: get_speaker_aware_transcript(ssm, f)
        with open(sp2, "w", encoding="utf-8-sig") as f: write_srt(ssm, f)
        with open(tp2, "r", encoding="utf-8-sig") as f: txt = f.read()
        yield (txt, sp2, tp2)
    finally:
        if os.path.exists(tp): shutil.rmtree(tp, ignore_errors=True)

def process_all(sel, language, supp, diar, nostem, wmodel):
    if not sel:
        sel = list_drive()
    if not sel:
        yield "Dosya yok", "uploads/ dizinine dosya yukleyin", None
        return
    lang = language if language != "Auto (Detect)" else None
    if lang: lang = lang.lower()
    total = len(sel)
    txts, srts, logs = [], [], []
    t0 = time.time()
    def log(m):
        logs.append(f"[{time.strftime('%H:%M:%S')}] {m}")
        return "\n".join(logs[-50:])
    l = log(f"Batch: {total} dosya | {wmodel} | {diar}")
    yield "", l, None
    for i, d in enumerate(sel):
        fn = d.split(" (")[0]
        ap = os.path.join(UPLOAD_DIR, fn)
        if not os.path.exists(ap):
            l = log(f"[{i+1}/{total}] YOK: {fn}")
            yield "\n\n".join(txts), l, None
            continue
        fs = time.time()
        l = log(f"[{i+1}/{total}] {fn}...")
        yield "\n\n".join(txts), l, None
        try:
            for update in run_pipeline(ap, lang, supp, diar, nostem, wmodel):
                if isinstance(update, str):
                    yield "\n\n".join(txts), log(f"  => {update}"), srts or None
                else:
                    t, s, _ = update
                    ft = int(time.time() - fs)
                    txts.append(f"--- {fn} ---\n{t}")
                    srts.append(s)
                    l = log(f"  OK ({ft}s)")
                    yield "\n\n".join(txts), l, srts
        except Exception as e:
            traceback.print_exc()
            l = log(f"  HATA: {e}")
            yield "\n\n".join(txts), l, srts or None
    bt = int(time.time()-t0)
    l = log(f"Bitti! {len(txts)}/{total} - {bt//60}dk {bt%60}sn")
    yield "\n\n".join(txts), l, srts or None

def single_process(ap, language, supp, diar, nostem, wmodel, url=None):
    import urllib.request
    import os
    import tempfile
    import shutil
    
    if url and url.strip():
        try:
            temp_dir = tempfile.mkdtemp()
            # Try to grab extension from URL before query params
            clean_url = url.split("?")[0]
            ext = os.path.splitext(clean_url)[1]
            if not ext:
                ext = ".mp4"
            downloaded_file = os.path.join(temp_dir, f"downloaded_audio{ext}")
            req = urllib.request.Request(url.strip(), headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=30) as response, open(downloaded_file, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            ap = downloaded_file
        except urllib.error.HTTPError as e:
            yield "", f"HTTP Error {e.code}: {e.reason} (Note: S3 links with X-Amz-Expires may have expired)", None
            return
        except Exception as e:
            yield "", f"Error downloading from URL: {str(e)}", None
            return

    if not ap:
        yield "", "Dosya yukleyin", None
        return
    lang = language if language != "Auto (Detect)" else None
    if lang: lang = lang.lower()
    logs = []
    def log(m):
        logs.append(f"[{time.strftime('%H:%M:%S')}] {m}")
        return "\n".join(logs[-50:])
    l = log(f"Isleniyor: {os.path.basename(ap)}")
    yield "", l, None
    t0 = time.time()
    try:
        for update in run_pipeline(ap, lang, supp, diar, nostem, wmodel):
            if isinstance(update, str):
                yield "", log(f"=> {update}"), None
            else:
                t, s, _ = update
                l = log(f"OK! {len(t)} kar. {int(time.time()-t0)}sn")
                yield t, l, s
    except Exception as e:
        traceback.print_exc()
        yield str(e), log(f"HATA: {e}"), None

# ── Premium Dark CSS ──
CUSTOM_CSS = """
/* Bootstrap 5 Mimic Theme for Gradio */

:root {
  --bs-blue: #0d6efd;
  --bs-primary: #0d6efd;
  --bs-secondary: #6c757d;
  --bs-success: #198754;
  --bs-body-bg: #f8f9fa;
  --bs-body-color: #212529;
  --bs-border-color: #dee2e6;
  --bs-border-radius: 0.375rem;
  --bs-box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  --bs-font-sans-serif: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif;
}

body, .gradio-container, .gr-blocks {
    background-color: var(--bs-body-bg) !important;
    background-image: none !important;
    color: var(--bs-body-color) !important;
    font-family: var(--bs-font-sans-serif) !important;
}

/* Cards (gr-box/panel) */
.gr-box, .gr-panel, fieldset, .gr-block {
    background-color: #ffffff !important;
    border: 1px solid var(--bs-border-color) !important;
    border-radius: var(--bs-border-radius) !important;
    box-shadow: var(--bs-box-shadow) !important;
}

/* Typography elements */
h1, h2, h3, h4, h5, h6, .gr-form-label, label, p, span {
    color: var(--bs-body-color) !important;
}

/* Form Controls (Inputs, Textarea, Select) */
input, textarea, select, .gr-input, .gr-dropdown {
    display: block !important;
    width: 100% !important;
    padding: 0.375rem 0.75rem !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
    color: var(--bs-body-color) !important;
    background-color: #fff !important;
    background-clip: padding-box !important;
    border: 1px solid #ced4da !important;
    appearance: none !important;
    border-radius: var(--bs-border-radius) !important;
    transition: border-color .15s ease-in-out,box-shadow .15s ease-in-out !important;
    box-shadow: none !important;
}

input:focus, textarea:focus, select:focus, .gr-input:focus {
    color: var(--bs-body-color) !important;
    background-color: #fff !important;
    border-color: #86b7fe !important;
    outline: 0 !important;
    box-shadow: 0 0 0 0.25rem rgba(13,110,253,.25) !important;
}

/* Primary Button (btn-primary) */
button.primary, .gr-button-primary {
    color: #fff !important;
    background-color: var(--bs-primary) !important;
    border-color: var(--bs-primary) !important;
    display: inline-block !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
    text-align: center !important;
    text-decoration: none !important;
    vertical-align: middle !important;
    cursor: pointer !important;
    user-select: none !important;
    border: 1px solid transparent !important;
    padding: 0.375rem 0.75rem !important;
    font-size: 1rem !important;
    border-radius: var(--bs-border-radius) !important;
    transition: color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out !important;
    box-shadow: none !important;
}
button.primary:hover, .gr-button-primary:hover {
    color: #fff !important;
    background-color: #0b5ed7 !important;
    border-color: #0a58ca !important;
}
button.primary:active, .gr-button-primary:active {
    background-color: #0a58ca !important;
    border-color: #0a53be !important;
    box-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125) !important;
}

/* Secondary Button (btn-secondary/btn-outline) */
button.secondary, .gr-button-secondary {
    color: var(--bs-secondary) !important;
    background-color: transparent !important;
    border: 1px solid var(--bs-secondary) !important;
    display: inline-block !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
    text-align: center !important;
    text-decoration: none !important;
    padding: 0.375rem 0.75rem !important;
    font-size: 1rem !important;
    border-radius: var(--bs-border-radius) !important;
    transition: color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out !important;
}
button.secondary:hover, .gr-button-secondary:hover {
    color: #fff !important;
    background-color: var(--bs-secondary) !important;
    border-color: var(--bs-secondary) !important;
}

/* Tabs (nav-tabs style) */
.gr-tabs > div > button {
    color: var(--bs-primary) !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-top-left-radius: var(--bs-border-radius) !important;
    border-top-right-radius: var(--bs-border-radius) !important;
    margin-bottom: -1px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 400 !important;
}
.gr-tabs > div > button.selected {
    color: #495057 !important;
    background-color: #fff !important;
    border-color: #dee2e6 #dee2e6 #fff !important;
}
.gr-tabs > div > button:hover:not(.selected) {
    border-color: #e9ecef #e9ecef #dee2e6 !important;
}
.gr-tabs {
    border-bottom: 1px solid #dee2e6 !important;
}

/* Checkbox (form-check-input) */
input[type="checkbox"] {
    width: 1em !important;
    height: 1em !important;
    margin-top: 0.25em !important;
    vertical-align: top !important;
    background-color: #fff !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: contain !important;
    border: 1px solid rgba(0,0,0,.25) !important;
    appearance: none !important;
    border-radius: 0.25em !important;
}
input[type="checkbox"]:checked {
    background-color: var(--bs-primary) !important;
    border-color: var(--bs-primary) !important;
}

/* File Upload Area */
.gr-file-upload {
    background-color: #f8f9fa !important;
    border: 2px dashed #dee2e6 !important;
    border-radius: var(--bs-border-radius) !important;
    transition: background-color 0.2s ease !important;
}
.gr-file-upload:hover {
    background-color: #e2e3e5 !important;
    border-color: #adb5bd !important;
}

/* Header */
.app-header h1 {
    font-weight: 500 !important;
    margin-bottom: 0.5rem !important;
    line-height: 1.2 !important;
    font-size: 2.5rem !important;
}
.app-header p {
    font-size: 1.25rem !important;
    font-weight: 300 !important;
    color: #6c757d !important;
}
"""


BS5_THEME = gr.themes.Base()

with gr.Blocks(title="Whisper Diarization", theme=BS5_THEME, css=CUSTOM_CSS) as demo:
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
                            bat_txt = gr.Textbox(label="Transcript Output", lines=16)
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
                            s_url = gr.Textbox(label="Or provide a direct URL (e.g., S3 link)", placeholder="https://...")
                            s_au = gr.Audio(type="filepath", label="Upload Audio / Video")
                            s_btn = gr.Button("✨ Start Transcription", variant="primary", size="lg")
                        with gr.Column(scale=3):
                            s_txt = gr.Textbox(label="Transcript", lines=12)
                            s_srt = gr.File(label="SRT Subtitle")
                    
                    s_log = gr.Textbox(label="Event Log", lines=4, interactive=False, elem_id="log-output")
                    s_btn.click(fn=single_process, inputs=[s_au, lang_dd, su_cb, d_dd, ns_cb, w_dd, s_url], outputs=[s_txt, s_log, s_srt])

    demo.load(fn=refresh_list, outputs=[f_cl, info_txt])

if __name__ == "__main__":
    print(f"Upload: {UPLOAD_DIR}")

    # Create FastAPI app and mount API routes
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    import uvicorn

    fastapi_app = FastAPI()

    @fastapi_app.post("/api/transcribe")
    async def handle_transcribe(request: Request):
        try:
            body = await request.json()
            url = body.get("url", "")
            lang = body.get("language", None)
            diar = body.get("diarizer", "sortformer")
            wmodel = body.get("model", "large-v3")

            if not url:
                return JSONResponse({"error": "Missing 'url' field"}, status_code=400)

            # Download audio from URL
            tmp_dir = os.path.join(PROJECT_DIR, f"api_dl_{os.getpid()}_{int(time.time())}")
            os.makedirs(tmp_dir, exist_ok=True)
            ext = os.path.splitext(url.split("?")[0])[-1] or ".mp4"
            tmp_file = os.path.join(tmp_dir, f"input{ext}")

            r = http_requests.get(url, timeout=120, stream=True)
            r.raise_for_status()
            with open(tmp_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Run pipeline
            result = api_transcribe_sync(tmp_file, lang=lang, diar=diar, wmodel=wmodel)

            # Cleanup
            shutil.rmtree(tmp_dir, ignore_errors=True)

            return JSONResponse(result)
        except Exception as e:
            import traceback as tbb
            return JSONResponse({"error": str(e), "trace": tbb.format_exc()}, status_code=500)

    @fastapi_app.get("/api/health")
    async def health():
        return JSONResponse({"status": "ok", "models_loaded": True})

    # Mount Gradio inside the FastAPI app
    fastapi_app = gr.mount_gradio_app(fastapi_app, demo, path="/")

    uvicorn.run(fastapi_app, host="0.0.0.0", port=7860)
