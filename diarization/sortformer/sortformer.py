from warnings import warn

import torch

from nemo.collections.asr.models import SortformerEncLabelModel
from nemo.collections.asr.parts.mixins.diarization import DiarizeConfig


class SortformerDiarizer:
    # Max chunk: 60 seconds at 16kHz = 960000 samples
    CHUNK_SAMPLES = 960000
    # Overlap: 5 seconds
    OVERLAP_SAMPLES = 80000

    def __init__(self, device):
        self.device = device
        self.model: SortformerEncLabelModel = SortformerEncLabelModel.from_pretrained(
            "nvidia/diar_streaming_sortformer_4spk-v2", map_location=device
        )

        # Force offline inference to avoid forward_streaming tensor bugs
        self.model.streaming_mode = False
        # Use FP16 to halve memory usage
        self.model.half()

        warn(
            "Sortformer supports maximum of 4 speakers only, "
            "please use MSDD if your audio has more than 4 speakers",
            Warning,
        )

        self.model.eval()

    def _infer_chunk(self, audio_chunk: torch.Tensor):
        """Run inference on a single chunk, returns raw preds tensor."""
        with torch.inference_mode():
            audio_len = torch.tensor([audio_chunk.shape[-1]]).to(audio_chunk.device)
            preds = self.model(audio_signal=audio_chunk.half(), audio_signal_length=audio_len)
            if isinstance(preds, tuple):
                preds = preds[0]
            return preds.cpu().float()

    def diarize(self, audio: torch.Tensor):
        total_samples = audio.shape[-1]

        # Clear GPU cache before starting
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # If audio fits in one chunk, process directly
        if total_samples <= self.CHUNK_SAMPLES:
            preds = self._infer_chunk(audio)
        else:
            # Split into overlapping chunks and merge
            chunk_preds = []
            step = self.CHUNK_SAMPLES - self.OVERLAP_SAMPLES
            starts = list(range(0, total_samples, step))

            for i, start in enumerate(starts):
                end = min(start + self.CHUNK_SAMPLES, total_samples)
                chunk = audio[:, start:end]

                # Skip very short chunks (< 1 second)
                if chunk.shape[-1] < 16000:
                    continue

                p = self._infer_chunk(chunk)
                chunk_preds.append((start, end, p))

                # Free GPU memory between chunks
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

            # Merge chunk predictions by converting each to labels and adjusting offsets
            all_labels = []
            for start_sample, end_sample, p in chunk_preds:
                offset_ms = int(start_sample / 16000 * 1000)
                chunk_labels = self._preds_to_labels(p)
                for s, e, spk in chunk_labels:
                    all_labels.append((s + offset_ms, e + offset_ms, spk))

            # Deduplicate overlapping labels from overlap regions
            all_labels = sorted(all_labels, key=lambda x: (x[2], x[0]))
            merged = []
            for label in all_labels:
                if merged and merged[-1][2] == label[2] and label[0] <= merged[-1][1]:
                    # Extend the existing label
                    merged[-1] = (merged[-1][0], max(merged[-1][1], label[1]), label[2])
                else:
                    merged.append(label)

            merged = sorted(merged, key=lambda x: x[0])
            return merged

        # Single-chunk path
        labels = self._preds_to_labels(preds)
        labels = sorted(labels, key=lambda x: x[0])
        return labels

    def _preds_to_labels(self, preds):
        """Convert model prediction tensor to (start_ms, end_ms, speaker_id) labels."""
        diarize_cfg = DiarizeConfig(
            postprocessing_params={
                "onset": 0.5,
                "offset": 0.5,
                "pad_onset": 0.0,
                "pad_offset": 0.0,
                "min_duration_on": 0.0,
                "min_duration_off": 0.0,
            }
        )

        audio_rttm_map_dict = {
            "audio": {
                "uniq_id": "audio",
                "audio_filepath": "tensor_audio",
                "offset": 0.0,
                "duration": None,
                "text": "-",
                "label": "infer",
            }
        }

        self.model._diarize_audio_rttm_map = audio_rttm_map_dict
        uniq_ids = list(self.model._diarize_audio_rttm_map.keys())
        processed_outputs = self.model._diarize_output_processing(preds, uniq_ids, diarize_cfg)
        self.model._diarize_audio_rttm_map = {}

        labels = []
        for label in processed_outputs[0]:
            start, end, speaker = label.split()
            start, end = float(start), float(end)
            start, end = int(start * 1000), int(end * 1000)
            labels.append((start, end, int(speaker.split("_")[1])))

        return labels
