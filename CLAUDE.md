# Claude Code Instructions for AI Trends Dashboard

Project Setup Guide for Claude AI Integration

---

## 📋 Project Overview

**Project**: AI Trends Dashboard with Agent Harness Architecture
**Type**: Python-based trend aggregation & analysis system
**Status**: Active development with multi-agent orchestration

**Key Files**:
- `AGENT_HARNESS.md` - Complete harness architecture & patterns
- `AGENTS.md` - Team agent role definitions
- `agent_harness/` - Core implementation package
- `requirements.txt` - Dependencies (includes anthropic SDK)

---

## 🤖 Agent Harness Configuration

### Phase 1: Tool Runner SDK (Current)

**Status**: ✅ Implemented
**Location**: `agent_harness/runner.py`
**Pattern**: Automatic tool execution loop
**Reference**: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner

#### How It Works

```
User Request
     ↓
[Agent Loop - Tool Runner]
     ↓
  ┌──────────────────────────┐
  │ 1. Claude receives tools │
  │ 2. Claude requests tool  │
  │ 3. Runner executes tool  │
  │ 4. Result fed back       │
  │ 5. Loop until done       │
  └──────────────────────────┘
     ↓
Final Dashboard Output
```

**Key Components**:

1. **Config** (`agent_harness/config.py`)
   - `ANTHROPIC_API_KEY`: Claude API authentication
   - `CLAUDE_MODEL`: "claude-opus-4-8"
   - `AGENT_EFFORT`: "high" (xhigh for complex tasks)
   - `MAX_ITERATIONS`: 10 (prevent runaway loops)
   - `MAX_TOKENS`: 4096 (output limit)

2. **Tools** (`agent_harness/tools/trend_collector.py`)
   - `fetch_hacker_news_trends()` - HN trending stories
   - `fetch_arxiv_trends()` - arXiv research papers
   - `fetch_reddit_trends()` - Reddit discussions
   - `aggregate_trends()` - Deduplicate & combine
   - `categorize_trends()` - Topic organization

3. **Runner Loop** (`agent_harness/runner.py`)
   - Orchestrates tool execution
   - Manages context window
   - Handles responses
   - Reports progress

#### Tool Definitions

Each tool follows this pattern:

```python
@beta_tool  # (future: from anthropic.lib.beta)
def tool_name(param: type) -> str:
    """
    Tool description for Claude.
    
    Args:
        param: Parameter description
    
    Returns:
        JSON string with results
    """
    # Implementation
    return json.dumps({...})
```

**Tool Execution Flow**:
1. Claude requests tool with parameters
2. `execute_tool()` dispatches to implementation
3. Tool runs and returns JSON string
4. Result automatically fed back to Claude
5. Claude decides next step (another tool or final response)

#### Running the Agent

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Tool Runner agent
python -m agent_harness.runner

# Expected output:
# Turn 1: Claude requests fetch_hacker_news_trends
#         Runner executes, returns 10 items
# Turn 2: Claude requests fetch_arxiv_trends
#         Runner executes, returns papers
# Turn 3: Claude requests aggregate_trends
#         Runner deduplicates & combines
# Turn 4: Claude requests categorize_trends
#         Runner organizes by topic
# Turn 5: Claude produces final report
```

**Environment Variables** (in `.env`):

```bash
ANTHROPIC_API_KEY=sk-ant-...
ANALYSIS_DEPTH=high
MAX_ITERATIONS=10
TRENDS_SOURCES=hacker-news,arxiv,reddit
TRENDS_DAYS=7
DEBUG=false
```

---

## 🔄 Agent Team Structure

### Three Specialized Agents

**1. Code Auditor Agent**
- Role: Code quality review
- Trigger: iterative-document-optimization skill
- Output: ISSUES.md (discovered issues)

**2. Issue Resolution Agent**
- Role: Automatic issue fixing
- Trigger: issue-resolution-workflow skill
- Output: Git commits with fixes

**3. Data Analytics Agent**
- Role: Trend analysis & visualization
- Trigger: agent_harness/runner.py
- Output: Dashboard HTML/data

### Communication Pattern

Agents communicate via:
- **Git commits** - State changes
- **Issue tracking** - Task assignment
- **ISSUES.md** - Issue registry
- **Environment variables** - Configuration
- **Tool results** - Data exchange

### Workflow Execution

```
Iteration Cycle:
  1. Code Auditor discovers issues
     └─> Updates ISSUES.md
  
  2. Issue Resolution fixes all issues
     └─> Creates atomic commits
  
  3. Data Analytics processes trends
     └─> Generates dashboard
  
  4. Repeat if new issues found
     else: ✅ Optimization complete
```

---

## 📋 Development Guidelines

### Adding New Tools

1. Create function in `agent_harness/tools/*.py`
2. Decorate with `@beta_tool` (placeholder for now)
3. Return `str` (JSON format)
4. Add tool definition to `TREND_TOOLS` in `runner.py`:

```python
{
    "name": "tool_name",
    "description": "What this tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "..."}
        },
        "required": ["param"]
    }
}
```

5. Add dispatch logic to `execute_tool()`:

```python
elif tool_name == "tool_name":
    result = tool_name(tool_input.get("param"))
```

### Error Handling

Tools should return:

**Success**:
```json
{
  "status": "success",
  "count": 10,
  "items": [...]
}
```

**Error**:
```json
{
  "status": "error",
  "error": "Error message"
}
```

Claude will handle `is_error: true` in tool results.

### Context Management

Tool Runner automatically:
- ✅ Caches system prompt
- ✅ Manages conversation history
- ✅ Stops when no more tool calls
- ✅ Compacts context if needed

Don't worry about context window manually.

---

## 🚀 Phase Roadmap

### Phase 1: Tool Runner ✅ (Complete)

**What**: Automatic tool execution loop
**When**: Now
**Effort**: ~1 week to test & validate
**Infrastructure**: Local (no cloud needed)

```bash
python -m agent_harness.runner
```

### Phase 2: Agent SDK Loop (Planned)

**What**: Manual loop for HITL & custom logging
**When**: When approval gates needed
**Effort**: ~2 weeks
**Location**: `agent_harness/sdk_loop.py`

**Use cases**:
- Require human approval before risky operations
- Custom logging per turn
- Conditional tool execution

### Phase 3: Multiagent Coordinator ✅ (Complete)

**What**: Three specialized agents coordinated in sequence
**When**: Enabled — run via `python -m agent_harness.managed_agents`
**Effort**: Complete
**Infrastructure**: Claude Managed Agents (beta, `managed-agents-2026-04-01`)

**Agents** (`agent_harness/agent_registry.json`):
- `code_auditor` — Code Auditor Agent (discovers issues → ISSUES.md)
- `issue_resolution` — Issue Resolution Agent (fixes issues → git commits)
- `data_analytics` — Data Analytics Agent (trends → trends_report.md)

**Run**:
```bash
python -m agent_harness.managed_agents [project_dir]
```

---

## 🔧 Configuration

### Model Selection

**Current**: `claude-opus-4-8`
- Reasoning depth: xhigh
- Thinking: Adaptive
- Cost: Optimal for analysis

**Don't change unless**:
- Performance issues → try `claude-sonnet-4-6`
- Need ultra-reasoning → try `claude-fable-5` (beta)

### Tool Timeout

Each tool should complete in < 30 seconds. If slower:
1. Add `timeout` parameter to requests
2. Implement streaming results
3. Break into smaller tools

### Context Window

- Total: 1M tokens (Opus 4.8)
- System prompt + tools: ~2K tokens (cached)
- Per turn available: ~990K tokens

Don't add tools with huge descriptions.

---

## 📊 Debugging

### Enable Debug Mode

```bash
DEBUG=true python -m agent_harness.runner
```

Shows:
- Each Claude API call
- Tool requests & parameters
- Tool execution timing
- Full JSON responses

### Common Issues

| Issue | Solution |
|-------|----------|
| API key error | Check `.env`, `ANTHROPIC_API_KEY` |
| Tool not found | Verify in `execute_tool()` dispatch |
| Timeout | Add timeout to requests, break tool |
| Max iterations | Increase `MAX_ITERATIONS` or debug loop |
| OOM on large data | Stream results or paginate |

### Logs Location

Tool Runner prints to stdout with clear markers:
- 📍 Turn indicators
- 🔧 Tool execution
- ✅ Completion
- ❌ Errors

---

## 🎯 Best Practices

### For Tool Development

1. **Keep tools focused** - One responsibility each
2. **Return JSON** - Always `str(json.dumps(...))`
3. **Handle errors gracefully** - Never raise, return error JSON
4. **Test independently** - Before adding to runner

```python
# ✅ Good
def fetch_trends(source: str) -> str:
    try:
        data = fetch_from_api(source)
        return json.dumps({"status": "success", "data": data})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})

# ❌ Bad
def fetch_trends(source: str) -> dict:
    data = fetch_from_api(source)  # Can raise
    return data  # Returns dict, not str
```

### For Agent Prompts

1. **Be explicit** - Tell Claude exactly what to do
2. **Use phases** - Break into clear steps
3. **Name tools clearly** - `fetch_hacker_news_trends` not `hn()`
4. **Set expectations** - "Use these tools in sequence: 1) fetch 2) aggregate 3) categorize"

### For Loop Management

1. **Set `MAX_ITERATIONS`** - Always, prevents runaway
2. **Monitor cost** - High effort = higher cost, worth it?
3. **Check `stop_reason`** - Only `end_turn` means Claude is done
4. **Handle `tool_use` gracefully** - Never assume tool succeeds

---

## 🔗 Related Documentation

### Claude Official Docs
- [Tool Runner Pattern](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner)
- [Agent SDK Loop](https://code.claude.com/docs/en/agent-sdk/agent-loop)
- [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)
- [Multiagent Sessions](https://platform.claude.com/docs/en/managed-agents/multi-agent)

### Project Docs
- `AGENT_HARNESS.md` - Full architecture & patterns
- `AGENTS.md` - Team agent definitions
- `ISSUES.md` - Current issue registry

---

## 📝 Git Workflow

### Commit Messages

Follow conventional commits:

```
feat: Add new tool or feature
fix: Bug fix in agent harness
docs: Update documentation
refactor: Code restructuring
```

Example:
```
feat: Add new trend categorization logic

- Implement ML/LLM category detection
- Add 5 new topic categories
- Update categorize_trends() tool

Fixes issue in ISSUES.md #5
```

### Before Pushing

1. Run agent to verify
2. Check `git status` for unexpected changes
3. Ensure tests pass (if applicable)
4. Review commit messages

---

## ✅ Validation Checklist

When running the agent:

- [ ] API key works (no 401 errors)
- [ ] Tools execute without errors
- [ ] Results are valid JSON
- [ ] Claude produces coherent response
- [ ] Loop completes in < 5 minutes
- [ ] Output can be used by dashboard

---

## 🤝 Contributing

When adding features:

1. Update `AGENT_HARNESS.md` with architecture changes
2. Document new tools with docstrings
3. Add tool definitions to `runner.py`
4. Test in `DEBUG=true` mode first
5. Commit with clear message

---

## Last Updated

2026-06-12 - Agent Harness Phase 1 Complete

**Next Review**: Before Phase 2 implementation

