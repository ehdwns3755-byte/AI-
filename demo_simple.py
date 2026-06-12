#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Agent Harness Demo - 실행 결과 보기
"""

import json
from agent_harness.tools.trend_collector import (
    fetch_hacker_news_trends,
    fetch_arxiv_trends,
    fetch_reddit_trends,
)

print("=" * 70)
print("AI Trends Dashboard - Agent Harness Execution Demo")
print("=" * 70)

print("\n[User Input]")
print('>>> "Please analyze the latest AI trends"')

print("\n[Claude Agent Thinking]")
print('Claude: "I need to collect trends from multiple sources..."')
print('Claude: "Let me execute my available tools in sequence:"')

# Step 1: Hacker News
print("\n" + "-" * 70)
print("[STEP 1] Executing: fetch_hacker_news_trends()")
print("-" * 70)

result1 = fetch_hacker_news_trends(days=7)
data1 = json.loads(result1)

print("Status: SUCCESS")
print("Items collected: " + str(data1['count']))
print("\nTop 3 trending stories:")
for i, item in enumerate(data1['trends'][:3], 1):
    print("[" + str(i) + "] " + item['title'])
    print("    Points: " + str(item['points']))
    print("")

# Step 2: arXiv
print("-" * 70)
print("[STEP 2] Executing: fetch_arxiv_trends()")
print("-" * 70)

result2 = fetch_arxiv_trends(days=7)
data2 = json.loads(result2)

print("Status: SUCCESS")
print("Papers collected: " + str(data2['count']))
if data2.get('papers'):
    print("\nSample papers:")
    for i, item in enumerate(data2['papers'][:2], 1):
        print("[" + str(i) + "] " + item['title'])
        print("    Authors: " + item['authors'][:40] + "...")
        print("")

# Step 3: Reddit
print("-" * 70)
print("[STEP 3] Executing: fetch_reddit_trends()")
print("-" * 70)

result3 = fetch_reddit_trends(subreddit="MachineLearning", days=7)
data3 = json.loads(result3)

print("Status: SUCCESS")
print("Discussions collected: " + str(data3['count']))
print("\nTop community discussions:")
for i, item in enumerate(data3['posts'][:3], 1):
    print("[" + str(i) + "] " + item['title'])
    print("    Community: r/" + item['subreddit'])
    print("")

# Final Summary
print("=" * 70)
print("[EXECUTION SUMMARY]")
print("=" * 70)

print("\nAgent Loop Execution:")
print("  Step 1: Hacker News trends - " + str(data1['count']) + " items")
print("  Step 2: arXiv papers - " + str(data2['count']) + " items")
print("  Step 3: Reddit discussions - " + str(data3['count']) + " items")

total_items = data1['count'] + data2['count'] + data3['count']
print("\n  TOTAL: " + str(total_items) + " items collected")

print("\n" + "=" * 70)
print("[WHAT HAPPENED]")
print("=" * 70)

print("""
1. Agent received your request
2. Agent decided which tools to use (AUTOMATICALLY)
3. Tools were executed in sequence:
   - fetch_hacker_news_trends
   - fetch_arxiv_trends
   - fetch_reddit_trends
4. Results were aggregated
5. Agent would then categorize and create a report

THIS IS THE AGENT HARNESS IN ACTION!

Key Points:
- All tools executed WITHOUT manual intervention
- Agent made decisions automatically
- Results were combined together
- This is what Claude + Tools do

Next step: With real Claude API, it would also:
- Automatically call aggregate_trends()
- Automatically call categorize_trends()
- Generate a professional dashboard report
""")

print("=" * 70)
print("Demo Complete!")
print("=" * 70 + "\n")
