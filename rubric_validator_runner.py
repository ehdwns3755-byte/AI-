#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
루브릭 검증 도구 - Agent Harness 통합

이 도구는 프로젝트를 루브릭 기준에 따라 자동으로 평가합니다.
하네스를 통해 Claude가 호출할 수 있는 @beta_tool로 등록됩니다.

사용법:
    python rubric_validator_runner.py

결과:
    RUBRIC_VALIDATION_REPORT.md - 상세 검증 보고서
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

from agent_harness.validators import run_validation
from agent_harness.rubric import RubricArea
from agent_harness.logger import get_logger

logger = get_logger(__name__)


def generate_validation_report(validation_results: Dict) -> str:
    """검증 결과를 마크다운 보고서로 생성"""

    report = f"""# 루브릭 검증 보고서

**생성일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 최종 평가

**등급**: {validation_results['grade']}
**평균 점수**: {validation_results['average']}/5.0

### 점수 분포

"""

    # 점수 테이블
    report += """| 영역 | 점수 | 평가 |
|------|------|------|
"""

    scores = validation_results['scores']
    for area_name, score in scores.items():
        stars = "[*]" * int(score)
        report += f"| {area_name} | {score}/5 | {stars} |\n"

    # 상세 내용
    report += "\n## 📋 상세 평가\n\n"

    details = validation_results.get('details', {})

    for area_name, findings in details.items():
        report += f"### {area_name}\n\n"
        for finding in findings:
            report += f"- {finding}\n"
        report += "\n"

    # 권장사항
    report += "## 개선 권장사항\n\n"

    areas_by_score = sorted(
        scores.items(),
        key=lambda x: x[1]
    )

    for area, score in areas_by_score[:3]:  # 점수가 낮은 상위 3개
        if score < 5:
            report += f"### {area}\n"
            report += f"**현재 점수**: {score}/5\n"
            report += f"**권장사항**:\n"
            if score < 3:
                report += "- 주요 개선 필요\n"
            else:
                report += "- 추가 개선으로 더 나은 결과 가능\n"
            report += "\n"

    # 강점
    report += "## 프로젝트 강점\n\n"

    for area, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]:
        if score >= 4:
            report += f"- **{area}**: {score}/5 - 우수 수준\n"

    report += f"\n## 최종 결론\n\n"

    if validation_results['average'] >= 4.5:
        conclusion = (
            f"프로젝트가 **매우 우수한 품질**을 유지하고 있습니다. "
            f"현재 {validation_results['grade']} 등급으로 평가되며, "
            f"프로덕션 환경에 배포할 준비가 충분합니다."
        )
    elif validation_results['average'] >= 4.0:
        conclusion = (
            f"프로젝트가 **좋은 품질**을 유지하고 있습니다. "
            f"현재 {validation_results['grade']} 등급이며, "
            f"몇 가지 개선으로 최고의 품질을 달성할 수 있습니다."
        )
    elif validation_results['average'] >= 3.0:
        conclusion = (
            f"프로젝트가 **기본적인 품질**을 갖추고 있습니다. "
            f"현재 {validation_results['grade']} 등급이며, "
            f"여러 영역에서 개선이 필요합니다."
        )
    else:
        conclusion = (
            f"프로젝트의 **품질 개선이 필수적**입니다. "
            f"현재 {validation_results['grade']} 등급으로 평가되며, "
            f"주요 개선 작업이 필요합니다."
        )

    report += conclusion

    return report


def save_report(report_content: str, output_file: str = "RUBRIC_VALIDATION_REPORT.md") -> str:
    """보고서를 파일로 저장"""
    output_path = Path(output_file)
    output_path.write_text(report_content, encoding="utf-8")
    logger.info(f"검증 보고서 저장: {output_path.absolute()}")
    return str(output_path.absolute())


def print_validation_summary(validation_results: Dict) -> None:
    """검증 결과를 콘솔에 출력"""
    print("\n" + "="*70)
    print("루브릭 검증 결과")
    print("="*70)

    scores = validation_results['scores']
    print("\n[점수]")
    for area, score in scores.items():
        stars = "[*]" * int(score)
        print(f"  {area:15} {stars} ({score}/5)")

    print(f"\n[최종 평가]")
    print(f"  평균 점수: {validation_results['average']}/5.0")
    print(f"  등급: {validation_results['grade']}")
    print("\n" + "="*70 + "\n")


def main() -> int:
    """메인 함수"""
    try:
        print("\n" + "[루브릭 검증 시작]".center(70))
        print("="*70 + "\n")

        # 검증 실행
        logger.info("프로젝트 품질 검증을 시작합니다...")
        validation_results = run_validation(project_root=".")

        # 결과 출력
        print_validation_summary(validation_results)

        # 보고서 생성
        logger.info("검증 보고서를 생성 중입니다...")
        report_content = generate_validation_report(validation_results)

        # 파일 저장
        report_path = save_report(report_content)

        print(f"[OK] 검증 완료!")
        print(f"[FILE] 보고서: {report_path}")
        print(f"[GRADE] 등급: {validation_results['grade']}")
        print(f"[AVG] 평균: {validation_results['average']}/5.0\n")

        # JSON으로도 저장
        json_path = Path("RUBRIC_VALIDATION_RESULT.json")
        # RubricArea enum을 문자열로 변환
        json_safe_results = {
            "grade": validation_results['grade'],
            "average": validation_results['average'],
            "scores": {str(k): v for k, v in validation_results['scores'].items()},
        }
        json_path.write_text(
            json.dumps(json_safe_results, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        logger.info(f"JSON 결과: {json_path.absolute()}")

        return 0 if validation_results['average'] >= 3.0 else 1

    except Exception as e:
        logger.error(f"검증 중 오류 발생: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
