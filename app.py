#!/usr/bin/env python3
"""Flask web server for AI Trends Dashboard"""

from flask import Flask, render_template_string
from ai_trends_dashboard import AITrendsDashboard
import os
import json
from datetime import datetime

app = Flask(__name__)
dashboard = AITrendsDashboard()

@app.route('/')
def index():
    """Serve the dashboard"""
    # Load cached data first for fast page load
    if os.path.exists(dashboard.data_file):
        try:
            with open(dashboard.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                dashboard.news_items = data.get('items', [])
        except Exception as e:
            print(f"Error loading data: {e}")

    # If no cached data, fetch new data
    if not dashboard.news_items:
        dashboard.run()
    else:
        dashboard.generate_html()

    # Serve the HTML
    if os.path.exists(dashboard.html_file):
        with open(dashboard.html_file, 'r', encoding='utf-8') as f:
            return f.read()

    return "<h1>Dashboard loading... Please refresh the page.</h1>"

@app.route('/refresh')
def refresh():
    """Refresh the dashboard data"""
    dashboard.news_items = []
    dashboard.run()

    with open(dashboard.html_file, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/data')
def api_data():
    """Return dashboard data as JSON"""
    if os.path.exists(dashboard.data_file):
        with open(dashboard.data_file, 'r', encoding='utf-8') as f:
            return f.read()

    return {'items': [], 'timestamp': datetime.now().isoformat()}

if __name__ == '__main__':
    print("Starting AI Trends Dashboard server on http://localhost:5000")
    app.run(debug=True, port=5000)
