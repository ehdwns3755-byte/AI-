"""
Managed Agents - Phase 3: Multi-agent Coordinator

Official docs: https://platform.claude.com/docs/en/managed-agents/overview
Beta header: managed-agents-2026-04-01 (SDK sets this automatically)

Three specialized agents work in sequence:
  1. Code Auditor Agent     -- discovers code issues → ISSUES.md
  2. Issue Resolution Agent -- fixes issues → git commits
  3. Data Analytics Agent   -- collects trends → dashboard report

Agents are persistent (create once, reuse by ID).
Environment is a reusable cloud sandbox.
Sessions are ephemeral (one per task execution).
"""

import json
import sys
from pathlib import Path
from anthropic import Anthropic
from agent_harness.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, DEBUG

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Persisted registry: agent IDs + environment ID (create once, reuse)
REGISTRY_FILE = Path(__file__).parent / "agent_registry.json"

AGENT_DEFINITIONS = {
    "code_auditor": {
        "name": "Code Auditor Agent",
        "system": (
            "You are a Code Auditor Agent specialized in static code analysis.\n\n"
            "Your role:\n"
            "- Analyze code for bugs, security vulnerabilities, and quality issues\n"
            "- Priority order: 🔴 High (security/runtime) → 🟡 Medium (functional) → 🟢 Low (UX/a11y)\n"
            "- Write discovered issues to ISSUES.md in structured format\n"
            "- Avoid false positives: verify context before flagging patterns\n\n"
            "Output format per issue:\n"
            "## Issue Title\n"
            "**Priority:** 🔴/🟡/🟢\n"
            "**File:** path/to/file:line\n"
            "**Problem:** description\n"
            "**Solution:** suggested fix\n\n"
            "Be precise. Report only real issues with clear evidence."
        ),
        "tools": [{"type": "agent_toolset_20260401"}],
    },
    "issue_resolution": {
        "name": "Issue Resolution Agent",
        "system": (
            "You are an Issue Resolution Agent that automatically fixes code issues.\n\n"
            "Your role:\n"
            "- Read ISSUES.md and fix issues in priority order (🔴 → 🟡 → 🟢)\n"
            "- Implement fixes using file operations and bash tools\n"
            "- Create atomic git commits per fix: `fix: description`\n"
            "- Mark each resolved issue in ISSUES.md with ✅\n\n"
            "Commit format:\n"
            "fix: Resolve N issues\n\n"
            "- fix: description 1\n"
            "- fix: description 2\n\n"
            "Co-Authored-By: Claude Agent Team <noreply@anthropic.com>\n\n"
            "Test changes where possible and verify no regressions."
        ),
        "tools": [{"type": "agent_toolset_20260401"}],
    },
    "data_analytics": {
        "name": "Data Analytics Agent",
        "system": (
            "You are a Data Analytics Agent for the AI Trends Dashboard.\n\n"
            "Your role:\n"
            "- Collect AI/ML trends from Hacker News, arXiv, and Reddit\n"
            "- Aggregate and deduplicate trend data\n"
            "- Categorize by topic (LLMs, Computer Vision, RL, etc.)\n"
            "- Generate a structured report saved as trends_report.md\n\n"
            "Execution sequence:\n"
            "1. Fetch from each source (use web search / web fetch tools)\n"
            "2. Aggregate and deduplicate results\n"
            "3. Categorize by theme\n"
            "4. Write trends_report.md with top trends and emerging topics"
        ),
        "tools": [{"type": "agent_toolset_20260401"}],
    },
}


# ── Registry helpers ──────────────────────────────────────────────────────────

def load_registry() -> dict:
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE) as f:
            return json.load(f)
    return {"agents": {}, "environment": None}


def save_registry(registry: dict):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)


def setup_team() -> dict:
    """
    Create agents and environment on first run; load IDs on subsequent runs.
    Agents are persistent — create once and reference by stored ID.
    """
    registry = load_registry()
    changed = False

    if "agents" not in registry:
        registry["agents"] = {}

    print("\n📋 Agent Team:")
    for key, defn in AGENT_DEFINITIONS.items():
        if key not in registry["agents"]:
            agent = client.beta.agents.create(
                name=defn["name"],
                model=CLAUDE_MODEL,
                system=defn["system"],
                tools=defn["tools"],
            )
            registry["agents"][key] = agent.id
            print(f"   + Created: {defn['name']}  ({agent.id})")
            changed = True
        else:
            aid = registry["agents"][key]
            print(f"   ✓ {defn['name']}  ({aid[:24]}...)")

    print("\n🌐 Environment:")
    if not registry.get("environment"):
        env = client.beta.environments.create(
            name="ai-trends-agent-team",
            config={"type": "cloud", "networking": {"type": "unrestricted"}},
        )
        registry["environment"] = env.id
        print(f"   + Created cloud sandbox  ({env.id})")
        changed = True
    else:
        eid = registry["environment"]
        print(f"   ✓ Cloud sandbox  ({eid[:24]}...)")

    if changed:
        save_registry(registry)

    return registry


# ── Session runner ────────────────────────────────────────────────────────────

def run_session(agent_id: str, env_id: str, label: str, task: str) -> str:
    """
    Start a session for `agent_id`, send `task`, stream events until idle.
    Returns the agent's final text output.
    """
    print(f"\n   🤖 {label}")
    print(f"   ▸ {task[:100]}{'...' if len(task) > 100 else ''}")

    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=env_id,
        title=f"{label}",
    )

    output_parts: list[str] = []

    with client.beta.sessions.events.stream(session.id) as stream:
        # Send task after stream opens (events are buffered until stream attaches)
        client.beta.sessions.events.send(
            session.id,
            events=[{
                "type": "user.message",
                "content": [{"type": "text", "text": task}],
            }],
        )

        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if hasattr(block, "text"):
                        print(block.text, end="", flush=True)
                        output_parts.append(block.text)
            elif event.type == "agent.tool_use":
                marker = f"\n   [Tool: {event.name}]" if DEBUG else "·"
                print(marker, end="", flush=True)
            elif event.type == "session.status_idle":
                print("\n   ✅ Idle")
                break

    return "".join(output_parts)


# ── Coordinator ───────────────────────────────────────────────────────────────

def run_agent_team(project_dir: str = ".") -> dict:
    """
    Multi-agent coordinator — orchestrates the three-agent team.

    Iteration cycle:
      1. Code Auditor  → discovers issues → ISSUES.md
      2. Issue Resolution → fixes issues → git commits
      3. (repeat until stable or MAX_ITER)
      4. Data Analytics → generates trends_report.md (always runs once)
    """
    print("\n" + "=" * 70)
    print("🚀 Phase 3: Managed Agents — Multi-agent Coordinator")
    print("=" * 70)

    registry = setup_team()
    agents = registry["agents"]
    env_id = registry["environment"]

    MAX_ITER = 3
    prev_count = float("inf")
    final_audit = ""
    final_resolve = ""

    for iteration in range(1, MAX_ITER + 1):
        print(f"\n{'─' * 50}")
        print(f"🔄  Iteration {iteration}/{MAX_ITER}")
        print("─" * 50)

        # Phase 1: Code Auditor
        print("\n[Phase 1] Code Auditor")
        audit_out = run_session(
            agents["code_auditor"],
            env_id,
            "Code Auditor Agent",
            (
                f"Audit all source files in '{project_dir}'. "
                "Find bugs, security issues, and code quality problems. "
                f"Write results to '{project_dir}/ISSUES.md' with priority labels (🔴🟡🟢). "
                "Skip already-resolved issues (marked ✅)."
            ),
        )
        final_audit = audit_out

        # Count unfixed issues from audit output
        issue_count = (
            audit_out.count("🔴")
            + audit_out.count("🟡")
            + audit_out.count("🟢")
        )

        if issue_count == 0:
            print("\n✅  No new issues found — agent team stable.")
            break

        if issue_count >= prev_count and iteration > 1:
            print(f"\n⚠️  Issue count not decreasing ({issue_count} ≥ {prev_count}). Manual review may be needed.")
            break

        prev_count = issue_count
        print(f"\n   → {issue_count} issue(s) detected, proceeding to resolution.")

        # Phase 2: Issue Resolution
        print("\n[Phase 2] Issue Resolution")
        resolve_out = run_session(
            agents["issue_resolution"],
            env_id,
            "Issue Resolution Agent",
            (
                f"Read '{project_dir}/ISSUES.md'. "
                "Fix all unresolved issues (those without ✅) in priority order (🔴 → 🟡 → 🟢). "
                "Create one git commit per issue fix. "
                "After each fix, mark the issue as ✅ in ISSUES.md."
            ),
        )
        final_resolve = resolve_out

    # Phase 3: Data Analytics (runs once regardless of iteration count)
    print("\n[Phase 3] Data Analytics")
    analytics_out = run_session(
        agents["data_analytics"],
        env_id,
        "Data Analytics Agent",
        (
            "Analyze the latest AI/ML trends from the past 7 days. "
            "Search Hacker News, arXiv, and Reddit for top discussions and papers. "
            "Aggregate, deduplicate, and categorize findings by theme. "
            f"Save output to '{project_dir}/trends_report.md'."
        ),
    )

    print("\n" + "=" * 70)
    print("📊  Agent Team Summary")
    print("=" * 70)
    print(f"  Iterations:  {iteration}")
    print(f"  Final state: {'Stable ✅' if issue_count == 0 else 'Check ISSUES.md'}")
    print(f"  Dashboard:   trends_report.md updated")

    return {
        "status": "success",
        "iterations": iteration,
        "audit_summary": final_audit[:300] if final_audit else "(none)",
        "analytics_summary": analytics_out[:300],
    }


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    """Run the managed agent team.

    Usage:
        python -m agent_harness.managed_agents [project_dir]
    """
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    try:
        run_agent_team(project_dir)
        return 0
    except KeyboardInterrupt:
        print("\n\n⛔  Agent team interrupted")
        return 1
    except Exception as exc:
        print(f"\n\n❌  Error: {exc}")
        if DEBUG:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
