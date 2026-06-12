"""Trend Collection Tools - @beta_tool decorated functions

Uses anthropic beta tool runner for automatic execution.
"""

import json
import feedparser
import requests
from datetime import datetime, timedelta
from typing import Any
from bs4 import BeautifulSoup

# Beta tool decorator (from Anthropic SDK)
# Note: This will be imported from anthropic.lib.beta in production
def beta_tool(func):
    """Decorator for beta tool registration - placeholder for anthropic SDK"""
    return func


@beta_tool
def fetch_hacker_news_trends(days: int = 7) -> str:
    """
    Fetch trending AI-related stories from Hacker News.

    Args:
        days: Number of days to look back (default: 7)

    Returns:
        JSON string with list of trending stories containing title, points, url
    """
    try:
        # Fetch Hacker News API
        response = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        )
        response.raise_for_status()
        story_ids = response.json()[:30]  # Top 30 stories

        trends = []
        cutoff_date = datetime.now() - timedelta(days=days)

        for story_id in story_ids:
            story_response = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                timeout=5
            )
            story = story_response.json()

            # Filter by keywords (AI, ML, LLM, etc.)
            title = story.get("title", "").lower()
            if any(kw in title for kw in ["ai", "llm", "ml", "neural", "language model", "gpt", "claude"]):
                trends.append({
                    "source": "hacker-news",
                    "title": story.get("title"),
                    "url": story.get("url"),
                    "points": story.get("score", 0),
                    "timestamp": datetime.fromtimestamp(story.get("time", 0)).isoformat()
                })

        return json.dumps({
            "status": "success",
            "source": "hacker-news",
            "count": len(trends),
            "trends": trends[:10]  # Top 10
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "source": "hacker-news",
            "error": str(e)
        })


@beta_tool
def fetch_arxiv_trends(days: int = 7) -> str:
    """
    Fetch recent AI/ML papers from arXiv.

    Args:
        days: Number of days to look back (default: 7)

    Returns:
        JSON string with list of papers
    """
    try:
        # arXiv RSS feed for AI/ML papers
        feed_url = "http://arxiv.org/rss/cs.AI"
        feed = feedparser.parse(feed_url)

        papers = []
        cutoff_date = datetime.now() - timedelta(days=days)

        for entry in feed.entries[:20]:
            pub_date = datetime(*entry.published_parsed[:6])

            if pub_date > cutoff_date:
                papers.append({
                    "source": "arxiv",
                    "title": entry.title,
                    "authors": ", ".join([author.name for author in entry.authors]),
                    "url": entry.id,
                    "published": entry.published,
                    "summary": entry.summary[:200] + "..."
                })

        return json.dumps({
            "status": "success",
            "source": "arxiv",
            "count": len(papers),
            "papers": papers[:10]
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "source": "arxiv",
            "error": str(e)
        })


@beta_tool
def fetch_reddit_trends(subreddit: str = "MachineLearning", days: int = 7) -> str:
    """
    Fetch trending posts from Reddit's ML community.

    Args:
        subreddit: Reddit subreddit to scrape (default: MachineLearning)
        days: Number of days to look back (default: 7)

    Returns:
        JSON string with list of trending posts
    """
    try:
        # Note: Reddit API requires authentication
        # Using public RSS feed as fallback
        feed_url = f"https://www.reddit.com/r/{subreddit}/hot.rss"
        feed = feedparser.parse(feed_url)

        posts = []

        for entry in feed.entries[:15]:
            posts.append({
                "source": "reddit",
                "subreddit": subreddit,
                "title": entry.title,
                "url": entry.link,
                "published": entry.published,
                "score": entry.get("score", "N/A")
            })

        return json.dumps({
            "status": "success",
            "source": "reddit",
            "subreddit": subreddit,
            "count": len(posts),
            "posts": posts[:10]
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "source": "reddit",
            "error": str(e)
        })


@beta_tool
def aggregate_trends(trends_data: list[str]) -> str:
    """
    Aggregate trends from multiple sources.

    Args:
        trends_data: List of JSON trend data from different sources

    Returns:
        Aggregated and deduplicated trends data
    """
    try:
        all_items = []

        for data_str in trends_data:
            data = json.loads(data_str)
            if data.get("status") == "success":
                if "trends" in data:
                    all_items.extend(data["trends"])
                elif "papers" in data:
                    all_items.extend(data["papers"])
                elif "posts" in data:
                    all_items.extend(data["posts"])

        # Deduplicate by title similarity (simple version)
        seen_titles = set()
        unique_items = []

        for item in all_items:
            title_lower = item.get("title", "").lower().strip()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_items.append(item)

        # Sort by source diversity
        return json.dumps({
            "status": "success",
            "total_items": len(unique_items),
            "items": unique_items[:25],  # Top 25 aggregated
            "aggregated_at": datetime.now().isoformat()
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Aggregation failed: {str(e)}"
        })


@beta_tool
def categorize_trends(trends_json: str) -> str:
    """
    Categorize aggregated trends by topic/theme.

    Args:
        trends_json: JSON string of aggregated trends

    Returns:
        Categorized trends with labels
    """
    try:
        trends = json.loads(trends_json)
        items = trends.get("items", [])

        categories = {
            "Large Language Models": [],
            "Computer Vision": [],
            "Reinforcement Learning": [],
            "Hardware & Infrastructure": [],
            "Applications & Products": [],
            "Research & Theory": [],
            "Other": []
        }

        keywords = {
            "Large Language Models": ["llm", "language model", "gpt", "claude", "transformer", "nlp", "chat"],
            "Computer Vision": ["vision", "image", "video", "detection", "segmentation", "ocr"],
            "Reinforcement Learning": ["rl", "reinforcement", "agent", "reward"],
            "Hardware & Infrastructure": ["gpu", "tpu", "hardware", "chip", "inference"],
            "Applications & Products": ["app", "product", "tool", "deployment", "api"],
        }

        for item in items:
            title = item.get("title", "").lower()
            found = False

            for category, kws in keywords.items():
                if any(kw in title for kw in kws):
                    categories[category].append(item)
                    found = True
                    break

            if not found:
                categories["Other"].append(item)

        return json.dumps({
            "status": "success",
            "categorized_trends": {
                cat: {"count": len(items), "items": items[:5]}
                for cat, items in categories.items() if items
            },
            "total": len(items),
            "categorized_at": datetime.now().isoformat()
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Categorization failed: {str(e)}"
        })
