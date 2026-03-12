import re

app_py = "/workspace/whisper-diarization/app.py"
with open(app_py, "r") as f:
    content = f.read()

# Replace the single process logic to stream the download
old_logic = """def single_process(ap, language, supp, diar, nostem, wmodel, url=None):
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
            return"""

new_logic = """def single_process(ap, language, supp, diar, nostem, wmodel, url=None):
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
            return"""

content = content.replace(old_logic, new_logic)

with open(app_py, "w") as f:
    f.write(content)

print("URL streaming logic patched")
