# Iterative Document & Code Optimization Skill

Automate continuous improvement of your project through iterative cycles of issue discovery and resolution.

## Overview

This skill combines two powerful workflows:
1. **Code Auditing** - Discovers issues in code, documentation, and structure
2. **Issue Resolution** - Automatically fixes all discovered issues

It repeats this cycle until no new issues are found, ensuring comprehensive project optimization.

## Features

✅ **Automatic Issue Discovery** - Uses code audit to find bugs, improvements, and refactoring opportunities
✅ **Automatic Issue Resolution** - Fixes discovered issues with proper commits
✅ **Iterative Improvement** - Repeats until reaching a stable state (no new issues)
✅ **Multi-Language Support** - Works with Python, JavaScript, Go, Java, Rust, etc.
✅ **Atomic Commits** - Each fix creates a clean, reviewable commit
✅ **Documentation Sync** - Keeps README and docs up-to-date with code
✅ **Progress Tracking** - Shows iteration progress and statistics

## Installation

Copy to your Claude Code skills directory:
```bash
cp -r iterative-document-optimization ~/.claude/skills/
```

## Quick Start

1. Navigate to your project:
```bash
cd /path/to/your/project
```

2. Invoke the skill:
```
/iterative-document-optimization
```

3. Watch as the skill:
   - Analyzes your project
   - Discovers issues
   - Fixes them automatically
   - Repeats until optimization complete

## How It Works

### The Optimization Cycle

```
┌─────────────────────────────────┐
│  Iteration N                    │
│  ┌─────────────────────────────┤
│  │ 1. Code Audit               │
│  │    (find issues)            │
│  │                             │
│  │ 2. Record issue count       │
│  │                             │
│  │ 3. Issue Resolution         │
│  │    (fix issues)             │
│  │                             │
│  │ 4. Code Audit again         │
│  │    (check for new issues)   │
│  │                             │
│  │ 5. Compare counts           │
│  │    Same? → DONE ✅          │
│  │    Different? → Continue    │
│  └─────────────────────────────┘
└─────────────────────────────────┘
```

### Example Output

```
🔍 PROJECT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project: AI Trends Dashboard
Type: Python (Flask/FastAPI)
Language: Python 3.8+
Framework: Click CLI

🔍 ITERATION 1: AUDIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Issues Found: 7
  - 2 Security vulnerabilities
  - 2 Code quality issues
  - 2 Documentation gaps
  - 1 Performance issue

🔧 RESOLVING 7 ISSUES...
✅ Fixed SQL injection vulnerability
✅ Added input validation
✅ Updated README with examples
✅ Optimized query performance
...

📦 Created 7 commits

🔍 ITERATION 2: AUDIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Issues Found: 3 (down from 7!)
  - 1 Test coverage issue
  - 1 Documentation
  - 1 Code style

🔧 RESOLVING 3 ISSUES...
✅ Added missing tests
✅ Updated API docs
✅ Fixed linting issues

📦 Created 3 commits

🔍 ITERATION 3: AUDIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Issues Found: 3 (No new issues!)
✅ Optimization Complete!

📈 RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Iterations: 3
Total Issues Fixed: 13
Total Commits: 13
Code Quality: ⬆️ Significantly Improved
Status: Ready for Production ✅
```

## Requirements

This skill requires:
- **Git repository** initialized
- **code-audit-and-github-issues skill** installed
- **issue-resolution-workflow skill** installed
- **Project files** to analyze (README.md, source code, etc.)

## Typical Iteration Counts

| Project Type | Size | Typical Iterations |
|---|---|---|
| New small project | < 1000 LOC | 1-2 |
| Medium project | 1000-10k LOC | 2-3 |
| Large codebase | 10k-100k LOC | 3-5 |
| Legacy project | 100k+ LOC | 4-8 |

## What Gets Fixed

Each iteration may address:

**Code Quality**
- Unused variables
- Dead code
- Code smells
- Refactoring opportunities

**Security**
- SQL injection vulnerabilities
- XSS attacks
- Insecure dependencies
- Missing validation

**Documentation**
- Outdated README
- Missing API docs
- Incomplete examples
- Typos and grammar

**Performance**
- Inefficient queries
- N+1 problems
- Memory leaks
- Slow algorithms

**Testing**
- Missing test cases
- Low coverage
- Failing tests
- Flaky tests

## Configuration

No configuration needed! The skill automatically:
- Detects project type
- Identifies code patterns
- Finds appropriate fixes
- Adapts to project structure

## Tips for Best Results

1. **Start with clean repo**: Commit or stash changes before running
2. **Have tests ready**: Run tests after optimization to verify
3. **Check git log**: Review commits created during optimization
4. **Review large changes**: Examine significant refactoring
5. **Push incrementally**: Push each iteration to see changes

## Troubleshooting

**Issue: Optimization never ends**
- The skill has protection against infinite loops
- If it continues past 5 iterations, review the ISSUES.md
- Manual review may be needed for complex patterns

**Issue: Some issues not fixed**
- Some architectural issues require human review
- Check the final ISSUES.md for unresolved items
- Fix manually or provide more context

**Issue: Want to stop early?**
- You can interrupt the skill anytime
- Current changes are already committed
- Re-run the skill later to continue optimization

## After Optimization

```bash
# 1. Review what changed
git log --oneline | head -20

# 2. Run tests to verify
pytest / npm test / go test

# 3. Push to remote
git push origin main

# 4. Create PR (optional)
gh pr create --title "Optimize code and documentation"
```

## Examples

### Example 1: Python Project
```
Project: Flask REST API
Starting issues: 12
After iteration 1: 5 issues fixed
After iteration 2: 3 issues fixed
After iteration 3: 0 new issues found
Total time: ~15 minutes
Result: 8 commits, significantly improved code
```

### Example 2: Node.js Project
```
Project: React + Express app
Starting issues: 8
After iteration 1: 4 issues fixed
After iteration 2: 2 issues fixed
After iteration 3: 1 issue fixed
After iteration 4: 0 new issues found
Total time: ~20 minutes
Result: 7 commits, modernized codebase
```

## Learning from Results

Each iteration teaches you about your codebase:
- What patterns are common
- What quality issues exist
- What documentation is missing
- What security gaps remain

Use this knowledge to:
- Train team on best practices
- Update code guidelines
- Improve review process
- Prevent future issues

## Support

For issues with the skill:
1. Check ISSUES.md for details on what was found
2. Review commits in git log
3. Check for error messages in skill output
4. Ensure both dependent skills are installed
