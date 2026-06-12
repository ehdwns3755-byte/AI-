"""
자동화된 품질 검증 엔진
루브릭 기준에 따라 프로젝트 품질 평가
"""

import json
import ast
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess

from agent_harness.rubric import (
    RubricArea,
    RubricLevel,
    RubricCriteria,
    RUBRIC_DEFINITIONS,
)
from agent_harness.logger import get_logger

logger = get_logger(__name__)


class QualityValidator:
    """품질 검증기"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.criteria = RubricCriteria()
        self.validation_results = {}

    # ========== 코드 품질 검증 ==========

    def validate_code_quality(self) -> Tuple[RubricLevel, List[str]]:
        """코드 품질 검증"""
        logger.info("코드 품질 검증 중...")
        findings = []

        # 1. 타입 힌팅 확인
        type_hints_ratio = self._check_type_hints()
        findings.append(f"타입 힌팅: {type_hints_ratio:.0%}")

        # 2. Docstring 확인
        docstring_ratio = self._check_docstrings()
        findings.append(f"Docstring: {docstring_ratio:.0%}")

        # 3. 코드 복잡도 확인
        complexity = self._check_complexity()
        findings.append(f"평균 복잡도: {complexity:.1f}")

        # 4. 라인 길이 확인
        long_lines = self._check_line_length()
        findings.append(f"긴 라인: {long_lines}개")

        # 평가
        score = (
            (type_hints_ratio * 0.3)
            + (docstring_ratio * 0.3)
            + (1 - min(complexity / 10, 1) * 0.2)
            + (1 - min(long_lines / 100, 1) * 0.2)
        )

        if score >= 0.9:
            level = RubricLevel.EXCELLENT
        elif score >= 0.7:
            level = RubricLevel.GOOD
        elif score >= 0.5:
            level = RubricLevel.ACCEPTABLE
        else:
            level = RubricLevel.POOR

        logger.info(f"코드 품질: {level.name}")
        self.criteria.set_score(RubricArea.CODE_QUALITY, level, findings)
        return level, findings

    def _check_type_hints(self) -> float:
        """타입 힌팅 비율 확인"""
        total_funcs = 0
        hinted_funcs = 0

        for py_file in self.project_root.rglob("*.py"):
            if "test" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_funcs += 1
                        # return type이 있으면 카운트
                        if node.returns:
                            hinted_funcs += 1
            except:
                pass

        return hinted_funcs / total_funcs if total_funcs > 0 else 0.0

    def _check_docstrings(self) -> float:
        """Docstring 비율 확인"""
        total_funcs = 0
        documented = 0

        for py_file in self.project_root.rglob("*.py"):
            if "test" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_funcs += 1
                        if ast.get_docstring(node):
                            documented += 1
            except:
                pass

        return documented / total_funcs if total_funcs > 0 else 0.0

    def _check_complexity(self) -> float:
        """평균 복잡도 확인"""
        complexities = []

        for py_file in self.project_root.rglob("*.py"):
            if "test" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 간단한 복잡도: if/for/while/try 개수
                    complexity = (
                        content.count("if ")
                        + content.count("for ")
                        + content.count("while ")
                        + content.count("try:")
                    )
                    complexities.append(complexity)
            except:
                pass

        return sum(complexities) / len(complexities) if complexities else 0.0

    def _check_line_length(self) -> int:
        """긴 라인(>100자) 개수"""
        long_lines = 0

        for py_file in self.project_root.rglob("*.py"):
            if "test" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if len(line.rstrip()) > 100:
                            long_lines += 1
            except:
                pass

        return long_lines

    # ========== 아키텍처 검증 ==========

    def validate_architecture(self) -> Tuple[RubricLevel, List[str]]:
        """아키텍처 검증"""
        logger.info("아키텍처 검증 중...")
        findings = []

        # 1. 모듈 구조 확인
        has_agent_harness = (self.project_root / "agent_harness").exists()
        findings.append(f"agent_harness 패키지: {'있음' if has_agent_harness else '없음'}")

        # 2. 분리된 관심사
        has_tools = (self.project_root / "agent_harness" / "tools").exists()
        findings.append(f"tools 모듈 분리: {'있음' if has_tools else '없음'}")

        has_config = (self.project_root / "agent_harness" / "config.py").exists() or \
                     (self.project_root / "agent_harness" / "constants.py").exists()
        findings.append(f"설정 중앙화: {'있음' if has_config else '없음'}")

        # 3. 테스트 분리
        has_tests = (self.project_root / "tests").exists()
        findings.append(f"테스트 디렉토리: {'있음' if has_tests else '없음'}")

        # 평가
        score = sum([
            has_agent_harness * 0.25,
            has_tools * 0.25,
            has_config * 0.25,
            has_tests * 0.25,
        ])

        if score >= 0.9:
            level = RubricLevel.EXCELLENT
        elif score >= 0.7:
            level = RubricLevel.GOOD
        elif score >= 0.5:
            level = RubricLevel.ACCEPTABLE
        else:
            level = RubricLevel.POOR

        logger.info(f"아키텍처: {level.name}")
        self.criteria.set_score(RubricArea.ARCHITECTURE, level, findings)
        return level, findings

    # ========== 문서화 검증 ==========

    def validate_documentation(self) -> Tuple[RubricLevel, List[str]]:
        """문서화 검증"""
        logger.info("문서화 검증 중...")
        findings = []

        # 1. README 확인
        has_readme = (self.project_root / "README.md").exists()
        findings.append(f"README.md: {'있음' if has_readme else '없음'}")

        # 2. CLAUDE.md 확인
        has_claude = (self.project_root / "CLAUDE.md").exists()
        findings.append(f"CLAUDE.md: {'있음' if has_claude else '없음'}")

        # 3. 아키텍처 문서
        has_arch = (self.project_root / "AGENT_HARNESS.md").exists()
        findings.append(f"AGENT_HARNESS.md: {'있음' if has_arch else '없음'}")

        # 4. 품질 보고서
        has_quality = (self.project_root / "QUALITY_REPORT.md").exists()
        findings.append(f"QUALITY_REPORT.md: {'있음' if has_quality else '없음'}")

        # 평가
        score = sum([
            has_readme * 0.25,
            has_claude * 0.25,
            has_arch * 0.25,
            has_quality * 0.25,
        ])

        if score >= 0.9:
            level = RubricLevel.EXCELLENT
        elif score >= 0.7:
            level = RubricLevel.GOOD
        elif score >= 0.5:
            level = RubricLevel.ACCEPTABLE
        else:
            level = RubricLevel.POOR

        logger.info(f"문서화: {level.name}")
        self.criteria.set_score(RubricArea.DOCUMENTATION, level, findings)
        return level, findings

    # ========== 테스트 검증 ==========

    def validate_testing(self) -> Tuple[RubricLevel, List[str]]:
        """테스트 검증"""
        logger.info("테스트 검증 중...")
        findings = []

        # 1. 테스트 파일 개수
        test_files = list(self.project_root.rglob("test_*.py"))
        findings.append(f"테스트 파일: {len(test_files)}개")

        # 2. pytest 설정
        has_pytest = (self.project_root / "pytest.ini").exists() or \
                     (self.project_root / "pyproject.toml").exists()
        findings.append(f"pytest 설정: {'있음' if has_pytest else '없음'}")

        # 3. 테스트 함수 개수
        test_functions = 0
        for test_file in test_files:
            try:
                with open(test_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    test_functions += content.count("def test_")
            except:
                pass

        findings.append(f"테스트 함수: {test_functions}개")

        # 평가
        if test_functions >= 30:
            level = RubricLevel.EXCELLENT
        elif test_functions >= 20:
            level = RubricLevel.GOOD
        elif test_functions >= 10:
            level = RubricLevel.ACCEPTABLE
        else:
            level = RubricLevel.POOR

        logger.info(f"테스트: {level.name}")
        self.criteria.set_score(RubricArea.TESTING, level, findings)
        return level, findings

    # ========== 성능 검증 ==========

    def validate_performance(self) -> Tuple[RubricLevel, List[str]]:
        """성능 검증"""
        logger.info("성능 검증 중...")
        findings = []

        # 1. 캐싱 구현
        has_cache = (self.project_root / "agent_harness" / "cache.py").exists()
        findings.append(f"캐싱: {'구현됨' if has_cache else '미구현'}")

        # 2. 최적화 주석
        optimization_comments = 0
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    optimization_comments += content.count("# 최적화") + \
                                            content.count("# optimization")
            except:
                pass

        findings.append(f"최적화 주석: {optimization_comments}개")

        # 평가
        if has_cache:
            level = RubricLevel.GOOD
        else:
            level = RubricLevel.ACCEPTABLE

        logger.info(f"성능: {level.name}")
        self.criteria.set_score(RubricArea.PERFORMANCE, level, findings)
        return level, findings

    # ========== 보안 검증 ==========

    def validate_security(self) -> Tuple[RubricLevel, List[str]]:
        """보안 검증"""
        logger.info("보안 검증 중...")
        findings = []

        # 1. 예외 처리
        has_exceptions = (self.project_root / "agent_harness" / "exceptions.py").exists()
        findings.append(f"커스텀 예외: {'있음' if has_exceptions else '없음'}")

        # 2. 입력 검증
        validation_count = 0
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    validation_count += content.count("validate_") + \
                                       content.count("if not ")
            except:
                pass

        findings.append(f"검증 함수: {validation_count}개")

        # 3. 환경변수 사용
        has_env_config = False
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    if "os.getenv" in f.read() or "dotenv" in f.read():
                        has_env_config = True
                        break
            except:
                pass

        findings.append(f"환경변수 설정: {'사용중' if has_env_config else '미사용'}")

        # 평가
        if has_exceptions and has_env_config:
            level = RubricLevel.GOOD
        elif has_exceptions:
            level = RubricLevel.ACCEPTABLE
        else:
            level = RubricLevel.POOR

        logger.info(f"보안: {level.name}")
        self.criteria.set_score(RubricArea.SECURITY, level, findings)
        return level, findings

    # ========== UX 검증 ==========

    def validate_ux(self) -> Tuple[RubricLevel, List[str]]:
        """UX 검증"""
        logger.info("UX 검증 중...")
        findings = []

        # 1. 대시보드 파일
        dashboards = list(self.project_root.glob("*dashboard*.html"))
        findings.append(f"대시보드: {len(dashboards)}개")

        # 2. 고급 기능 확인
        has_search = False
        has_dark_mode = False
        has_responsive = False

        for dashboard in dashboards:
            try:
                with open(dashboard, "r", encoding="utf-8") as f:
                    content = f.read()
                    has_search = has_search or "search" in content.lower()
                    has_dark_mode = has_dark_mode or "dark" in content.lower()
                    has_responsive = has_responsive or "responsive" in content or "@media" in content
            except:
                pass

        findings.append(f"검색 기능: {'있음' if has_search else '없음'}")
        findings.append(f"다크모드: {'있음' if has_dark_mode else '없음'}")
        findings.append(f"반응형 디자인: {'있음' if has_responsive else '없음'}")

        # 평가
        features = sum([has_search, has_dark_mode, has_responsive, len(dashboards) > 0])
        if features >= 3:
            level = RubricLevel.EXCELLENT
        elif features >= 2:
            level = RubricLevel.GOOD
        elif features >= 1:
            level = RubricLevel.ACCEPTABLE
        else:
            level = RubricLevel.POOR

        logger.info(f"UX: {level.name}")
        self.criteria.set_score(RubricArea.USER_EXPERIENCE, level, findings)
        return level, findings

    # ========== 운영 안정성 검증 ==========

    def validate_operability(self) -> Tuple[RubricLevel, List[str]]:
        """운영 안정성 검증"""
        logger.info("운영 안정성 검증 중...")
        findings = []

        # 1. 로깅 시스템
        has_logging = (self.project_root / "agent_harness" / "logger.py").exists()
        findings.append(f"로깅 시스템: {'있음' if has_logging else '없음'}")

        # 2. 스케줄러
        has_scheduler = list(self.project_root.glob("*scheduler*.py"))
        findings.append(f"스케줄러: {len(has_scheduler)}개")

        # 3. 모니터링/헬스 체크
        has_monitoring = False
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    if "health" in f.read().lower() or "monitor" in f.read().lower():
                        has_monitoring = True
                        break
            except:
                pass

        findings.append(f"모니터링: {'있음' if has_monitoring else '없음'}")

        # 평가
        if has_logging and len(has_scheduler) > 0:
            level = RubricLevel.GOOD
        elif has_logging:
            level = RubricLevel.ACCEPTABLE
        else:
            level = RubricLevel.POOR

        logger.info(f"운영 안정성: {level.name}")
        self.criteria.set_score(RubricArea.OPERABILITY, level, findings)
        return level, findings

    # ========== 전체 검증 ==========

    def validate_all(self) -> Dict:
        """모든 영역 검증"""
        logger.info("="*70)
        logger.info("전체 품질 검증 시작")
        logger.info("="*70)

        # 각 영역별 검증
        self.validate_code_quality()
        self.validate_architecture()
        self.validate_documentation()
        self.validate_testing()
        self.validate_performance()
        self.validate_security()
        self.validate_ux()
        self.validate_operability()

        # 결과 정리
        summary = self.criteria.get_summary()

        logger.info("="*70)
        logger.info(f"최종 등급: {summary['grade']} ({summary['average']}/5)")
        logger.info("="*70)

        return summary


def run_validation(project_root: str = ".") -> Dict:
    """검증 실행"""
    validator = QualityValidator(project_root)
    return validator.validate_all()
