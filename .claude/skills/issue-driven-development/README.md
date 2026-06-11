# Issue-Driven Development Workflow

## Quick Start

This skill automates the complete workflow: **Plan → Issues → Execute → Track → Verify → Report**.

### Three-Phase Process

```
┌──────────────────┐
│  1. Plan Input   │  Read project plan
│     → Issues     │  Create GitHub Issues
└────────┬─────────┘
         │
┌────────▼─────────┐
│  2. Track &      │  Post progress comments
│     Execute      │  Update issue status
│     Work         │  Link PRs to issues
└────────┬─────────┘
         │
┌────────▼─────────┐
│  3. Verify &     │  Validate completion
│     Report       │  Generate metrics
│     Results      │  Archive for insights
└──────────────────┘
```

## Files in This Skill

- **SKILL.md** — Complete skill definition (methodology, workflows, best practices)
- **README.md** — This file (quick reference)
- **plan_to_issues_example.md** — Sample plan and generated issues
- **progress_tracking_example.md** — Example progress comments and closures

## When Claude Uses This Skill

The main agent will automatically apply this skill when you ask to:

```
❌ "Create issues from my project plan"
✅ "Convert my AI dashboard plan to GitHub Issues and track progress"

❌ "Update issue status"
✅ "Post progress updates to these GitHub Issues and close them when done"

❌ "Summarize what we built"
✅ "Create completion report from our closed issues, with time tracking and metrics"
```

## Key Features

### 1. **Plan to Issues Conversion**
- Parse project plans (markdown, text, structured)
- Extract work items and milestones
- Create GitHub Issues with proper structure
- Set labels, milestones, and dependencies
- Group by epic or area

### 2. **Progress Tracking**
- Post checklist comments
- Update status with time tracking
- Document blockers and decisions
- Link PRs and commits to issues
- Create follow-up issues as discovered

### 3. **Completion Verification**
- Validate acceptance criteria met
- Check test coverage and reviews
- Document proof (PR links, test results)
- Generate completion reports with metrics
- Archive learnings for retrospectives

## Usage Example

### Step 1: Convert Plan to Issues

```
User: "I have an AI dashboard project plan. Convert it to GitHub Issues 
       and track progress as I implement each item."

Claude applies this skill to:
  ✓ Parse the plan (7 work items)
  ✓ Create 7 GitHub Issues (#1-#7)
  ✓ Set labels (epic:dashboard, area:backend)
  ✓ Set milestone (v1.0)
  ✓ Return issue URLs for tracking
```

### Step 2: Execute & Update

```
User: "I'm working on issue #1 (API Setup). Update status."

Claude applies this skill to:
  ✓ Parse progress description
  ✓ Post comment with checklist
  ✓ Link any PRs (#456)
  ✓ Track time (2h done, 1h remaining)
  ✓ Flag blockers or decisions
```

### Step 3: Close & Report

```
User: "All issues are done. Generate a completion report."

Claude applies this skill to:
  ✓ Verify all issues closed
  ✓ Count time per issue
  ✓ Extract learnings from comments
  ✓ Generate metric report
  ✓ Recommend follow-ups
```

## Prerequisites

Before using this skill, ensure:

1. **GitHub Personal Access Token** (create at settings/tokens)
   ```bash
   export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
   ```

2. **Repository Access**
   - Repository is public or you have write access
   - Token has `repo` scope (full control)

3. **Project Plan**
   - Clear work items and milestones
   - Ideally with estimates and dependencies
   - Acceptance criteria for each item

## API Authentication

This skill uses **GitHub REST API v3** with Personal Access Tokens:

```bash
# Create Token
1. Visit: https://github.com/settings/tokens/new
2. Scopes: Select "repo" (full control of private repositories)
3. Copy token (only shown once!)
4. Store in environment: export GITHUB_TOKEN="ghp_..."

# Permissions needed
- repo (full control of repositories)
- read:user (to verify authenticated)
- project (if using GitHub Projects)
```

## Rate Limiting

GitHub API limits:
- **Unauthenticated**: 60 requests/hour
- **Authenticated**: 5,000 requests/hour ← You'll use this

For 10 issues with 5 comments each: ~50 API calls, well under the limit.

## Example Workflow

### Input: Project Plan

```markdown
# AI Trends Dashboard v1.0

## Phase 1: Setup (2 days)
- [ ] Create git repository
- [ ] Set up requirements.txt
- [ ] Write README.md

## Phase 2: Core Features (3 days)
- [ ] Fetch news from Google News
- [ ] Fetch news from Hacker News
- [ ] Generate HTML dashboard

## Phase 3: Automation (1 day)
- [ ] Set up Windows Task Scheduler
- [ ] Test daily automation
- [ ] Deploy to GitHub
```

### Output: GitHub Issues

```markdown
Issue #1: Set up project repository
├─ Labels: epic:setup, priority:high, area:infra
├─ Milestone: v1.0
├─ Effort: 2 hours

Issue #2: Fetch news from Google News
├─ Labels: epic:features, priority:high, area:backend
├─ Milestone: v1.0
├─ Effort: 4 hours
├─ Blocked by: #1

Issue #3: Generate HTML dashboard
├─ Labels: epic:features, priority:high, area:frontend
├─ Milestone: v1.0
├─ Effort: 3 hours
└─ Depends on: #2

... [7 total issues]
```

### During Work: Progress Comment

```markdown
## Progress Update

### Completed
- [x] Initialize git repository
- [x] Create requirements.txt

### In Progress
- [ ] Write README (50% done)

### Blocked
- None

**Time spent**: 1h 30m | **Estimate remaining**: 30m
```

### After Completion: Issue Closed

```markdown
## ✅ Complete

### What Was Done
- Created repository with git init
- Added requirements.txt with dependencies
- Wrote comprehensive README.md

### Proof
- PR: #123
- Commit: abc1234

**Total time**: 2 hours | **Status**: Ready

### Next Steps
- #2 can now start (unblocked)
```

## Troubleshooting

### Issue Creation Failed (401 Unauthorized)
**Problem**: Token invalid or expired
**Solution**: 
1. Regenerate token at https://github.com/settings/tokens
2. Update GITHUB_TOKEN environment variable
3. Verify token has `repo` scope

### Cannot Find Plan File
**Problem**: Plan document path not correct
**Solution**:
1. Check file location (local vs remote)
2. Verify file format (markdown, text, YAML)
3. Provide full path or file content inline

### Comments Not Posting
**Problem**: Insufficient repo permissions
**Solution**:
1. Verify you have write access to repo
2. Check token scope includes `repo`
3. Ensure issue exists and is accessible

## Integration with Managed Agents

This skill is available for use in Claude Managed Agents:

```python
agent = client.beta.agents.create(
    name="Project Manager",
    model="claude-opus-4-8",
    system="You manage GitHub Issues-driven projects...",
    skills=[
        {
            "type": "custom",
            "skill_id": "issue-driven-development",
            "version": "latest"
        }
    ]
)
```

When you start a session with this agent and ask it to convert a plan to issues, it will automatically:
1. Parse your project plan
2. Create structured GitHub Issues
3. Track progress via comments
4. Verify completion and generate reports

## Next Steps

1. **Store Your Token**
   ```bash
   export GITHUB_TOKEN="your_token_here"
   ```

2. **Prepare Your Plan**
   - Write or provide a project plan with clear work items
   - Include estimates and dependencies where possible
   - Define acceptance criteria for each item

3. **Start an Issue-Driven Project**
   ```
   "Convert my project plan to GitHub Issues and help me track progress."
   ```

4. **Track Progress**
   - Comment on issues with daily updates
   - Link PRs and commits
   - Post blockers and decisions

5. **Generate Reports**
   - Ask for completion metrics
   - Review learnings and next steps
   - Archive for retrospectives

## Related Documentation

- [SKILL.md](./SKILL.md) — Complete methodology and workflows
- [plan_to_issues_example.md](./plan_to_issues_example.md) — Real plan conversion
- [progress_tracking_example.md](./progress_tracking_example.md) — Progress examples

## Support

For issues with this skill:
1. Check the **Prerequisites** section above
2. Review **Troubleshooting** for common problems
3. Verify your GitHub token and repository access
4. Consult [GitHub REST API docs](https://docs.github.com/en/rest)

---

**Skill Version**: 1.0  
**Last Updated**: 2026-06-11  
**Status**: Production Ready
