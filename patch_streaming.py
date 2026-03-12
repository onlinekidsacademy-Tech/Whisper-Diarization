import os
import re

file_path = "app.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add yield statements into run_pipeline
code = code.replace(
    "def run_pipeline(apath, lang, supp, diar, nostem, wmodel):",
    "def run_pipeline(apath, lang, supp, diar, nostem, wmodel):\n    yield \"Vokal ayirma (Demucs) basliyor...\""
)

code = code.replace(
    "w, wp = get_whisper(wmodel)",
    "yield \"Whisper modeli yukleniyor...\"\n        w, wp = get_whisper(wmodel)"
)

code = code.replace(
    "segs, info = wp.transcribe(wav, lang, suppress_tokens=st, batch_size=8)",
    "yield \"Whisper deşifre (transcription) ediliyor...\"\n        segs, info = wp.transcribe(wav, lang, suppress_tokens=st, batch_size=8)"
)

code = code.replace(
    "em, stride = generate_emissions",
    "yield \"Hizalama (alignment) emisyonları olusturuluyor...\"\n        em, stride = generate_emissions"
)

code = code.replace(
    "dia = get_diarizer(diar)",
    "yield f\"Konuşmacı ayrımı ({diar}) basliyor...\"\n        dia = get_diarizer(diar)"
)

code = code.replace(
    "return txt, sp2, tp2",
    "yield (txt, sp2, tp2)"
)

# 2. Update process_all to consume the generator
old_process_all = """        try:
            t, s, _ = run_pipeline(ap, lang, supp, diar, nostem, wmodel)
            ft = int(time.time() - fs)
            txts.append(f"--- {fn} ---\n{t}")
            srts.append(s)
            l = log(f"  OK ({ft}s)")
            yield "\\n\\n".join(txts), l, srts"""

new_process_all = """        try:
            for update in run_pipeline(ap, lang, supp, diar, nostem, wmodel):
                if isinstance(update, str):
                    yield "\\n\\n".join(txts), log(f"  => {update}"), srts or None
                else:
                    t, s, _ = update
                    ft = int(time.time() - fs)
                    txts.append(f"--- {fn} ---\\n{t}")
                    srts.append(s)
                    yield "\\n\\n".join(txts), log(f"  OK ({ft}s)"), srts
"""
code = code.replace(old_process_all, new_process_all)


# 3. Update single_process to consume the generator
old_single = """    try:
        t, s, _ = run_pipeline(ap, lang, supp, diar, nostem, wmodel)
        l = log(f"OK! {len(t)} kar. {int(time.time()-t0)}sn")
        yield t, l, s"""

new_single = """    try:
        for update in run_pipeline(ap, lang, supp, diar, nostem, wmodel):
            if isinstance(update, str):
                yield "", log(f"=> {update}"), None
            else:
                t, s, _ = update
                l = log(f"OK! {len(t)} kar. {int(time.time()-t0)}sn")
                yield t, l, s"""
code = code.replace(old_single, new_single)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch applied!")
