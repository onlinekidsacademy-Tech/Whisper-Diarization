app_py = "/workspace/whisper-diarization/app.py"

with open(app_py, "r") as f:
    content = f.read()

import re
old_all_btn = "all_btn.click(fn=lambda *a: process_all([], *a), inputs=[lang_dd, su_cb, d_dd, ns_cb, w_dd], outputs=[bat_txt, bat_log, bat_srt])"
new_all_btn = """
            def process_all_wrapper(lang, supp, diar, nostem, wmodel):
                yield from process_all([], lang, supp, diar, nostem, wmodel)
            
            all_btn.click(fn=process_all_wrapper, inputs=[lang_dd, su_cb, d_dd, ns_cb, w_dd], outputs=[bat_txt, bat_log, bat_srt])
"""
content = content.replace(old_all_btn, new_all_btn.strip('\n'))

with open(app_py, "w") as f:
    f.write(content)
