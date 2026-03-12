import re

file_path = "diarization/sortformer/sortformer.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Replace the inference_mode block
old_block = """        with torch.inference_mode():
            processed_signal, processed_signal_length = self.model.process_signal(
                audio_signal=audio,
                audio_signal_length=torch.tensor([audio.shape[-1]]),
            )
            processed_signal = processed_signal[:, :, : processed_signal_length.max()]

            preds, _ = self.model(audio_signal=processed_signal, audio_signal_length=processed_signal_length)
            preds = preds.cpu()"""

new_block = """        with torch.inference_mode():
            audio_len = torch.tensor([audio.shape[-1]]).to(audio.device)
            preds, _ = self.model(audio_signal=audio, audio_signal_length=audio_len)
            preds = preds.cpu()"""

if old_block in code:
    code = code.replace(old_block, new_block)
else:
    print("Could not find the block to replace!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("sortformer.py completely patched!")
