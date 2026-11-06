from backend.app.core.config import settings
from backend.app.detection.base import BaseAnomalyDetector, DetectionResult
from backend.app.detection.deeplog_detector import DeepLogDetector
from backend.app.detection.rule_detector import RuleBasedAnomalyDetector
from backend.app.models.log import Log

class AnomalyDetectionService:
    def __init__(self):
        if settings.ANOMALY_DETECTOR_TYPE.lower() == "deeplog":
            self.detector: BaseAnomalyDetector = DeepLogDetector(
                model_path=settings.DEEPLOG_MODEL_PATH,
                vocab_path=settings.DEEPLOG_VOCAB_PATH,
                window_size=settings.DEEPLOG_WINDOW_SIZE,
                top_g=settings.DEEPLOG_TOP_G
            )
        else:
            self.detector = RuleBasedAnomalyDetector()

    def evaluate_log(self, log: Log) -> DetectionResult:
        return self.detector.evaluate_log(log)

anomaly_detection_service = AnomalyDetectionService()

