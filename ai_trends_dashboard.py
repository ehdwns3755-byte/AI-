#!/usr/bin/env python3
"""AI Trends Daily Dashboard Generator"""

import requests
import feedparser
import json
import os
import logging
from datetime import datetime
from html import escape
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

class AITrendsDashboard:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        if load_dotenv:
            env_file = os.path.join(self.script_dir, '.env')
            load_dotenv(env_file)

        self.data_dir = os.getenv('DATA_DIR', self.script_dir)
        self.log_dir = os.getenv('LOG_DIR', self.script_dir)

        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

        self.data_file = os.path.join(self.data_dir, 'ai_trends_data.json')
        self.html_file = os.path.join(self.data_dir, 'ai_dashboard.html')
        self.log_file = os.path.join(self.log_dir, 'ai_trends.log')
        self.config_file = os.path.join(self.script_dir, 'config.json')
        self.news_items = []
        self.config = self._load_config()
        self._setup_logging()

    def _load_config(self):
        """Load configuration from config.json"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config.json: {e}. Using defaults.")

        return {
            'sources': {
                'google_news_ko': {'limit': 15, 'timeout': 10},
                'naver_news': {'limit': 15, 'timeout': 10},
                'daumnet_news': {'limit': 10, 'timeout': 10},
                'hacker_news': {'limit': 10, 'timeout': 10, 'max_workers': 5}
            }
        }

    def _setup_logging(self):
        """Configure logging to both file and console"""
        log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def fetch_google_news_ko(self):
        """Fetch AI news from Google News Korea"""
        try:
            config = self.config.get('sources', {}).get('google_news_ko', {})
            url = config.get('url', 'https://news.google.com/rss/search?q=인공지능+OR+AI+OR+머신러닝+OR+LLM+OR+챗봇+OR+딥러닝&hl=ko&gl=KR&ceid=KR:ko')
            limit = config.get('limit', 15)
            timeout = config.get('timeout', 10)

            response = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            response.encoding = 'utf-8'
            feed = feedparser.parse(response.content)

            if not feed.entries:
                logging.warning("No entries found in Google News Korea feed")
                return

            for entry in feed.entries[:limit]:
                self.news_items.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'source': 'Google News 한국',
                    'category': self._categorize(entry.get('title', '')),
                    'date': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200]
                })
        except requests.Timeout:
            logging.error("Timeout while fetching Google News Korea")
        except requests.RequestException as e:
            logging.error(f"Network error fetching Google News Korea: {e}")
        except Exception as e:
            logging.error(f"Unexpected error fetching Google News Korea: {e}")

    def fetch_hacker_news(self):
        """Fetch AI-related stories from Hacker News using official API with parallel requests"""
        try:
            config = self.config.get('sources', {}).get('hacker_news', {})
            url_ids = config.get('url_ids', 'https://hacker-news.firebaseio.com/v0/topstories.json')
            url_item = config.get('url_item', 'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
            limit = config.get('limit', 10)
            timeout = config.get('timeout', 10)
            max_workers = config.get('max_workers', 5)

            response = requests.get(url_ids, timeout=timeout)
            response.raise_for_status()
            story_ids = response.json()[:30]

            if not story_ids:
                logging.warning("No stories found in Hacker News API")
                return

            def fetch_story(story_id):
                """Fetch individual story data"""
                try:
                    story_url = url_item.format(story_id=story_id)
                    story_response = requests.get(story_url, timeout=timeout)
                    story_response.raise_for_status()
                    return story_response.json()
                except Exception:
                    return None

            hn_count = len([x for x in self.news_items if x['source'] == 'Hacker News'])

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(fetch_story, sid): sid for sid in story_ids}

                for future in as_completed(futures):
                    if hn_count >= limit:
                        break

                    story = future.result()
                    if not story:
                        continue

                    title = story.get('title', '')
                    if any(keyword in title.lower() for keyword in ['ai', 'ml', 'llm', 'neural', 'gpt', 'claude']):
                        story_link = story.get('url', f"https://news.ycombinator.com/item?id={futures[future]}")
                        story_date = datetime.fromtimestamp(story.get('time', 0)).strftime('%Y-%m-%d')
                        self.news_items.append({
                            'title': title,
                            'link': story_link,
                            'source': 'Hacker News',
                            'category': self._categorize(title),
                            'date': story_date,
                            'summary': ''
                        })
                        hn_count += 1
        except requests.Timeout:
            logging.error("Timeout while fetching Hacker News")
        except requests.RequestException as e:
            logging.error(f"Network error fetching Hacker News: {e}")
        except Exception as e:
            logging.error(f"Unexpected error fetching Hacker News: {e}")

    def fetch_naver_news(self):
        """Fetch AI news from Naver Tech"""
        try:
            config = self.config.get('sources', {}).get('naver_news', {})
            # Naver Tech news feed
            url = config.get('url', 'https://rss.naver.com/news/today/it.xml')
            limit = config.get('limit', 15)
            timeout = config.get('timeout', 10)

            response = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            response.raise_for_status()
            response.encoding = 'utf-8'
            feed = feedparser.parse(response.content)

            if not feed.entries:
                logging.warning("No entries found in Naver News feed")
                return

            for entry in feed.entries[:limit]:
                title = entry.get('title', '')
                # More flexible filtering for Korean AI news
                if any(keyword in title for keyword in ['AI', '인공지능', '머신러닝', 'LLM', '자동화', '로봇', '딥러닝', '챗봇', 'GPT', '클로드']):
                    self.news_items.append({
                        'title': title,
                        'link': entry.get('link', ''),
                        'source': '네이버 뉴스',
                        'category': self._categorize(title),
                        'date': entry.get('published', ''),
                        'summary': entry.get('summary', '')[:200]
                    })
        except requests.Timeout:
            logging.error("Timeout while fetching Naver News")
        except requests.RequestException as e:
            logging.error(f"Network error fetching Naver News: {e}")
        except Exception as e:
            logging.error(f"Unexpected error fetching Naver News: {e}")

    def fetch_daumnet_news(self):
        """Fetch AI news from Daum News IT"""
        try:
            config = self.config.get('sources', {}).get('daumnet_news', {})
            url = config.get('url', 'https://rss.daum.net/rss/breakingnews/it.xml')
            limit = config.get('limit', 10)
            timeout = config.get('timeout', 10)

            response = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            response.raise_for_status()
            response.encoding = 'utf-8'
            feed = feedparser.parse(response.content)

            if not feed.entries:
                logging.warning("No entries found in Daum News feed")
                return

            for entry in feed.entries[:limit]:
                title = entry.get('title', '')
                # More flexible filtering for Korean AI news
                if any(keyword in title for keyword in ['AI', '인공지능', '머신러닝', 'LLM', '자동화', '로봇', '딥러닝', '챗봇', 'GPT', '클로드']):
                    self.news_items.append({
                        'title': title,
                        'link': entry.get('link', ''),
                        'source': '다음 뉴스',
                        'category': self._categorize(title),
                        'date': entry.get('published', ''),
                        'summary': entry.get('summary', '')[:200]
                    })
        except requests.Timeout:
            logging.error("Timeout while fetching Daum News")
        except requests.RequestException as e:
            logging.error(f"Network error fetching Daum News: {e}")
        except Exception as e:
            logging.error(f"Unexpected error fetching Daum News: {e}")

    def _categorize(self, text):
        """Categorize news based on keywords from config"""
        text = text.lower()
        categories = self.config.get('categories', {})

        for category, keywords in categories.items():
            if any(word in text for word in keywords):
                return category

        return 'General AI'

    def _backup_data(self):
        """Create backup of current data for fallback"""
        try:
            if os.path.exists(self.data_file):
                backup_file = self.data_file + '.backup'
                with open(self.data_file, 'r', encoding='utf-8') as src:
                    backup_data = src.read()
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(backup_data)
                logging.debug(f"Backup created: {backup_file}")
        except Exception as e:
            logging.warning(f"Failed to create backup: {e}")

    def _load_cached_data(self):
        """Load cached data when current fetch fails"""
        try:
            backup_file = self.data_file + '.backup'
            if os.path.exists(backup_file):
                with open(backup_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    logging.warning(f"Loaded cached data with {len(cached_data.get('items', []))} items")
                    return cached_data
        except Exception as e:
            logging.warning(f"Failed to load cached data: {e}")

        return {'items': [], 'timestamp': datetime.now().isoformat()}

    def save_data(self):
        """Save collected data to JSON"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'items': self.news_items
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Data saved: {len(self.news_items)} items")
            self._backup_data()
        except Exception as e:
            logging.error(f"Error saving data: {e}")

    def generate_html(self):
        """Generate HTML dashboard"""
        categories = {}
        for item in self.news_items:
            cat = item['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="3600">
    <title>AI 동향 대시보드</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --accent-blue: #3b82f6;
            --accent-purple: #a855f7;
            --accent-green: #10b981;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 2px solid var(--accent-blue);
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .timestamp {{
            color: var(--text-secondary);
            font-size: 0.95em;
        }}

        .category-section {{
            margin-bottom: 40px;
        }}

        .category-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--accent-purple);
            color: var(--accent-purple);
        }}

        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}

        .news-card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
        }}

        .news-card:hover {{
            transform: translateY(-5px);
            border-color: var(--accent-blue);
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
        }}

        .news-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}

        .news-source {{
            background: var(--accent-blue);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 600;
            white-space: nowrap;
        }}

        .news-date {{
            color: var(--text-secondary);
            font-size: 0.85em;
        }}

        .news-title {{
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 10px;
            line-height: 1.4;
        }}

        .news-title a {{
            color: var(--text-primary);
            text-decoration: none;
            transition: color 0.3s ease;
        }}

        .news-title a:hover {{
            color: var(--accent-blue);
        }}

        .news-summary {{
            color: var(--text-secondary);
            font-size: 0.9em;
            margin-bottom: 15px;
            flex-grow: 1;
        }}

        .news-link {{
            display: inline-block;
            color: var(--accent-blue);
            text-decoration: none;
            font-size: 0.9em;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .news-link:hover {{
            color: var(--accent-purple);
        }}

        .empty-state {{
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
        }}

        footer {{
            text-align: center;
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-secondary);
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 1.8em;
            }}

            .news-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI 동향 대시보드</h1>
            <p class="timestamp">마지막 업데이트: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
        </header>

        <main>
"""

        if not self.news_items:
            html_content += """
            <div class="empty-state">
                <p>현재 표시할 뉴스가 없습니다. 나중에 다시 시도해주세요.</p>
            </div>
"""
        else:
            for category in sorted(categories.keys()):
                items = categories[category]
                html_content += f"""
        <section class="category-section">
            <h2 class="category-title">{category}</h2>
            <div class="news-grid">
"""
                for item in items[:6]:
                    escaped_title = escape(item['title'])
                    escaped_summary = escape(item['summary']) if item['summary'] else ''
                    escaped_link = escape(item['link'])
                    escaped_source = escape(item['source'])
                    escaped_date = escape(item['date'])
                    html_content += f"""
                <div class="news-card">
                    <div class="news-card-header">
                        <span class="news-source">{escaped_source}</span>
                        <span class="news-date">{escaped_date}</span>
                    </div>
                    <h3 class="news-title">
                        <a href="{escaped_link}" target="_blank" rel="noopener noreferrer">
                            {escaped_title}
                        </a>
                    </h3>
                    {f'<p class="news-summary">{escaped_summary}</p>' if escaped_summary else ''}
                    <a href="{escaped_link}" class="news-link" target="_blank" rel="noopener noreferrer">
                        전체 보기 →
                    </a>
                </div>
"""
                html_content += """
            </div>
        </section>
"""

        html_content += """
        </main>

        <footer>
            <p>자동으로 매일 오전 8시에 업데이트됩니다.</p>
            <p style="margin-top: 10px; opacity: 0.7;">
                이 대시보드는 여러 뉴스 소스에서 AI 관련 기사를 수집합니다.
            </p>
        </footer>
    </div>
</body>
</html>
"""

        try:
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logging.info(f"HTML dashboard generated: {self.html_file}")
        except Exception as e:
            logging.error(f"Error generating HTML: {e}")

    def run(self):
        """Main execution"""
        logging.info("=" * 50)
        logging.info("Starting AI news collection (Korean)")
        logging.info("=" * 50)

        self.fetch_google_news_ko()
        google_count = len([x for x in self.news_items if x['source'] == 'Google News 한국'])
        logging.info(f"Google News Korea: {google_count} items")

        self.fetch_naver_news()
        naver_count = len([x for x in self.news_items if x['source'] == '네이버 뉴스'])
        logging.info(f"Naver News: {naver_count} items")

        self.fetch_daumnet_news()
        daum_count = len([x for x in self.news_items if x['source'] == '다음 뉴스'])
        logging.info(f"Daum News: {daum_count} items")

        self.fetch_hacker_news()
        hn_count = len([x for x in self.news_items if x['source'] == 'Hacker News'])
        logging.info(f"Hacker News: {hn_count} items")

        if not self.news_items:
            logging.warning("No news items collected. Trying to load cached data...")
            cached_data = self._load_cached_data()
            self.news_items = cached_data.get('items', [])

            if not self.news_items:
                logging.warning("No cached data available. Check network connection and API status.")
                return

        # Remove duplicates by normalized title
        seen = set()
        unique_items = []
        for item in self.news_items:
            normalized_title = item['title'].lower().strip()
            if normalized_title not in seen:
                seen.add(normalized_title)
                unique_items.append(item)

        duplicates_removed = len(self.news_items) - len(unique_items)
        self.news_items = unique_items
        logging.info(f"Removed {duplicates_removed} duplicates. Total items: {len(self.news_items)}")

        self.save_data()
        self.generate_html()

        # Open in default browser (optional)
        try:
            import webbrowser
            webbrowser.open(f'file:///{self.html_file.replace(chr(92), "/")}')
            logging.info("Opened dashboard in default browser")
        except Exception as e:
            logging.debug(f"Failed to open browser: {e}")

        logging.info("Collection and dashboard generation completed successfully")
        logging.info("=" * 50)

if __name__ == '__main__':
    dashboard = AITrendsDashboard()
    dashboard.run()
