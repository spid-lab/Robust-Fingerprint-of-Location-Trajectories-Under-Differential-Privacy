from enum import Enum


class EvaluationMetric(Enum):
    QA_POINTS = "qa_points"
    QA_PATTERNS = "qa_patterns"
    AREA_POPULARITY = "area_popularity"
    TRIP_ERROR = "trip_error"
    DIAMETER_ERROR = "diameter_error"
    TRIP_SIMILARITY = "trip_similarity"
