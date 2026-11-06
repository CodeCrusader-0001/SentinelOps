from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from backend.app.models.log import Log

@dataclass
class DetectionResult:
    is_anomaly: bool
    anomaly_score: float
    actual_event: str
    predicted_event: Optional[str] = None
    supporting_evidence: str = ""
    detection_method: str = "deeplog"
    details: Dict[str, Any] = field(default_factory=dict)

class BaseAnomalyDetector(ABC):
    @abstractmethod
    def evaluate_log(self, log: Log) -> DetectionResult:
        """Evaluates a single log event within its session/service context."""
        pass

    @abstractmethod
    def evaluate_sequence(self, sequence: List[int]) -> DetectionResult:
        """Evaluates a numeric token/event sequence."""
        pass

