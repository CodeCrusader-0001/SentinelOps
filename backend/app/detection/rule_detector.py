import re
from typing import List, Dict, Any
from backend.app.detection.base import BaseAnomalyDetector, DetectionResult
from backend.app.models.log import Log

class RuleBasedAnomalyDetector(BaseAnomalyDetector):
    """
    Deterministic rule-based anomaly detector.
    Acts as a production-grade heuristic fallback when ML models are unavailable or uninitialized.
    """
    ANOMALY_PATTERNS = [
        (re.compile(r"connection\s*refused|connection\s*reset|timeout|unreachable", re.I), "Network / Connection Degradation", 0.92),
        (re.compile(r"out\s*of\s*memory|oomkiller|heap\s*exhausted|memory\s*leak", re.I), "Memory Exhaustion Anomaly", 0.95),
        (re.compile(r"deadlock|lock\s*wait\s*timeout|transaction\s*aborted", re.I), "Database Concurrency Anomaly", 0.92),
        (re.compile(r"disk\s*full|no\s*space\s*left|filesystem\s*corrupt", re.I), "Storage Failure Anomaly", 0.92),
        (re.compile(r"circuit\s*breaker\s*open|rate\s*limit\s*exceeded|too\s*many\s*requests", re.I), "Traffic Spike Anomaly", 0.85),
        (re.compile(r"fatal|panic|segmentation\s*fault|core\s*dumped", re.I), "Process Crash Anomaly", 0.98),
    ]

    def evaluate_log(self, log: Log) -> DetectionResult:
        msg = log.message or ""
        
        # Immediate check on Critical severity
        if log.level in ["CRITICAL"]:
            return DetectionResult(
                is_anomaly=True,
                anomaly_score=0.95,
                actual_event=f"{log.service}:CRITICAL",
                predicted_event="NORMAL_EXECUTION",
                supporting_evidence=f"Critical system log event in service '{log.service}': {msg[:120]}",
                detection_method="rule_based",
                details={"level": log.level, "service": log.service}
            )

        # Pattern match for failure signatures
        for pattern, anomaly_type, score in self.ANOMALY_PATTERNS:
            match = pattern.search(msg)
            if match:
                return DetectionResult(
                    is_anomaly=True,
                    anomaly_score=score,
                    actual_event=f"{log.service}:{anomaly_type}",
                    predicted_event="HEALTHY_STATUS",
                    supporting_evidence=f"Matched anomaly heuristic '{anomaly_type}' on token: '{match.group(0)}'",
                    detection_method="rule_based",
                    details={"pattern": anomaly_type, "matched_text": match.group(0)}
                )

        # High error density in error level
        if log.level in ["ERROR"]:
            return DetectionResult(
                is_anomaly=True,
                anomaly_score=0.70,
                actual_event=f"{log.service}:ERROR",
                predicted_event="INFO",
                supporting_evidence=f"Error level condition detected in service '{log.service}'",
                detection_method="rule_based",
                details={"level": log.level}
            )

        return DetectionResult(
            is_anomaly=False,
            anomaly_score=0.05,
            actual_event=f"{log.service}:NORMAL",
            predicted_event="NORMAL",
            supporting_evidence="Log matched expected steady-state operating parameters.",
            detection_method="rule_based"
        )

    def evaluate_sequence(self, sequence: List[int]) -> DetectionResult:
        # Rule check on sequence token values
        has_error_token = any(token > 20 for token in sequence)
        return DetectionResult(
            is_anomaly=has_error_token,
            anomaly_score=0.80 if has_error_token else 0.10,
            actual_event=str(sequence[-1]) if sequence else "0",
            predicted_event="<=20",
            supporting_evidence="Sequence token threshold rule check",
            detection_method="rule_based"
        )
