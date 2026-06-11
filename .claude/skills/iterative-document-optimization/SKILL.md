---
name: iterative-document-optimization
description: "Automate the complete cycle of project optimization: analyze code, discover issues, resolve them, and repeat until no new issues are found. This skill orchestrates a full iterative workflow that combines code auditing (to find issues) with automatic issue resolution (to fix them). Use this whenever you want to continuously improve a project's code quality and documentation. The skill handles analysis, issue discovery, implementation, validation, and iteration automatically - perfect for bringing legacy projects up to standard or refactoring large codebases systematically."
compatibility: "Requires: code-audit-and-github-issues skill, issue-resolution-workflow skill, git repository"
---

# Iterative Document & Code Optimization Workflow

**Automate continuous project improvement through iterative cycles of issue discovery and resolution.**

This skill orchestrates a complete optimization loop:
1. **Analyze** the project (code, documentation, structure)
2. **Discover** issues using code audit (via code-audit-and-github-issues skill)
3. **Resolve** all discovered issues (via issue-resolution-workflow skill)
4. **Evaluate** improvements and repeat until no new issues are found

Perfect for:
- **Refactoring legacy projects** - Continuously improve code quality
- **Quality assurance** - Systematic bug discovery and fixing
- **Documentation optimization** - Keep docs in sync with code
- **Codebase modernization** - Find and fix deprecated patterns
- **Compliance checks** - Discover and resolve security issues

## How It Works

### Phase 1: Project Analysis
- Reads project structure (README.md, package.json, requirements.txt, etc.)
- Identifies programming language and framework
- Assesses current state and identifies improvement areas

### Phase 2: Issue Discovery (Cycle)
- Calls `code-audit-and-github-issues` skill
- Generates comprehensive list of issues (bugs, improvements, refactoring)
- Records issue count and details in ISSUES.md

### Phase 3: Issue Resolution (Cycle)
- Calls `issue-resolution-workflow` skill
- Automatically fixes all discovered issues
- Creates atomic commits for each fix
- Updates documentation

### Phase 4: Validation & Iteration
- Checks if new issues were discovered
- **If new issues found**: Repeat Phase 2-4
- **If no new issues**: Optimization complete ✅

## Iteration Logic

The skill automatically repeats until reaching a **steady state** (no new issues):

```
Iteration 1:
  Issue Count: 5
  → Discover & fix 5 issues
  → Commit changes

Iteration 2:
  Issue Count: 3 (fewer than before!)
  → Discover & fix 3 issues
  → Commit changes

Iteration 3:
  Issue Count: 3 (no new issues)
  → STOP - Optimization complete
```

This ensures:
- ✅ All discoverable issues are found and fixed
- ✅ Code quality reaches a stable level
- ✅ Documentation is synchronized with code
- ✅ Each improvement builds on the previous one

## Example Workflow

**Initial Project State:**
- 50 issues in code quality
- Outdated README
- Missing error handling
- Security vulnerabilities

**Execution:**

```
🔍 ITERATION 1: Initial Audit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Issues discovered: 12
  - 3 Security issues
  - 4 Code quality issues
  - 3 Documentation issues
  - 2 Performance issues

🔧 Resolving all 12 issues...
✅ Fixed security vulnerabilities
✅ Improved error handling
✅ Updated documentation
✅ Optimized performance

📦 Created 12 commits

🔍 ITERATION 2: Second Pass
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Issues discovered: 5
  (Fewer issues due to fixes from iteration 1)
  - 1 Code smell
  - 2 Documentation
  - 2 Test coverage

🔧 Resolving all 5 issues...
✅ Refactored problematic code
✅ Improved test coverage
✅ Updated docs

📦 Created 5 commits

🔍 ITERATION 3: Final Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Issues discovered: 5 (Same as last iteration)
✅ No new issues! Optimization complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 FINAL RESULTS:
  • Total iterations: 3
  • Total issues fixed: 22
  • Total commits: 22
  • Code quality improved: 100%
  • Ready for production ✅
```

## Execution Flow

### Step 1: Analyze Project
```bash
# The skill will:
1. Read README.md, package.json, requirements.txt, etc.
2. Identify project type (Python, Node, Go, etc.)
3. Assess current code structure
4. Understand project goals from documentation
```

### Step 2: Iterate Until Stable
```bash
# For each iteration:
REPEAT {
  1. Call code-audit-and-github-issues skill
     → Generate comprehensive issue list
     → Save to ISSUES.md
  
  2. Record issue count
  
  3. Call issue-resolution-workflow skill
     → Fix all issues
     → Create commits
  
  4. Run code-audit-and-github-issues again
     → Check for new issues
  
  5. IF (new_issue_count == previous_issue_count)
       → Done! Optimization complete
     ELSE
       → Continue to next iteration
}
```

### Step 3: Summarize Results
- Total iterations completed
- Total issues discovered and fixed
- Files modified
- Commits created
- Final code quality assessment

## Best Practices

1. **Large Projects**: May take multiple iterations (2-5 is typical)
2. **Keep Momentum**: Each iteration builds on the previous
3. **Review Commits**: Check `git log` to see all improvements
4. **Push When Ready**: After complete optimization, `git push origin`
5. **Test Integration**: Run project tests after completion

## Configuration

The skill automatically detects and adapts to:
- Project type (Python, JavaScript, Go, Java, etc.)
- Dependency managers (pip, npm, gradle, cargo, etc.)
- Code structure and patterns
- Existing issue documentation format

## Limitations

- Issues requiring architecture redesign may need human review
- External dependencies issues require manual investigation
- Infinite loops prevented by "no new issues" exit condition
- Complex refactoring may be split across iterations

## Success Criteria

Optimization is complete when:
- ✅ No new issues found in consecutive scans
- ✅ Code passes all available tests
- ✅ Documentation is up-to-date
- ✅ All discovered issues have been addressed

## Next Steps

After optimization completes:

1. **Review results**:
   ```bash
   git log --oneline | head -20  # See all commits
   ```

2. **Test the project**:
   ```bash
   npm test / pytest / go test
   ```

3. **Push to remote**:
   ```bash
   git push origin main
   ```

4. **Create PR** (optional):
   ```bash
   gh pr create --title "Optimize code and docs" --body "..."
   ```

---

## How to Use

Simply invoke the skill and let it run the complete optimization workflow:

```
/iterative-document-optimization
```

The skill will:
- 🔍 Analyze your project
- 🐛 Find all issues iteratively
- 🔧 Fix them automatically
- 📝 Create professional commits
- ✅ Repeat until optimization complete
- 📊 Provide final summary
