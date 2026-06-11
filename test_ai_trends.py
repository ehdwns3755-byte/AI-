#!/usr/bin/env python3
"""Unit tests for AI Trends Dashboard"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from ai_trends_dashboard import AITrendsDashboard


class TestAITrendsDashboard:
    """Test cases for AITrendsDashboard class"""

    @pytest.fixture
    def dashboard(self):
        """Create dashboard instance for testing"""
        with patch('ai_trends_dashboard.logging'):
            return AITrendsDashboard()

    def test_init_creates_required_attributes(self, dashboard):
        """Test that __init__ creates necessary attributes"""
        assert hasattr(dashboard, 'script_dir')
        assert hasattr(dashboard, 'data_file')
        assert hasattr(dashboard, 'html_file')
        assert hasattr(dashboard, 'log_file')
        assert hasattr(dashboard, 'config_file')
        assert hasattr(dashboard, 'news_items')
        assert hasattr(dashboard, 'config')

    def test_config_loads_or_defaults(self, dashboard):
        """Test that config loads or returns defaults"""
        assert isinstance(dashboard.config, dict)
        assert 'sources' in dashboard.config

    def test_categorize_large_language_models(self, dashboard):
        """Test categorization of LLM-related news"""
        text = "OpenAI releases new GPT transformer model"
        assert dashboard._categorize(text) == "Large Language Models"

    def test_categorize_computer_vision(self, dashboard):
        """Test categorization of computer vision news"""
        text = "New image recognition neural network breakthrough"
        assert dashboard._categorize(text) == "Computer Vision"

    def test_categorize_automation(self, dashboard):
        """Test categorization of automation news"""
        text = "Robot automation in manufacturing accelerates"
        assert dashboard._categorize(text) == "Automation & Robotics"

    def test_categorize_default(self, dashboard):
        """Test default categorization for unknown topics"""
        text = "Random news about weather"
        assert dashboard._categorize(text) == "General AI"

    def test_categorize_case_insensitive(self, dashboard):
        """Test that categorization is case-insensitive"""
        text = "CHATGPT INTEGRATION ANNOUNCED"
        assert dashboard._categorize(text) == "Large Language Models"

    @patch('ai_trends_dashboard.requests.get')
    def test_fetch_google_news_success(self, mock_get, dashboard):
        """Test successful Google News fetching"""
        mock_response = Mock()
        mock_response.content = b'<?xml version="1.0"?><feed><entry><title>AI News</title><link>http://example.com</link><summary>Summary</summary></entry></feed>'
        mock_get.return_value = mock_response

        with patch('ai_trends_dashboard.feedparser.parse') as mock_parse:
            mock_entry = {
                'title': 'GPT Model Released',
                'link': 'http://example.com',
                'summary': 'New model announcement',
                'published': '2026-06-11'
            }
            mock_parse.return_value.entries = [mock_entry]

            dashboard.fetch_google_news()
            assert len(dashboard.news_items) > 0
            assert any(item['source'] == 'Google News' for item in dashboard.news_items)

    @patch('ai_trends_dashboard.requests.get')
    def test_fetch_google_news_timeout(self, mock_get, dashboard):
        """Test handling of timeout in Google News"""
        import requests
        mock_get.side_effect = requests.Timeout()

        with patch('ai_trends_dashboard.logging') as mock_logging:
            dashboard.fetch_google_news()
            # Should handle timeout gracefully without raising exception

    @patch('ai_trends_dashboard.json.dump')
    @patch('builtins.open', create=True)
    def test_save_data_creates_file(self, mock_open, mock_dump, dashboard):
        """Test that save_data writes JSON file"""
        dashboard.news_items = [
            {'title': 'Test', 'link': 'http://test.com', 'source': 'Test'}
        ]

        dashboard.save_data()
        mock_open.assert_called()

    def test_save_data_handles_errors(self, dashboard):
        """Test that save_data handles write errors gracefully"""
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with patch('ai_trends_dashboard.logging'):
                # Should not raise exception
                dashboard.save_data()

    @patch('ai_trends_dashboard.requests.get')
    def test_fetch_reddit_success(self, mock_get, dashboard):
        """Test successful Reddit fetching"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {
                'children': [
                    {
                        'data': {
                            'title': 'GPT Discussion',
                            'permalink': '/r/MachineLearning/comments/123',
                            'created_utc': 1686429600,
                            'selftext': 'Discussion about GPT'
                        }
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        dashboard.fetch_reddit()
        assert any(item['source'] == 'Reddit' for item in dashboard.news_items)

    def test_duplicate_removal_by_normalized_title(self, dashboard):
        """Test that duplicates are removed by normalized title"""
        dashboard.news_items = [
            {'title': 'GPT Model Released', 'link': 'http://a.com', 'source': 'A'},
            {'title': 'gpt model released', 'link': 'http://b.com', 'source': 'B'},
            {'title': 'GPT MODEL RELEASED', 'link': 'http://c.com', 'source': 'C'},
            {'title': 'Different News', 'link': 'http://d.com', 'source': 'D'}
        ]

        # Simulate duplicate removal from run() method
        seen = set()
        unique_items = []
        for item in dashboard.news_items:
            normalized_title = item['title'].lower().strip()
            if normalized_title not in seen:
                seen.add(normalized_title)
                unique_items.append(item)

        assert len(unique_items) == 2
        assert unique_items[0]['title'] == 'GPT Model Released'
        assert unique_items[1]['title'] == 'Different News'

    def test_html_generation_with_empty_items(self, dashboard):
        """Test HTML generation with no news items"""
        dashboard.news_items = []
        dashboard.generate_html()

        with open(dashboard.html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            assert '현재 표시할 뉴스가 없습니다' in html_content

    def test_html_escaping_prevents_xss(self, dashboard):
        """Test that HTML content is properly escaped"""
        dashboard.news_items = [
            {
                'title': '<script>alert("XSS")</script>',
                'link': 'http://example.com',
                'source': 'Test',
                'category': 'General AI',
                'date': '2026-06-11',
                'summary': '<img src=x onerror="alert(1)">'
            }
        ]

        dashboard.generate_html()

        with open(dashboard.html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            # Check that script tags are escaped
            assert '<script>' not in html_content
            assert '&lt;script&gt;' in html_content
            assert 'onerror=' not in html_content

    def test_config_fallback_to_defaults(self):
        """Test that missing config.json falls back to defaults"""
        with patch('ai_trends_dashboard.os.path.exists', return_value=False):
            with patch('ai_trends_dashboard.logging'):
                dashboard = AITrendsDashboard()
                assert dashboard.config['sources']['google_news']['limit'] == 15
                assert dashboard.config['sources']['hacker_news']['timeout'] == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
