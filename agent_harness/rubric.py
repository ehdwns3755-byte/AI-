"""
프로젝트 품질 루브릭 정의
각 영역별 평가 기준 및 채점 시스템
"""

from typing import Dict, List, Tuple
from enum import Enum


class RubricLevel(Enum):
    """루브릭 단계"""
    EXCELLENT = 5
    GOOD = 4
    ACCEPTABLE = 3
    POOR = 2
    NOT_PRESENT = 1


class RubricArea(Enum):
    """평가 영역"""
    CODE_QUALITY = "코드 품질"
    ARCHITECTURE = "아키텍처 설계"
    DOCUMENTATION = "문서화"
    TESTING = "테스트"
    PERFORMANCE = "성능"
    SECURITY = "보안"
    USER_EXPERIENCE = "사용자 경험"
    OPERABILITY = "운영 안정성"


# 루브릭 정의
RUBRIC_DEFINITIONS = {
    RubricArea.CODE_QUALITY: {
        RubricLevel.EXCELLENT: [
            "일관된 코드 스타일",
            "명확한 변수명",
            "함수 분해 최적화",
            "낮은 복잡도",
            "주석은 필요한 곳만",
        ],
        RubricLevel.GOOD: [
            "대부분 일관된 스타일",
            "명확한 네이밍",
            "적절한 함수 크기",
            "복잡도 관리됨",
        ],
        RubricLevel.ACCEPTABLE: [
            "기본 스타일 준수",
            "이해 가능한 코드",
            "일부 복잡함수",
            "문서화 부족",
        ],
        RubricLevel.POOR: [
            "일관성 없음",
            "난해한 변수명",
            "함수 너무 큼",
            "높은 복잡도",
        ],
    },

    RubricArea.ARCHITECTURE: {
        RubricLevel.EXCELLENT: [
            "명확한 레이어 분리",
            "높은 응집도",
            "낮은 결합도",
            "확장성 극대화",
            "SOLID 원칙 준수",
        ],
        RubricLevel.GOOD: [
            "체계적인 모듈 구조",
            "분리된 관심사",
            "명확한 의존성",
            "확장 용이",
        ],
        RubricLevel.ACCEPTABLE: [
            "기본 모듈화",
            "일부 계층 분리",
            "의존성 관리 필요",
            "확장성 제한",
        ],
    },

    RubricArea.DOCUMENTATION: {
        RubricLevel.EXCELLENT: [
            "README + API docs + 다이어그램",
            "예제 코드",
            "트러블슈팅 가이드",
            "완전한 설정 문서",
        ],
        RubricLevel.GOOD: [
            "상세 README",
            "함수 docstring",
            "아키텍처 설명",
            "예제 코드",
        ],
        RubricLevel.ACCEPTABLE: [
            "기본 README",
            "부분적 주석",
            "일부 설명",
        ],
    },

    RubricArea.TESTING: {
        RubricLevel.EXCELLENT: [
            "Unit 테스트 >80%",
            "Integration 테스트",
            "E2E 테스트",
            "CI/CD 파이프라인",
        ],
        RubricLevel.GOOD: [
            "Unit 테스트 60-80%",
            "Integration 테스트",
            "자동 검증",
        ],
        RubricLevel.ACCEPTABLE: [
            "기본 테스트 <30%",
            "수동 검증",
        ],
    },

    RubricArea.PERFORMANCE: {
        RubricLevel.EXCELLENT: [
            "<1초 응답",
            "최적화된 알고리즘",
            "메모리 효율적",
            "캐싱 활용",
        ],
        RubricLevel.GOOD: [
            "1-5초 응답",
            "합리적 성능",
            "병목 최적화",
            "페이지네이션",
        ],
        RubricLevel.ACCEPTABLE: [
            "5-30초 응답",
            "기본 성능",
            "최적화 필요",
        ],
    },

    RubricArea.SECURITY: {
        RubricLevel.EXCELLENT: [
            "의존성 감시",
            "입력 검증",
            "SQL injection 방지",
            "암호화",
            "접근제어",
        ],
        RubricLevel.GOOD: [
            "기본 입력 검증",
            "안전한 라이브러리",
            "환경변수 사용",
        ],
        RubricLevel.ACCEPTABLE: [
            "일부 보안 조치",
            "기본 검증",
        ],
    },

    RubricArea.USER_EXPERIENCE: {
        RubricLevel.EXCELLENT: [
            "직관적 UI",
            "반응형 디자인",
            "빠른 로딩",
            "명확한 에러 메시지",
            "접근성 지원",
        ],
        RubricLevel.GOOD: [
            "깔끔한 UI",
            "기본 반응형",
            "빠른 속도",
            "좋은 레이아웃",
        ],
        RubricLevel.ACCEPTABLE: [
            "기본적인 인터페이스",
            "부분 반응형",
            "사용 가능",
        ],
    },

    RubricArea.OPERABILITY: {
        RubricLevel.EXCELLENT: [
            "CI/CD 파이프라인",
            "모니터링",
            "로깅",
            "백업",
            "자동화",
        ],
        RubricLevel.GOOD: [
            "스크립트 자동화",
            "기본 로깅",
            "스케줄링",
            "에러 추적",
        ],
        RubricLevel.ACCEPTABLE: [
            "수동 운영 대부분",
            "기본 로깅",
        ],
    },
}


class RubricCriteria:
    """루브릭 평가 기준"""

    def __init__(self):
        self.scores: Dict[RubricArea, Tuple[RubricLevel, str]] = {}
        self.details: Dict[RubricArea, List[str]] = {}

    def set_score(
        self,
        area: RubricArea,
        level: RubricLevel,
        details: List[str] = None,
    ) -> None:
        """평가 점수 설정"""
        self.scores[area] = (level, area.value)
        if details:
            self.details[area] = details

    def get_average_score(self) -> float:
        """평균 점수 계산"""
        if not self.scores:
            return 0.0
        total = sum(level.value for level, _ in self.scores.values())
        return total / len(self.scores)

    def get_grade(self) -> str:
        """등급 계산"""
        avg = self.get_average_score()
        if avg >= 4.5:
            return "A+"
        elif avg >= 4.0:
            return "A"
        elif avg >= 3.5:
            return "B+"
        elif avg >= 3.0:
            return "B"
        elif avg >= 2.5:
            return "C"
        else:
            return "F"

    def get_summary(self) -> Dict:
        """평가 요약"""
        return {
            "scores": {
                area.value: level.value
                for area, (level, _) in self.scores.items()
            },
            "average": round(self.get_average_score(), 2),
            "grade": self.get_grade(),
            "details": self.details,
        }


def get_rubric_definition(
    area: RubricArea,
    level: RubricLevel,
) -> List[str]:
    """루브릭 정의 조회"""
    return RUBRIC_DEFINITIONS.get(area, {}).get(level, [])


def compare_with_rubric(
    current_score: float,
    previous_score: float,
    area: RubricArea,
) -> Dict:
    """루브릭과 비교"""
    improvement = current_score - previous_score
    percentage = (improvement / previous_score * 100) if previous_score > 0 else 0

    return {
        "area": area.value,
        "previous": previous_score,
        "current": current_score,
        "improvement": round(improvement, 2),
        "percentage": round(percentage, 1),
        "trend": "상승" if improvement > 0 else "하락" if improvement < 0 else "유지",
    }
