import torch
import torchaudio
from diarization.sortformer.sortformer import SortformerDiarizer

def test():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dia = SortformerDiarizer(device)
    # Generate 10 seconds of dummy audio
    audio = torch.randn(1, 16000 * 10).to(device)
    print("Testing forward_streaming (which may crash)...")
    try:
        dia.diarize(audio)
        print("Streaming worked!")
    except Exception as e:
        print(f"Streaming failed: {e}")
        
    print("\nMonkey-patching to use standard forward()...")
    
    orig_forward_streaming = dia.model.forward_streaming
    
    def mock_streaming(processed_signal, processed_signal_length):
        # In NeMo ASR models, the standard forward pass takes these kwargs
        # usually returning (logits, encoder_lengths) or something similar
        logits, encoded_len = dia.model(input_signal=processed_signal, input_signal_length=processed_signal_length)
        return logits
        
    dia.model.forward_streaming = mock_streaming
    
    try:
        res = dia.diarize(audio)
        print(f"Standard forward worked! Found {len(res)} speaker segments.")
    except Exception as e:
        print(f"Standard forward failed: {e}")

test()
