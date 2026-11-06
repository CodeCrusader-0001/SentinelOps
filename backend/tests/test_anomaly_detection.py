import pytest
from backend.app.models.log import Log
from backend.app.detection.rule_detector import RuleBasedAnomalyDetector
from backend.app.detection.deeplog_detector import DeepLogDetector
from backend.app.detection.service import anomaly_detection_service
from backend.app.core.config import settings

def test_rule_based_anomaly_detection_error_and_critical():
    detector = RuleBasedAnomalyDetector()
    
    # Critical log
    crit_log = Log(
        application="auth",
        service="session-mgr",
        level="CRITICAL",
        message="Fatal crash: segmentation fault in thread 0x4a"
    )
    result = detector.evaluate_log(crit_log)
    assert result.is_anomaly is True
    assert result.anomaly_score >= 0.90
    assert result.detection_method == "rule_based"

    # Connection refused log
    conn_log = Log(
        application="db",
        service="postgres-pool",
        level="ERROR",
        message="Connection refused when connecting to database host 10.0.0.5:5432"
    )
    result = detector.evaluate_log(conn_log)
    assert result.is_anomaly is True
    assert "Connection" in result.actual_event

    # Normal log
    norm_log = Log(
        application="api",
        service="health-check",
        level="INFO",
        message="Service heartbeat OK, 200 responses handled"
    )
    norm_result = detector.evaluate_log(norm_log)
    assert norm_result.is_anomaly is False
    assert norm_result.anomaly_score < 0.20

def test_deeplog_detector_loading_and_evaluation():
    detector = DeepLogDetector(
        model_path=settings.DEEPLOG_MODEL_PATH,
        vocab_path=settings.DEEPLOG_VOCAB_PATH,
        window_size=10,
        top_g=5
    )
    assert detector.is_loaded is True
    assert detector.model is not None
    assert detector.vocab.get("vocab_size") == 31

    # Normal sequence
    normal_seq = [2, 3, 5, 6, 2, 3, 5, 6, 2, 3]
    res_normal = detector.evaluate_sequence(normal_seq)
    assert res_normal.detection_method == "deeplog"

    # Evaluate normal log
    normal_log = Log(
        application="hdfs",
        service="datanode",
        level="INFO",
        message="Receiving block blk_123456 src: 10.0.0.1 dest: 10.0.0.2"
    )
    res = detector.evaluate_log(normal_log)
    assert res.detection_method == "deeplog"
    assert "details" in res.__dict__

def test_unified_anomaly_detection_service():
    test_log = Log(
        application="payment-service",
        service="checkout",
        level="ERROR",
        message="OutOfMemoryError: Java heap space exhausted during settlement"
    )
    res = anomaly_detection_service.evaluate_log(test_log)
    assert res.is_anomaly is True
    assert res.anomaly_score > 0.50

