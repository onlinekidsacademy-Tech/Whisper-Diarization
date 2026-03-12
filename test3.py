import torch
from nemo.collections.asr.models import SortformerEncLabelModel

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SortformerEncLabelModel.from_pretrained("nvidia/diar_streaming_sortformer_4spk-v2", map_location=device)
model.eval()

# Raw audio: batch=1, time=160000 (10 seconds)
audio = torch.randn(1, 160000).to(device)
audio_len = torch.tensor([160000]).to(device)

print("Testing direct forward with raw audio...")
try:
    with torch.inference_mode():
        preds, _ = model(audio_signal=audio, audio_signal_length=audio_len)
    print("Success! Preds shape:", preds.shape)
except Exception as e:
    print("Failed direct forward:", e)
