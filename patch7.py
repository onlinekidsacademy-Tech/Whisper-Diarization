app_py = "/workspace/whisper-diarization/app.py"

with open(app_py, "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "def process_all_wrapper(lang, supp, diar, nostem, wmodel):" in line:
        continue
    if "yield from process_all([], lang, supp, diar, nostem, wmodel)" in line:
        continue
    if "all_btn.click(fn=process_all_wrapper" in line:
        new_lines.append('            def process_all_wrapper(lang, supp, diar, nostem, wmodel):\n')
        new_lines.append('                yield from process_all([], lang, supp, diar, nostem, wmodel)\n')
        new_lines.append('            all_btn.click(fn=process_all_wrapper, inputs=[lang_dd, su_cb, d_dd, ns_cb, w_dd], outputs=[bat_txt, bat_log, bat_srt])\n')
    else:
        new_lines.append(line)

with open(app_py, "w") as f:
    f.writelines(new_lines)
