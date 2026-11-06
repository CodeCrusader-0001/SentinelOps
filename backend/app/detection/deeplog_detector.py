import os
import pickle
import torch
import torch.nn.functional as F
from typing import Dict, List, Optional
from collections import defaultdict

from backend.app.detection.base import BaseAnomalyDetector, DetectionResult
from backend.app.detection.model_arch import DeepLogLSTM
from backend.app.detection.rule_detector import RuleBasedAnomalyDetector
from backend.app.models.log import Log
from backend.app.core.logging import logger

class DeepLogDetector(BaseAnomalyDetector):
    def __init__(
        self,
        model_path: str,
        vocab_path: str,
        window_size: int = 10,
        top_g: int = 5,
        device: str = "cpu"
    ):
        self.model_path = model_path
        self.vocab_path = vocab_path
        self.window_size = window_size
        self.top_g = top_g
        self.device = torch.device(device)
        self.fallback = RuleBasedAnomalyDetector()
        
        self.is_loaded = False
        self.model = None
        self.vocab = {}
        self.event_to_vocab = {}
        self.vocab_to_event = {}
        
        # In-memory sliding window history buffer per service: service -> List[int]
        self.session_windows = defaultdict(list)
        
        self._load_model_and_vocab()

    def _load_model_and_vocab(self):
        try:
            if not os.path.exists(self.model_path) or not os.path.exists(self.vocab_path):
                logger.warning(
                    f"DeepLog files not found at {self.model_path} or {self.vocab_path}. Falling back to Rule-based detection."
                )
                return

            with open(self.vocab_path, "rb") as f:
                vocab_data = pickle.load(f)
                self.vocab = vocab_data
                self.event_to_vocab = vocab_data.get("event_to_vocab", {})
                self.vocab_to_event = vocab_data.get("vocab_to_event", {})
                vocab_size = vocab_data.get("vocab_size", 31)

            self.model = DeepLogLSTM(
                vocab_size=vocab_size,
                embedding_dim=32,
                hidden_size=64,
                num_layers=2
            ).to(self.device)

            state = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(state)
            self.model.eval()
            self.is_loaded = True
            logger.info("DeepLog LSTM model and vocabulary successfully loaded into memory.")
        except Exception as e:
            logger.error(f"Failed to load DeepLog model: {e}", exc_info=True)
            self.is_loaded = False

    def _map_log_to_event_id(self, log: Log) -> int:
        """
        Maps a log entry to one of the 29 learned DeepLog template event IDs,
        or uses deterministic hashing into the event vocabulary range [1, 29].
        """
        msg = log.message.lower()
        if "exception" in msg or "error" in msg:
            return 4  # Got exception while serving / processing
        if "timeout" in msg:
            return 29 # PendingReplicationMonitor timed out block
        if "receiving" in msg:
            return 5  # Receiving block
        if "received" in msg:
            return 6  # Received block
        if "served" in msg:
            return 3  # Served block
        if "delete" in msg or "deleting" in msg:
            return 21 # Deleting block
        if "verification" in msg:
            return 2  # Verification succeeded
        if "adding" in msg:
            return 1  # Adding an already existing block
        
        # Deterministic hash to event range [1, 28] for general application log lines
        hash_val = sum(ord(c) for c in log.message) % 28 + 1
        return hash_val

    def evaluate_log(self, log: Log) -> DetectionResult:
        if not self.is_loaded:
            return self.fallback.evaluate_log(log)

        try:
            # Also invoke rule check for immediate critical security / crash events
            rule_check = self.fallback.evaluate_log(log)
            if rule_check.is_anomaly and rule_check.anomaly_score > 0.90:
                rule_check.detection_method = "deeplog_hybrid"
                return rule_check

            event_id = self._map_log_to_event_id(log)
            vocab_id = self.event_to_vocab.get(event_id, 1) # 1 is <UNK>

            window = self.session_windows[log.service]
            
            # If window is smaller than required, pad with 0 (<PAD>)
            if len(window) < self.window_size:
                padded = [0] * (self.window_size - len(window)) + window
            else:
                padded = window[-self.window_size:]

            # Forward pass
            x_tensor = torch.tensor([padded], dtype=torch.long, device=self.device)
            with torch.no_grad():
                logits = self.model(x_tensor)
                probs = F.softmax(logits, dim=1)[0]
                _, top_indices = torch.topk(logits, self.top_g, dim=1)
                top_preds = top_indices[0].tolist()

            # Append current vocab_id to service history window
            window.append(vocab_id)
            if len(window) > 50:
                self.session_windows[log.service] = window[-self.window_size:]

            is_anomaly = vocab_id not in top_preds
            actual_prob = float(probs[vocab_id].item())
            anomaly_score = max(0.0, 1.0 - actual_prob)

            predicted_events = [str(self.vocab_to_event.get(p, p)) for p in top_preds]

            return DetectionResult(
                is_anomaly=is_anomaly,
                anomaly_score=round(anomaly_score, 4),
                actual_event=f"E{event_id}",
                predicted_event=f"Top-{self.top_g}: {predicted_events}",
                supporting_evidence=(
                    f"Observed event template E{event_id} (P={actual_prob:.4f}) was not within "
                    f"DeepLog top-{self.top_g} predictions: {predicted_events}"
                ) if is_anomaly else "Log sequence aligns with DeepLog normal execution path.",
                detection_method="deeplog",
                details={
                    "event_id": event_id,
                    "vocab_id": vocab_id,
                    "top_predictions": top_preds,
                    "probability": actual_prob
                }
            )
        except Exception as e:
            logger.warning(f"DeepLog inference error, using rule fallback: {e}")
            return self.fallback.evaluate_log(log)

    def evaluate_sequence(self, sequence: List[int]) -> DetectionResult:
        if not self.is_loaded:
            return self.fallback.evaluate_sequence(sequence)

        try:
            L = len(sequence)
            if L <= self.window_size:
                padded = [0] * (self.window_size - L + 1) + sequence
                window = padded[:-1]
                target = padded[-1]
            else:
                window = sequence[-self.window_size - 1 : -1]
                target = sequence[-1]

            x_tensor = torch.tensor([window], dtype=torch.long, device=self.device)
            with torch.no_grad():
                logits = self.model(x_tensor)
                _, top_indices = torch.topk(logits, self.top_g, dim=1)
                top_preds = top_indices[0].tolist()

            is_anomaly = target not in top_preds
            return DetectionResult(
                is_anomaly=is_anomaly,
                anomaly_score=0.92 if is_anomaly else 0.08,
                actual_event=str(target),
                predicted_event=str(top_preds),
                supporting_evidence="Sequence evaluation against trained DeepLog LSTM model.",
                detection_method="deeplog"
            )
        except Exception as e:
            logger.error(f"Error evaluating sequence with DeepLog: {e}")
            return self.fallback.evaluate_sequence(sequence)

