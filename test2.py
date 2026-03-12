import torch
from diarization.sortformer.sortformer import SortformerDiarizer
device = "cuda" if torch.cuda.is_available() else "cpu"
dia = SortformerDiarizer(device)
audio = torch.randn(1, 16000 * 10).to(device)

print("Patching sortformer...")
def mock_diarize(self, audio):
    with torch.inference_mode():
        # See what forward(audio) does
        preds = self.model(audio_signal=audio, audio_signal_length=torch.tensor([audio.shape[-1]]).to(device))
        if isinstance(preds, tuple):
            preds = preds[0]
        preds = preds.cpu()
        print("Forward shape:", preds.shape)
        # Bypassing the rest for the test
        return preds
        
dia.diarize = mock_diarize.__get__(dia)
print("Testing...")
dia.diarize(audio)
