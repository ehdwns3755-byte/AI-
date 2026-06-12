"""Configuration for Agent Harness"""

import os
from dotenv import load_dotenv

load_dotenv()

# Claude API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-opus-4-8"

# Agent Configuration
AGENT_EFFORT = os.getenv("ANALYSIS_DEPTH", "high")
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

# Trends Configuration
TRENDS_SOURCES = os.getenv("TRENDS_SOURCES", "hacker-news,arxiv,reddit").split(",")
TRENDS_DAYS = int(os.getenv("TRENDS_DAYS", "7"))

# Logging
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
