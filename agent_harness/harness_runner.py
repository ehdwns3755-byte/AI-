"""
Agent Harness Runner — Comprehensive Entry Point

Integrates all three harness phases per official Claude documentation:
  https://platform.claude.com/docs/en/managed-agents/overview

Phase 1: Tool Runner   — automatic tool execution loop (local tools)
Phase 2: SDK Loop      — manual turn-by-turn loop (approval gates / logging)
Phase 3: Managed Agents — server-managed sessions (long-running, sandboxed)

Rubric validation is woven into the loop: the harness runs quality checks
after each major step and keeps iterating until the rubric score is 5.0/5.0
or the configured budget is exhausted.

Usage:
    python -m agent_harness.harness_runner [--phase 1|2|3|all] [--validate]

CLI examples:
    python -m agent_harness.harness_runner                  # full pipeline
    python -m agent_harness.harness_runner --phase 1        # Tool Runner only
    python -m agent_harness.harness_runner --validate       # rubric check only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from anthropic import Anthropic

from agent_harness.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    MAX_ITERATIONS,
    MAX_TOKENS,
    DEBUG,
)
from agent_harness.logger import get_logger
from agent_harness.performance import timer, ResponseBudget, all_stats
from agent_harness.validators.quality_validator import run_validation
from agent_harness.tools.trend_collector import (
    fetch_hacker_news_trends,
    fetch_arxiv_trends,
    fetch_reddit_trends,
    aggregate_trends,
    categorize_trends,
)

logger = get_logger(__name__)
client = Anthropic(api_key=ANTHROPIC_API_KEY)


# ── Rubric Validation Tool (used in Phase 1 loop) ─────────────────────────────

def validate_project_quality(project_dir: str = ".") -> str:
    """Run rubric validation and return JSON summary."""
    results = run_validation(project_dir)
    return json.dumps({
        "grade": results["grade"],
        "average": results["average"],
        "scores": {str(k): v for k, v in results["scores"].items()},
        "is_perfect": results["average"] >= 5.0,
    }, ensure_ascii=False)


HARNESS_TOOLS = [
    {
        "name": "fetch_hacker_news_trends",
        "description": "Fetch trending AI stories from Hacker News",
        "input_schema": {
            "type": "object",
            "properties": {"days": {"type": "integer", "description": "Days to look back"}},
            "required": ["days"],
        },
    },
    {
        "name": "fetch_arxiv_trends",
        "description": "Fetch recent AI/ML research papers from arXiv",
        "input_schema": {
            "type": "object",
            "properties": {"days": {"type": "integer"}},
            "required": ["days"],
        },
    },
    {
        "name": "fetch_reddit_trends",
        "description": "Fetch trending posts from Reddit ML community",
        "input_schema": {
            "type": "object",
            "properties": {
                "subreddit": {"type": "string"},
                "days": {"type": "integer"},
            },
            "required": ["subreddit", "days"],
        },
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
                }
            },
            "required": ["trends_data"],
        },
    },
    {
        "name": "categorize_trends",
        "description": "Categorize aggregated trends by AI topic",
        "input_schema": {
            "type": "object",
            "properties": {"trends_json": {"type": "string"}},
            "required": ["trends_json"],
        },
    },
    {
        "name": "validate_project_quality",
        "description": "Run rubric validation and return quality score",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_dir": {
                    "type": "string",
                    "description": "Project root directory (default '.')",
                }
            },
            "required": [],
        },
    },
]


def _dispatch_tool(name: str, tool_input: dict) -> str:
    """Route tool calls to their Python implementations."""
    try:
        match name:
            case "fetch_hacker_news_trends":
                return fetch_hacker_news_trends(days=tool_input.get("days", 7))
            case "fetch_arxiv_trends":
                return fetch_arxiv_trends(days=tool_input.get("days", 7))
            case "fetch_reddit_trends":
                return fetch_reddit_trends(
                    subreddit=tool_input.get("subreddit", "MachineLearning"),
                    days=tool_input.get("days", 7),
                )
            case "aggregate_trends":
                return aggregate_trends(tool_input.get("trends_data", []))
            case "categorize_trends":
                return categorize_trends(tool_input.get("trends_json", "{}"))
            case "validate_project_quality":
                return validate_project_quality(tool_input.get("project_dir", "."))
            case _:
                return json.dumps({"status": "error", "error": f"Unknown tool: {name}"})
    except Exception as exc:
        return json.dumps({"status": "error", "error": str(exc)})


# ── Phase 1: Tool Runner ──────────────────────────────────────────────────────

PHASE1_SYSTEM = """You are the AI Trends Harness Agent.

Your job: collect AI trends from all sources, aggregate them, categorize by topic,
then validate the project quality. Use tools in this order:
1. fetch_hacker_news_trends (days=7)
2. fetch_arxiv_trends (days=7)
3. fetch_reddit_trends (subreddit="MachineLearning", days=7)
4. aggregate_trends with all collected data
5. categorize_trends with aggregated data
6. validate_project_quality to confirm rubric score

Report final trends summary and quality grade."""


def run_phase1(budget: ResponseBudget) -> dict[str, Any]:
    """
    Phase 1: Tool Runner — automatic tool execution loop.
    Claude calls tools; the loop executes them and feeds results back.
    """
    logger.info("Phase 1: Tool Runner starting")
    messages: list[dict] = [
        {
            "role": "user",
            "content": (
                "Collect AI trends from all sources, aggregate, categorize, "
                "then validate project quality. Run the full pipeline."
            ),
        }
    ]

    turn = 0
    final_text = ""

    while turn < MAX_ITERATIONS:
        turn += 1
        logger.info(f"  Turn {turn}")

        with budget.track(f"phase1_turn{turn}"):
            resp = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                system=PHASE1_SYSTEM,
                tools=HARNESS_TOOLS,
                messages=messages,
            )

        if resp.stop_reason == "end_turn":
            for block in resp.content:
                if hasattr(block, "text"):
                    final_text = block.text
            logger.info("  Phase 1 complete (end_turn)")
            break

        if resp.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            results = []
            for block in resp.content:
                if block.type == "tool_use":
                    logger.info(f"    Tool: {block.name}")
                    with budget.track(f"tool:{block.name}"):
                        result = _dispatch_tool(block.name, block.input)
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": results})

    return {"phase": 1, "turns": turn, "output": final_text}


# ── Phase 2: SDK Loop (manual, with per-turn logging) ────────────────────────

def run_phase2(task: str, budget: ResponseBudget) -> dict[str, Any]:
    """
    Phase 2: Manual SDK loop — full control per turn.
    Use this when you need approval gates, custom logging, or conditional tools.
    """
    logger.info("Phase 2: SDK Loop starting")
    messages: list[dict] = [{"role": "user", "content": task}]
    turn = 0
    output = ""

    while turn < MAX_ITERATIONS:
        turn += 1
        logger.info(f"  SDK turn {turn}")

        with budget.track(f"phase2_turn{turn}"):
            resp = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                messages=messages,
            )

        # Per-turn hook: log stop reason (approval gate could go here)
        logger.info(f"    stop_reason={resp.stop_reason}, tokens={resp.usage.output_tokens}")

        for block in resp.content:
            if hasattr(block, "text"):
                output += block.text

        if resp.stop_reason == "end_turn":
            break

        messages.append({"role": "assistant", "content": resp.content})
        # No tools in Phase 2 — simple turn-by-turn conversation
        messages.append({"role": "user", "content": "Continue."})

    return {"phase": 2, "turns": turn, "output": output}


# ── Phase 3: Managed Agents ───────────────────────────────────────────────────

def run_phase3(project_dir: str = ".") -> dict[str, Any]:
    """
    Phase 3: Managed Agents — server-managed sessions.
    Delegates to managed_agents.run_agent_team() which orchestrates
    Code Auditor → Issue Resolution → Data Analytics agents in cloud sandboxes.
    """
    from agent_harness.managed_agents import run_agent_team
    logger.info("Phase 3: Managed Agents starting")
    result = run_agent_team(project_dir)
    return {"phase": 3, **result}


# ── Rubric validation loop ────────────────────────────────────────────────────

def run_rubric_loop(project_dir: str = ".", max_rounds: int = 3) -> dict[str, Any]:
    """
    Run rubric validation repeatedly until 5.0/5.0 or max_rounds exhausted.
    Between rounds, use Phase 1 Tool Runner to attempt fixes.
    """
    logger.info("Rubric validation loop starting")
    history: list[dict] = []

    for round_num in range(1, max_rounds + 1):
        logger.info(f"  Validation round {round_num}")
        results = run_validation(project_dir)
        history.append({
            "round": round_num,
            "grade": results["grade"],
            "average": results["average"],
        })
        logger.info(f"  → {results['grade']}  avg={results['average']}/5")

        if results["average"] >= 5.0:
            logger.info("  ✅ Perfect score achieved")
            break

        if round_num < max_rounds:
            logger.info("  Running Phase 1 to improve score...")
            budget = ResponseBudget(target_seconds=120.0)
            run_phase1(budget)

    return {
        "final_grade": results["grade"],
        "final_average": results["average"],
        "rounds": history,
        "perfect": results["average"] >= 5.0,
    }


# ── Full pipeline ─────────────────────────────────────────────────────────────

def run_full_pipeline(project_dir: str = ".") -> None:
    """
    Run all three phases in sequence, then validate.

    Pipeline:
        Phase 1: Trend collection + quality check (Tool Runner)
        Phase 2: Quick SDK loop verification
        Phase 3: Managed Agents deep analysis
        Rubric:  Validate until 5.0/5.0
    """
    print("\n" + "=" * 70)
    print("🚀 Agent Harness — Full Pipeline")
    print("=" * 70)

    budget = ResponseBudget(target_seconds=300.0)

    # Phase 1
    print("\n📍 Phase 1: Tool Runner")
    p1 = run_phase1(budget)
    print(f"   Turns: {p1['turns']}")

    # Phase 2 (quick verification pass)
    print("\n📍 Phase 2: SDK Loop (verification)")
    p2 = run_phase2(
        "Summarize the AI trends findings in 3 bullet points.",
        budget,
    )
    print(f"   Turns: {p2['turns']}")

    # Phase 3
    print("\n📍 Phase 3: Managed Agents")
    p3 = run_phase3(project_dir)
    print(f"   Iterations: {p3.get('iterations', '?')}")

    # Rubric validation
    print("\n📊 Rubric Validation Loop")
    rubric = run_rubric_loop(project_dir)
    print(f"   Final grade: {rubric['final_grade']}  ({rubric['final_average']}/5.0)")
    print(f"   Perfect:     {rubric['perfect']}")

    # Performance summary
    print("\n⏱  Performance Stats")
    for stat in sorted(all_stats(), key=lambda s: s["avg_ms"], reverse=True)[:5]:
        print(f"   {stat['label']:30} avg={stat['avg_ms']:6.0f}ms  calls={stat['calls']}")

    print("\n" + "=" * 70)
    print("✅  Pipeline complete")
    print("=" * 70 + "\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Agent Harness Runner — all phases + rubric validation"
    )
    p.add_argument(
        "--phase",
        choices=["1", "2", "3", "all"],
        default="all",
        help="Which phase to run (default: all)",
    )
    p.add_argument(
        "--validate",
        action="store_true",
        help="Run rubric validation only and exit",
    )
    p.add_argument(
        "--project-dir",
        default=".",
        help="Project root directory (default: current directory)",
    )
    return p


def main() -> int:
    args = _build_parser().parse_args()

    if args.validate:
        result = run_rubric_loop(args.project_dir)
        print(f"Grade: {result['final_grade']}  ({result['final_average']}/5.0)")
        return 0 if result["perfect"] else 1

    budget = ResponseBudget(target_seconds=300.0)

    if args.phase == "1":
        result = run_phase1(budget)
        print(result["output"])
    elif args.phase == "2":
        result = run_phase2("Analyse AI trends briefly.", budget)
        print(result["output"])
    elif args.phase == "3":
        run_phase3(args.project_dir)
    else:
        run_full_pipeline(args.project_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
