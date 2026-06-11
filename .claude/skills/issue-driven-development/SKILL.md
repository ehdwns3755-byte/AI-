---
name: issue-driven-development
description: Complete workflow for GitHub Issues-driven development and project management
---

# Issue-Driven Development Workflow

## 📋 Purpose

This skill provides an end-to-end workflow for GitHub Issues-driven development: create issues from a project plan, track progress through comments, execute the plan, verify completion, and document the results.

## 🎯 When to Use

Use this skill when you need to:
- **Convert project plans into GitHub Issues** (roadmap → actionable issues)
- **Track progress with issue comments** (plan updates, blockers, decisions)
- **Execute issues systematically** (work through a priority list)
- **Verify issue completion** (test, validate, document)
- **Create follow-up issues** (cascade new work from discoveries)
- **Generate completion reports** (metrics, time tracking, lessons learned)

## 🔄 Complete Workflow

### Phase 1: Plan → Issues
```
1. Understand Project Plan
   ├─ Read plan file (CLAUDE.md, .md, project docs)
   ├─ Extract work items (tasks, milestones, acceptance criteria)
   ├─ Identify dependencies and priority order
   └─ Group related work under epics/milestones

2. Create GitHub Issues
   ├─ Generate issue title and description from plan items
   ├─ Add labels (epic, priority, area)
   ├─ Set milestone if applicable
   ├─ Assign to team members
   └─ Return issue numbers for tracking
```

### Phase 2: Track & Execute
```
3. Post Initial Plan as Comment
   ├─ Add checklist comment to each issue
   ├─ Break down work steps
   ├─ Estimate effort and dependencies
   └─ Link related issues

4. Execute Work
   ├─ Work through issues in priority order
   ├─ Update issue status in comments
   ├─ Post blockers and decisions
   ├─ Close issue when complete with proof
   └─ Create follow-up issues as discovered
```

### Phase 3: Verify & Report
```
5. Verify Completion
   ├─ Check that work meets acceptance criteria
   ├─ Run tests / validate output
   ├─ Get stakeholder approval
   └─ Document any deviations

6. Generate Completion Report
   ├─ Count issues by status
   ├─ Calculate time spent
   ├─ Identify blockers that became issues
   ├─ Extract learnings and next steps
   └─ Archive metrics
```

## 🛠️ Implementation Details

### Prerequisites
- **GitHub Personal Access Token** (repo scope)
- **Project plan document** (text, markdown, or plan file)
- **Repository access** to post issues and comments
- **Team clarity** on issue labels and workflow conventions

### Tools & Technologies
```
Issue Management:
  ├─ GitHub REST API v3
  ├─ Issue schema: {title, body, labels, milestone, assignee}
  ├─ Comments API for updates and blockers
  └─ Personal Access Token (ghp_...)

Plan Extraction:
  ├─ Read markdown/text plan documents
  ├─ Parse structured formats (YAML, JSON)
  ├─ Extract work items, milestones, dependencies
  └─ Group by epic or area

Progress Tracking:
  ├─ Comment templates (progress, blockers, decisions)
  ├─ Checklist completion tracking
  ├─ Time estimation and actuals
  └─ Cross-linking related issues
```

### Authentication Flow
```
1. Generate Token
   ├─ GitHub Settings → Developer settings → Personal access tokens
   ├─ Scopes: repo (full control of private repositories)
   └─ Keep token secure (environment variables or .env)

2. Verify Access
   ├─ Test API call: GET /repos/{owner}/{repo}
   ├─ Confirm token has repo scope
   └─ Ensure user has write access to repo

3. Create Issues & Comments
   ├─ POST /repos/{owner}/{repo}/issues
   ├─ POST /repos/{owner}/{repo}/issues/{issue_number}/comments
   └─ Return issue numbers and URLs
```

## 📊 Issue Template

### Issue Creation (from Plan)
```markdown
## What
[One-sentence summary of what needs to be done]

## Why
[Why is this important? What does it enable?]

## Acceptance Criteria
- [ ] Criterion 1: [specific, testable]
- [ ] Criterion 2: [specific, testable]
- [ ] Criterion 3: [specific, testable]

## Implementation Plan
[Steps to complete, dependencies, estimated effort]

## Related Issues
- Blocked by #X
- Blocks #Y
- Related to #Z

## Labels
- epic:my-epic
- priority:high
- area:backend
```

### Progress Comment
```markdown
## Progress Update

### Completed
- [x] Step 1: [description]
- [x] Step 2: [description]

### In Progress
- [ ] Step 3: [description] (ETA: 2 hours)

### Blocked
- [ ] Step 4: [description] (Waiting for: #123)

### Notes
- Discovery: [new information]
- Decision: [what we chose and why]
- Next: [what's next]

**Time spent**: 2h | **Estimate remaining**: 1h
```

### Completion Comment
```markdown
## ✅ Issue Complete

### What Was Done
- Implemented X feature
- Added Y tests
- Updated Z documentation

### Testing
- [x] Manual test on feature
- [x] Automated tests pass
- [x] Code review approved by @reviewer

### Proof
- PR: #456
- Deployed to: production
- Dashboard: [link]

**Total time**: 2h 30m | **Status**: Ready for release

### Follow-up Issues Created
- #789: Performance optimization
- #790: Documentation update
```

## 🔐 Security Checklist

Before running this workflow:

- [ ] **Token Security**
  - Token stored in environment variable (not in code)
  - Token has minimal required scopes (repo only)
  - Token will be rotated regularly
  - Token is not hardcoded in scripts

- [ ] **Data Privacy**
  - Plan being tracked is approved for public/private visibility
  - No sensitive data (API keys, credentials) in issues
  - Issues created in appropriate repository (private if sensitive)
  - Comments don't expose internal decisions

- [ ] **Access Control**
  - All team members have repo access
  - Issue permissions match visibility (private repo = internal only)
  - Assignments are to authorized team members

## 💡 Best Practices

### For Converting Plans to Issues
1. **Be specific** — "Implement user authentication" not "Fix auth stuff"
2. **Include acceptance criteria** — "PR reviewed and merged" not "Done"
3. **Estimate effort** — Size as S/M/L/XL or hours for clarity
4. **Link dependencies** — Issues should reference blockers with #number
5. **Group by epic** — Related work gets same label for filtering

### For Tracking Progress
1. **Comment frequently** — Update progress daily, not at the end
2. **Post blockers early** — Don't wait until stuck
3. **Use checklists** — Visual progress keeps team aligned
4. **Reference commits** — Link PRs and commits to issues
5. **Time tracking** — Post actuals vs estimates for future planning

### For Execution
1. **One issue at a time** — Complete before moving to next
2. **Test thoroughly** — Validate before marking done
3. **Document discovery** — New issues from learning go to backlog
4. **Get approval** — Code review or stakeholder sign-off before close
5. **Link everything** — PRs reference issues, commits reference PRs

## 🚀 Example Workflow

### Step 1: Create Issues from Plan
```
Input: AI Dashboard project plan (8 work items)
Process: Parse plan, create issues for each item
Output: 8 GitHub Issues (#1-#8) with labels and milestones
```

### Step 2: Post Plan Comment
```
Input: Issue #1 (Implement API endpoint)
Process: Post checklist comment with breakdown
Output: Issue shows: 5 subtasks, estimated 4 hours
```

### Step 3: Execute & Update
```
Input: Work on issue #1
Process: Update comment with progress, create PR
Output: Comment shows: 3/5 steps done, waiting on code review
```

### Step 4: Close with Proof
```
Input: Work complete and approved
Process: Post completion comment with PR link
Output: Issue closed, linked to PR #456, time tracked
```

### Step 5: Generate Report
```
Input: All issues closed
Process: Aggregate metrics from comments
Output: Completion report: 8/8 issues, 12h total, 0 blockers
```

## 📝 Integration Points

### With Project Management
- Sync GitHub Issues ↔ Linear/Jira/Asana via webhooks
- Set milestones to track releases
- Use labels for filtering in dashboards
- Archive closed issues for retrospectives

### With Development Workflow
- Link PRs to issues (#456 closes #123)
- Reference issues in commit messages (Fix #123)
- Use issue numbers in branch names (feature/123-auth)
- Block PRs until linked issue is approved

### With Notifications
- Mention @person in comments for attention
- Set up GitHub notifications for followed issues
- Create alerts for specific labels (priority:critical, blocked)
- Digest emails for team standup

## ⚙️ Configuration

### Environment Variables
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"  # Your PAT
export GITHUB_OWNER="your-org"                   # Repository owner
export GITHUB_REPO="your-repo"                   # Repository name
export ISSUE_MILESTONE="v1.0"                    # Optional milestone
export ISSUE_EPIC_LABEL="epic:my-feature"        # Optional epic label
```

### API Endpoints
```
Base URL: https://api.github.com
Issues: POST /repos/{owner}/{repo}/issues
Comments: POST /repos/{owner}/{repo}/issues/{issue_number}/comments
Close: PATCH /repos/{owner}/{repo}/issues/{issue_number}
Labels: GET /repos/{owner}/{repo}/labels
```

### Workflow Labels (Suggested)
```
Priority: priority:critical, priority:high, priority:medium, priority:low
Status: status:ready, status:blocked, status:review
Type: type:bug, type:feature, type:docs, type:refactor
Area: area:frontend, area:backend, area:devops, area:security
Epic: epic:auth, epic:api, epic:dashboard, epic:infra
```

## 🔗 Related Skills

- **code-audit-and-github-issues** — Find bugs and create issues from code review
- **code-refactoring** — Large-scale improvements tracked in issues
- **pull-request-review** — Review PRs linked to issues
- **project-management** — Broader portfolio and portfolio planning

## 📚 References

- [GitHub REST API - Issues](https://docs.github.com/en/rest/issues)
- [GitHub Issues Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- [GitHub Project Management](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Agile Methodology](https://www.atlassian.com/agile/project-management/user-stories)
