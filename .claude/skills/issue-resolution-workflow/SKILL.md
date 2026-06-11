---
name: issue-resolution-workflow
description: "Automate issue resolution workflow for any project. This skill reads issues from ISSUES.md or similar files, prioritizes them by severity, directly fixes code, and generates atomic commits. Use this whenever your project has an issues list that needs systematic resolution. Works with any codebase - Python, JavaScript, Go, etc. The skill handles parsing issues, understanding the problems, implementing fixes, and committing changes automatically."
compatibility: "Requires git repository with issue documentation"
---

# Issue Resolution Workflow

Automate the complete workflow for resolving documented issues in a project. This skill:

1. **Discovers and parses issues** from ISSUES.md or similar documentation
2. **Prioritizes intelligently** by severity (High → Medium → Low) and type
3. **Analyzes and fixes code** directly using available tools
4. **Generates professional commits** with detailed commit messages
5. **Works across any project** - language/framework agnostic

## When to use this skill

- You have a list of documented issues in your project (bugs, improvements, refactoring)
- You want to resolve multiple issues systematically instead of ad-hoc
- You want atomic commits with clear messages for each fix
- Your issues include reproduction steps, expected vs actual behavior, or solutions

## How it works

### Step 1: Discover Issues
The skill searches for issue documentation (ISSUES.md, TODO.md, bugs.md, etc.) in the project root.

### Step 2: Parse and Categorize
Issues are parsed by:
- **Priority**: High (🔴) → Medium (🟡) → Low (🟢)
- **Type**: Bug, Feature, Improvement, Documentation, etc.
- **Status**: Identifies which issues are already resolved

### Step 3: Resolve Issues in Order
For each unresolved issue, the skill:
1. **Reads** the problem description and context
2. **Locates** affected code files and lines
3. **Implements** the fix using Edit/Write/Bash tools
4. **Tests** the changes where possible
5. **Verifies** the fix doesn't introduce regressions

### Step 4: Commit Changes
After each fix (or batch of related fixes):
- Generates a clear commit message following conventional commits
- Includes references to the issue being fixed
- Tags the co-author

## Issue Documentation Format

The skill works with issues documented like this:

```markdown
## Issue Title

**Type:** Bug 🐛 / Improvement 📈 / Feature ✨ / Documentation 📚
**Priority:** 🔴 High / 🟡 Medium / 🟢 Low

### Problem
Clear description of what's wrong or missing.

### Location
- File path and line numbers
- Function/class names

### Solution
Suggested fix or approach.

### Expected Result
What should happen after the fix.
```

## Configuration

The skill automatically detects:
- **Issue files**: ISSUES.md, TODO.md, BUGS.md, GitHub issues (via CLI)
- **Project type**: Python, JavaScript, Go, Java, etc.
- **Version control**: Git or other VCS
- **Build system**: npm, pip, cargo, maven, etc.

## Example

**Input:**
```markdown
## XSS Vulnerability in HTML generation

**Type:** Bug 🐛
**Priority:** 🔴 High

### Problem
User input is directly inserted into HTML without escaping, allowing XSS attacks.

### Location
- dashboard.py, line 347: `{item['title']}`
- dashboard.py, line 350: `{item['summary']}`

### Solution
Use html.escape() to sanitize all user input before HTML rendering.
```

**Output:**
- ✅ Code is automatically fixed
- ✅ Commit created: `fix: Prevent XSS vulnerabilities in HTML generation`
- ✅ Issue marked as resolved

## Best Practices

1. **Detailed issue descriptions** → Better fixes. Include reproduction steps for bugs.
2. **File paths and line numbers** → Helps locate problems faster.
3. **Solution hints** → Optional but helpful (e.g., "Use middleware X", "Add timeout=10")
4. **Group related issues** → Fixes can be batched in one commit when appropriate.

## Limitations

- Issues that require architectural changes may need human review
- Complex refactoring might be split across multiple commits
- Issues requiring external API changes will be highlighted for review
- No automatic PR creation (use GitHub CLI separately if needed)

## Next Steps After Resolution

1. Review generated commits: `git log --oneline -n 5`
2. Push to remote: `git push origin main`
3. Create PR if needed: `gh pr create --title "Fix all issues" --body "..."`
4. Update ISSUES.md to mark resolved issues with ✅

---

## Execution Steps

When you invoke this skill, follow these steps:

### Step 1: Discover Issues File
```bash
# Look for issue documentation in the project
find . -maxdepth 2 -type f -name "ISSUES.md" -o -name "TODO.md" -o -name "BUGS.md" | head -5
```

If no file found, ask the user to provide or create an ISSUES.md file.

### Step 2: Parse Issues
Read the issues file and extract:
- Issue title
- Type (Bug, Feature, Improvement, Documentation)
- Priority (High 🔴, Medium 🟡, Low 🟢)
- Problem description
- Location (file paths, line numbers)
- Suggested solution
- Current status

### Step 3: Prioritize and Filter
Sort issues by:
1. Priority (High → Medium → Low)
2. Type (Bug → Feature → Improvement → Documentation)
3. Filter out already resolved issues (marked with ✅)

### Step 4: Resolve Each Issue
For each unresolved issue in order:

1. **Read the context**
   - Understand the problem from the description
   - Locate the affected files using the file paths provided
   
2. **Implement the fix**
   - Use Read tool to examine current code
   - Use Edit tool to make changes
   - Use Write tool for new files if needed
   - Use Bash/PowerShell for complex operations
   
3. **Test if possible**
   - Run tests: `npm test`, `pytest`, etc.
   - Verify the fix works
   - Check for regressions

4. **Create a commit**
   - Stage changes: `git add -A` or specific files
   - Create commit with message: `git commit -m "fix: <description>"`
   - Commit message should:
     - Start with type: fix(scope), feat(scope), docs, refactor, etc.
     - Reference the issue: "Resolves issue #X" or "Fixes problem with X"
     - Be concise but descriptive
     - Include Co-Authored-By if appropriate

### Step 5: Report Progress
After completing each issue:
- Print status: `✅ Resolved: [Issue Title]`
- Show commit hash
- Summarize what changed

### Step 6: Final Summary
After all issues are resolved:
- Print total issues resolved
- Show commit log of all new commits
- List any issues that require manual review
- Ask if user wants to push changes

## Usage Example

```
/issue-resolution-workflow
```

The skill will:
1. Find ISSUES.md in current directory
2. Parse all documented issues
3. Sort by priority (High → Medium → Low)
4. Fix each issue automatically with proper commits
5. Report completion status
6. Ask if you want to push to remote

## Example Workflow

**Initial state:** 5 unresolved issues in ISSUES.md

**Execution:**
```
🔍 Discovering issues file...
✓ Found: ISSUES.md (5 issues)

📋 Parsing and prioritizing...
Issues found:
  🔴 [HIGH] XSS vulnerability - database.py:45
  🔴 [HIGH] Missing error handling - api.py:120
  🟡 [MEDIUM] Improve logging - main.py:30
  🟡 [MEDIUM] Update README - README.md
  🟢 [LOW] Code cleanup - utils.py

🔧 Resolving issues...

1️⃣  Fixing XSS vulnerability...
   📝 database.py modified
   ✅ Tests passed
   📦 Commit: fix: Prevent XSS attacks with HTML escaping

2️⃣  Fixing error handling...
   📝 api.py modified
   ✅ Tests passed
   📦 Commit: fix: Add error handling to API routes

... (continuing for all issues)

✅ All issues resolved!
📊 Summary:
   - 5 issues fixed
   - 5 commits created
   - Ready to push!
```

## Important Notes

- Each fix should result in a **separate, atomic commit** for clarity
- Use descriptive commit messages following **conventional commits** format
- Mark issues as resolved in ISSUES.md by adding ✅
- Test changes when possible to ensure they work
- For complex fixes, explain the approach before implementing
