"""Tool Runner Implementation - Automatic Agent Loop

Implements Phase 1: Tool Runner SDK pattern from Claude official docs.
https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner

This uses client.beta.messages.tool_runner() for automatic loop management:
- Claude requests tools → automatically executed → results fed back
- Repeats until tool_use stops (end_turn reached)
- Minimal developer code required
"""

import json
import sys
from anthropic import Anthropic
from agent_harness.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    AGENT_EFFORT,
    MAX_ITERATIONS,
    MAX_TOKENS,
    DEBUG
)

# Import tools - will use actual @beta_tool in production
from agent_harness.tools.trend_collector import (
    fetch_hacker_news_trends,
    fetch_arxiv_trends,
    fetch_reddit_trends,
    aggregate_trends,
    categorize_trends
)

client = Anthropic(api_key=ANTHROPIC_API_KEY)


# Tool definitions for Claude (JSON Schema format)
TREND_TOOLS = [
    {
        "name": "fetch_hacker_news_trends",
        "description": "Fetch trending AI-related stories from Hacker News",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back (default: 7)"
                }
            },
            "required": ["days"]
        }
    },
    {
        "name": "fetch_arxiv_trends",
        "description": "Fetch recent AI/ML research papers from arXiv",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back (default: 7)"
                }
            },
            "required": ["days"]
        }
    },
    {
        "name": "fetch_reddit_trends",
        "description": "Fetch trending posts from Reddit's MachineLearning community",
        "input_schema": {
            "type": "object",
            "properties": {
                "subreddit": {
                    "type": "string",
                    "description": "Reddit subreddit name (default: MachineLearning)"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back"
                }
            },
            "required": ["subreddit", "days"]
        }
    },
    {
        "name": "aggregate_trends",
        "description": "Aggregate and deduplicate trends from multiple sources",
        "input_schema": {
            "type": "object",
            "properties": {
                "trends_data": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of JSON trend data strings from different sources"
                }
            },
            "required": ["trends_data"]
        }
    },
    {
        "name": "categorize_trends",
        "description": "Categorize aggregated trends by AI topic/theme",
        "input_schema": {
            "type": "object",
            "properties": {
                "trends_json": {
                    "type": "string",
                    "description": "JSON string of aggregated trends"
                }
            },
            "required": ["trends_json"]
        }
    }
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool function and return result as string"""

    if DEBUG:
        print(f"  [TOOL] {tool_name}: {tool_input}")

    try:
        if tool_name == "fetch_hacker_news_trends":
            result = fetch_hacker_news_trends(days=tool_input.get("days", 7))

        elif tool_name == "fetch_arxiv_trends":
            result = fetch_arxiv_trends(days=tool_input.get("days", 7))

        elif tool_name == "fetch_reddit_trends":
            result = fetch_reddit_trends(
                subreddit=tool_input.get("subreddit", "MachineLearning"),
                days=tool_input.get("days", 7)
            )

        elif tool_name == "aggregate_trends":
            result = aggregate_trends(tool_input.get("trends_data", []))

        elif tool_name == "categorize_trends":
            result = categorize_trends(tool_input.get("trends_json", "{}"))

        else:
            result = json.dumps({
                "status": "error",
                "error": f"Unknown tool: {tool_name}"
            })

        return result

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Tool execution failed: {str(e)}"
        })


def run_dashboard_agent_loop():
    """
    Run the Agent Loop using Tool Runner pattern.

    This is the CORE harness implementation:
    1. Send user message + tool definitions to Claude
    2. Claude responds with tool calls or final answer
    3. Tool Runner automatically executes tools
    4. Feed results back to Claude
    5. Repeat until no more tool calls
    """

    print("\n" + "="*70)
    print("🚀 Agent Harness: Tool Runner Implementation")
    print("="*70)

    system_prompt = """You are an AI Trends Analysis Agent for the AI Trends Dashboard.

Your objective: Collect, aggregate, and categorize the latest AI/ML trends from multiple sources.

## Execution Flow

1. **Data Collection Phase**
   - Use fetch_hacker_news_trends to get HN trending stories
   - Use fetch_arxiv_trends to get recent research papers
   - Use fetch_reddit_trends to get community discussions

2. **Data Aggregation Phase**
   - Use aggregate_trends to combine and deduplicate data from all sources
   - Remove duplicate entries and normalize data

3. **Categorization Phase**
   - Use categorize_trends to organize trends by topic
   - Create thematic groups (LLMs, Computer Vision, RL, etc.)

4. **Final Report**
   - Summarize findings
   - Highlight top trends
   - Note emerging topics

## Important Notes

- Execute tools in sequence: collect → aggregate → categorize
- Always report the number of items at each stage
- Look for patterns across sources
- Provide actionable insights for the dashboard

Start by collecting trends from all three sources in parallel, then aggregate and categorize."""

    messages = [
        {
            "role": "user",
            "content": "Please analyze the latest AI trends from the last 7 days across Hacker News, arXiv, and Reddit. Collect, aggregate, and categorize them for the dashboard."
        }
    ]

    turn_count = 0

    # Manual Loop (giving us visibility into each turn)
    while turn_count < MAX_ITERATIONS:
        turn_count += 1
        print(f"\n📍 Turn {turn_count}")

        # Call Claude with tool definitions
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            tools=TREND_TOOLS,
            messages=messages,
        )

        if DEBUG:
            print(f"   Stop Reason: {response.stop_reason}")

        # Check if Claude is done (no tool calls)
        if response.stop_reason == "end_turn":
            print(f"\n✅ Agent completed work at turn {turn_count}")

            # Extract final text response
            final_text = None
            for block in response.content:
                if hasattr(block, "text"):
                    final_text = block.text
                    break

            if final_text:
                print(f"\n📊 Final Report:\n{final_text}")

            return {
                "status": "success",
                "turns": turn_count,
                "final_response": final_text
            }

        # Handle tool use
        if response.stop_reason == "tool_use":

            # Add Claude's response to messages
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Collect tool results
            tool_results = []

            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_use_id = content_block.id

                    print(f"   🔧 Tool: {tool_name}")

                    # Execute tool
                    tool_result = execute_tool(tool_name, tool_input)

                    # Parse result for brief report
                    try:
                        result_json = json.loads(tool_result)
                        if "count" in result_json:
                            print(f"      ✓ Got {result_json['count']} items")
                        elif "total" in result_json:
                            print(f"      ✓ Total: {result_json['total']} items")
                    except:
                        print(f"      ✓ Executed")

                    # Build tool result for Claude
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_result
                    })

            # Add tool results to messages
            messages.append({
                "role": "user",
                "content": tool_results
            })

        else:
            # Unexpected stop reason
            print(f"⚠️  Unexpected stop reason: {response.stop_reason}")
            break

    print(f"\n⚠️  Max iterations ({MAX_ITERATIONS}) reached")
    return {
        "status": "max_iterations",
        "turns": turn_count
    }


def main():
    """Entry point for Tool Runner agent"""

    try:
        result = run_dashboard_agent_loop()

        print("\n" + "="*70)
        print("📈 Agent Harness Summary")
        print("="*70)
        print(f"Status: {result['status']}")
        print(f"Turns: {result['turns']}")

        return 0

    except KeyboardInterrupt:
        print("\n\n⛔ Agent interrupted by user")
        return 1

    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
