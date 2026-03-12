import re

app_py = "/workspace/whisper-diarization/app.py"
with open(app_py, "r") as f:
    content = f.read()

# Replace the beginning of single_process
old_single_process = """def single_process(ap, language, supp, diar, nostem, wmodel, url=None):
    if not ap:
        yield "", "Dosya yukleyin", None
        return"""

new_single_process = """def single_process(ap, language, supp, diar, nostem, wmodel, url=None):
    import urllib.request
    import os
    import tempfile
    
    if url and url.strip():
        try:
            temp_dir = tempfile.mkdtemp()
            ext = ".mp4" if ".mp4" in url else ".wav"
            downloaded_file = os.path.join(temp_dir, f"downloaded_audio{ext}")
            req = urllib.request.Request(url.strip(), headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(downloaded_file, 'wb') as out_file:
                out_file.write(response.read())
            ap = downloaded_file
        except Exception as e:
            yield "", f"Error downloading from URL: {str(e)}", None
            return

    if not ap:
        yield "", "Dosya yukleyin", None
        return"""

content = content.replace(old_single_process, new_single_process)

with open(app_py, "w") as f:
    f.write(content)

print("URL logic fixed")
