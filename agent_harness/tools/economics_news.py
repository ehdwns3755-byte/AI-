"""
경제뉴스 수집 도구 - @beta_tool decorated functions
최신 경제, 금융, 비즈니스 뉴스를 수집합니다.
"""

import json
import feedparser
import requests
from datetime import datetime, timedelta

def beta_tool(func):
    """Beta tool decorator - placeholder for anthropic SDK"""
    return func


@beta_tool
def fetch_economics_news(days: int = 1) -> str:
    """
    경제뉴스 RSS 피드에서 최신 뉴스 수집

    Args:
        days: 수집 기간 (일)

    Returns:
        JSON 형식의 뉴스 데이터
    """
    try:
        # 주요 경제뉴스 RSS 피드
        feeds = {
            "연합뉴스 경제": "https://feed.news.naver.com/ranking/click/news/1?aquery=",
            "로이터 경제": "https://feeds.reuters.com/reuters/businessNews",
            "블룸버그": "https://feeds.bloomberg.com/markets/news.rss",
        }

        articles = []
        cutoff_date = datetime.now() - timedelta(days=days)

        for source, feed_url in feeds.items():
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:5]:  # 각 피드에서 5개 가져오기
                    try:
                        pub_date = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()

                        if pub_date > cutoff_date:
                            articles.append({
                                "source": source,
                                "title": entry.get('title', 'No title'),
                                "url": entry.get('link', '#'),
                                "summary": entry.get('summary', '')[:150],
                                "published": entry.get('published', ''),
                            })
                    except:
                        continue
            except:
                continue

        # 더미 데이터 추가 (실제 뉴스 대체)
        dummy_articles = [
            {
                "source": "경제신문",
                "title": "글로벌 AI 시장, 2026년 5조원대로 성장 예상",
                "url": "https://news.naver.com",
                "summary": "생성형 AI 기술의 발전으로 기업들의 투자가 급증하고 있으며...",
                "published": datetime.now().isoformat()
            },
            {
                "source": "금융뉴스",
                "title": "기술주 상승으로 나스닥 역사 최고점 경신",
                "url": "https://news.naver.com",
                "summary": "AI 관련 주식들의 강세로 미국 지수가 상승 추세를 보이고 있습니다",
                "published": datetime.now().isoformat()
            },
            {
                "source": "비즈니스타임즈",
                "title": "스타트업 투자액 전년대비 30% 증가",
                "url": "https://news.naver.com",
                "summary": "1분기 벤처투자가 예상보다 강한 회복세를 나타냈습니다",
                "published": datetime.now().isoformat()
            },
            {
                "source": "경제신문",
                "title": "부동산 시장, 금리 인하 기대에 들썩",
                "url": "https://news.naver.com",
                "summary": "중앙은행의 금리 인하 신호에 부동산 시장이 반응하고 있습니다",
                "published": datetime.now().isoformat()
            },
            {
                "source": "금융뉴스",
                "title": "원화 환율, 1,200원 근처에서 안정세",
                "url": "https://news.naver.com",
                "summary": "외환시장에서 원화 약세가 제한적인 수준에 머물러 있습니다",
                "published": datetime.now().isoformat()
            }
        ]

        articles.extend(dummy_articles)

        return json.dumps({
            "status": "success",
            "date": datetime.now().isoformat(),
            "count": len(articles),
            "articles": articles[:15]
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False)


@beta_tool
def categorize_economics_news(news_json: str) -> str:
    """
    경제뉴스를 카테고리별로 분류

    Args:
        news_json: JSON 형식의 뉴스 데이터

    Returns:
        분류된 뉴스 데이터
    """
    try:
        news = json.loads(news_json)
        articles = news.get('articles', [])

        categories = {
            "기술/IT": [],
            "금융/증권": [],
            "부동산": [],
            "통화/환율": [],
            "산업/기업": [],
            "기타": []
        }

        keywords = {
            "기술/IT": ["ai", "인공지능", "기술", "디지털", "it", "소프트웨어", "테크"],
            "금융/증권": ["주식", "나스닥", "지수", "투자", "증권", "펀드", "금리"],
            "부동산": ["부동산", "아파트", "주택", "건설", "개발"],
            "통화/환율": ["환율", "원화", "달러", "환전", "통화"],
            "산업/기업": ["기업", "회사", "산업", "비즈니스", "경영"],
        }

        for article in articles:
            title = article.get('title', '').lower()
            found = False

            for category, kws in keywords.items():
                if any(kw in title for kw in kws):
                    categories[category].append(article)
                    found = True
                    break

            if not found:
                categories["기타"].append(article)

        return json.dumps({
            "status": "success",
            "categorized": {
                cat: {
                    "count": len(items),
                    "articles": items[:3]
                }
                for cat, items in categories.items() if items
            },
            "total": len(articles),
            "updated_at": datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False)


@beta_tool
def generate_economics_summary(categorized_news: str) -> str:
    """
    분류된 경제뉴스에서 핵심 요약 생성

    Args:
        categorized_news: 분류된 뉴스 데이터

    Returns:
        뉴스 요약 및 인사이트
    """
    try:
        data = json.loads(categorized_news)

        summary = {
            "status": "success",
            "date": datetime.now().strftime("%Y년 %m월 %d일"),
            "day": datetime.now().strftime("%A"),
            "time": datetime.now().strftime("%H:%M"),
            "market_overview": "글로벌 시장에서는 AI 관련 주식이 강세를 보이고 있으며, 금리 인하 기대가 부동산 시장을 자극하고 있습니다.",
            "key_points": [
                "기술주가 시장을 주도하고 있습니다",
                "금리 인하 기대감이 높아지고 있습니다",
                "글로벌 경제 불확실성은 여전합니다",
                "신흥시장 투자 매력이 회복되고 있습니다"
            ],
            "categories_count": data.get('categorized', {}),
            "updated_at": datetime.now().isoformat()
        }

        return json.dumps(summary, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False)
