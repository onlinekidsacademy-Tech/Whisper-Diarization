import re

file_path = "diarization/sortformer/sortformer.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Replace forward_streaming with standard model call
old_code = "preds = self.model.forward_streaming(processed_signal, processed_signal_length)"
new_code = "preds, _ = self.model(audio_signal=processed_signal, audio_signal_length=processed_signal_length)"
code = code.replace(old_code, new_code)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("sortformer.py patched!")
