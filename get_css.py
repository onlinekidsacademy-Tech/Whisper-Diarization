import re
with open('/workspace/whisper-diarization/app.py', 'r') as f:
    content = f.read()

match = re.search(r'(CUSTOM_CSS\s*=\s*"""(.*?)""")', content, re.DOTALL)
if match:
    # Just checking it exists
    print("Found CUSTOM_CSS")
else:
    print("Not found")
