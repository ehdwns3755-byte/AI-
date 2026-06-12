#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
매일 아침 8시마다 경제뉴스를 수집하고 대시보드 생성

사용법:
    python daily_economics_scheduler.py
"""

import json
import schedule
import time
from datetime import datetime
from pathlib import Path

from agent_harness.tools.economics_news import (
    fetch_economics_news,
    categorize_economics_news,
    generate_economics_summary,
)


def generate_economics_dashboard(news_data, categorized, summary):
    """경제뉴스 대시보드 HTML 생성"""

    articles = news_data.get('articles', [])
    categories = categorized.get('categorized', {})

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>경제뉴스 일일 정리 - {summary['date']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #1e3c72;
            padding-bottom: 30px;
        }}
        h1 {{
            color: #1e3c72;
            font-size: 36px;
            margin-bottom: 10px;
        }}
        .date-info {{
            color: #666;
            font-size: 16px;
            margin-bottom: 20px;
        }}
        .date-info span {{
            font-weight: 600;
            color: #1e3c72;
        }}

        .market-overview {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 40px;
            font-size: 16px;
            line-height: 1.8;
        }}

        .key-points {{
            background: #f5f5f5;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 40px;
            border-left: 4px solid #1e3c72;
        }}
        .key-points h3 {{
            color: #1e3c72;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        .key-points ul {{
            list-style: none;
            padding-left: 0;
        }}
        .key-points li {{
            padding: 8px 0;
            padding-left: 24px;
            position: relative;
            color: #333;
        }}
        .key-points li:before {{
            content: "→";
            position: absolute;
            left: 0;
            color: #1e3c72;
            font-weight: bold;
        }}

        .section {{
            margin-bottom: 50px;
        }}
        .section h2 {{
            color: #1e3c72;
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        .section .count {{
            display: inline-block;
            background: #1e3c72;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }}
        .card {{
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s;
            background: white;
            border-left: 4px solid #2a5298;
            display: flex;
            flex-direction: column;
        }}
        .card:hover {{
            box-shadow: 0 12px 40px rgba(30, 60, 114, 0.2);
            transform: translateY(-6px);
        }}
        .card-source {{
            font-size: 11px;
            color: #1e3c72;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .card h3 {{
            color: #333;
            font-size: 15px;
            margin-bottom: 10px;
            line-height: 1.4;
            font-weight: 600;
        }}
        .card p {{
            font-size: 13px;
            color: #666;
            line-height: 1.6;
            flex-grow: 1;
        }}
        .card-link {{
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #f0f0f0;
        }}
        .card a {{
            color: #2a5298;
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
        }}
        .card a:hover {{
            text-decoration: underline;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stat {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-num {{
            font-size: 24px;
            font-weight: bold;
            color: #1e3c72;
        }}
        .stat-label {{
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }}

        .footer {{
            text-align: center;
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid #e0e0e0;
            color: #999;
            font-size: 12px;
        }}
        .footer p {{
            margin: 5px 0;
        }}

        .no-data {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 헤더 -->
        <div class="header">
            <h1>📊 경제뉴스 일일 정리</h1>
            <div class="date-info">
                <span>{summary['date']}</span> | {summary['time']} 업데이트
            </div>
        </div>

        <!-- 시장 개요 -->
        <div class="market-overview">
            <strong>오늘의 시장 요약</strong>
            <p style="margin-top: 12px; margin-bottom: 0;">
                {summary['market_overview']}
            </p>
        </div>

        <!-- 핵심 포인트 -->
        <div class="key-points">
            <h3>📍 주요 포인트</h3>
            <ul>
"""

    for point in summary.get('key_points', []):
        html += f'                <li>{point}</li>\n'

    html += f"""            </ul>
        </div>

        <!-- 통계 -->
        <div class="stats">
"""

    for cat, info in categories.items():
        count = info.get('count', 0)
        html += f"""            <div class="stat">
                <div class="stat-num">{count}</div>
                <div class="stat-label">{cat}</div>
            </div>
"""

    html += """        </div>

        <!-- 뉴스 섹션 -->
"""

    for category, info in categories.items():
        cat_articles = info.get('articles', [])
        if cat_articles:
            html += f"""        <div class="section">
            <h2>{category}<span class="count">{info.get('count', 0)}개</span></h2>
            <div class="cards">
"""

            for article in cat_articles:
                html += f"""                <div class="card">
                    <div class="card-source">{article.get('source', 'Unknown')}</div>
                    <h3>{article.get('title', 'No title')}</h3>
                    <p>{article.get('summary', '')}</p>
                    <div class="card-link">
                        <a href="{article.get('url', '#')}" target="_blank">원문 읽기 →</a>
                    </div>
                </div>
"""

            html += """            </div>
        </div>

"""

    html += f"""        <!-- 푸터 -->
        <div class="footer">
            <p>🤖 AI 트렌드 대시보드 - Agent Harness 시스템</p>
            <p>매일 아침 8시마다 자동 생성됩니다</p>
            <p>생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""

    return html


def job():
    """매일 8시마다 실행될 작업"""

    print(f"\n{'='*70}")
    print(f"[경제뉴스 수집 시작] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    try:
        # 1단계: 뉴스 수집
        print("\n[1단계] 경제뉴스 수집 중...")
        news_result = fetch_economics_news(days=1)
        news_data = json.loads(news_result)
        print(f"[OK] {news_data.get('count', 0)}개의 뉴스 수집 완료")

        # 2단계: 뉴스 분류
        print("\n[2단계] 뉴스 분류 중...")
        categorized_result = categorize_economics_news(news_result)
        categorized_data = json.loads(categorized_result)
        print("[OK] 카테고리별 분류 완료")

        # 3단계: 요약 생성
        print("\n[3단계] 요약 생성 중...")
        summary_result = generate_economics_summary(categorized_result)
        summary_data = json.loads(summary_result)
        print("[OK] 핵심 요약 생성 완료")

        # 4단계: 대시보드 생성
        print("\n[4단계] 대시보드 생성 중...")
        html = generate_economics_dashboard(news_data, categorized_data, summary_data)

        # 파일 저장
        output_path = Path("economics_news_daily.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"[OK] 대시보드 저장 완료: {output_path}")

        # 완료 메시지
        print(f"\n{'='*70}")
        print(f"[SUCCESS] 경제뉴스 정리 완료!")
        print(f"파일: {output_path.absolute()}")
        print(f"브라우저: http://localhost:8000/economics_news_daily.html")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")


def main():
    """메인 함수 - 스케줄러 시작"""

    print("\n" + "="*70)
    print("[경제뉴스 일일 정리 시스템 시작]")
    print("="*70)
    print("\n스케줄 설정:")
    print("  [시간] 매일 아침 8시에 실행")
    print("  [파일] 저장 위치: economics_news_daily.html")
    print("  [웹] 접속 주소: http://localhost:8000/economics_news_daily.html")
    print("\n종료 명령: Ctrl+C\n")

    # 매일 8시에 실행하도록 스케줄 설정
    schedule.every().day.at("08:00").do(job)

    # 즉시 실행 (테스트용)
    print("초기 테스트 실행 중...\n")
    job()

    # 스케줄러 실행
    print("\n스케줄러 대기 중...")
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 확인
        except KeyboardInterrupt:
            print("\n\n프로그램 종료됨")
            break
        except Exception as e:
            print(f"오류: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
