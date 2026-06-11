# Issue Resolution Workflow Skill

This skill automates the complete process of resolving documented issues in any project.

## Installation

Copy this directory to your Claude Code skills folder:
```bash
cp -r issue-resolution-workflow ~/.claude/skills/
```

## Quick Start

1. Ensure your project has an `ISSUES.md` file with documented issues
2. Run the skill from your project directory
3. The skill will:
   - Parse all issues
   - Fix them in priority order
   - Create commits automatically

## Supported Projects

- **Languages**: Python, JavaScript, TypeScript, Go, Java, Rust, C++, etc.
- **Frameworks**: Django, Flask, React, Vue, Express, Spring, etc.
- **Any project** with:
  - Git repository
  - Issue documentation (ISSUES.md, TODO.md, etc.)
  - Source code to fix

## Issue File Format

Create an `ISSUES.md` file in your project root:

```markdown
# Issues

## Issue 1: Bug title

**Type:** Bug 🐛
**Priority:** 🔴 High / 🟡 Medium / 🟢 Low

### Problem
Description of the bug or issue.

### Location
- file.py, line 42
- class SomeClass, method someMethod()

### Solution
How to fix it.

---

## Issue 2: Another issue

...
```

## How It Works

### Phase 1: Discovery
- Scans project root for issue files (ISSUES.md, TODO.md, BUGS.md)
- Reads and parses the issue document
- Extracts issue metadata (type, priority, status)

### Phase 2: Analysis
- Identifies affected code files
- Understands the problem context
- Determines if issue is already resolved

### Phase 3: Resolution
- Reads the problem description
- Locates and opens affected files
- Implements the fix
- Tests changes if applicable

### Phase 4: Commit
- Generates a descriptive commit message
- Creates an atomic commit with all related changes
- References the issue being fixed

## Features

✅ **Automatic code fixes** - Directly modifies source code
✅ **Smart prioritization** - High priority issues first
✅ **Professional commits** - Follows conventional commits format
✅ **Multi-language support** - Works with any programming language
✅ **Batch operations** - Can process multiple issues
✅ **Issue tracking** - Marks resolved issues in documentation

## Example

**Input ISSUES.md:**
```markdown
## XSS Vulnerability

**Type:** Bug 🐛
**Priority:** 🔴 High

### Problem
HTML content not escaped in template rendering.

### Location
- template.py, line 45-50

### Solution
Use html.escape() on all user input before rendering.
```

**Output:**
- Code is automatically fixed
- Commit: `fix: Escape HTML content to prevent XSS vulnerabilities`
- ISSUES.md updated with ✅ status

## Configuration

No configuration needed! The skill automatically detects:
- Project structure
- Programming language
- Issue file location
- Git repository info

## Tips for Best Results

1. **Be specific in descriptions** - Include file names, line numbers, function names
2. **Provide solution hints** - The skill will follow your recommendations
3. **Group related issues** - Can be fixed in one commit
4. **Update status** - Mark issues as ✅ DONE or 🚧 IN PROGRESS

## Limitations

- Issues requiring major architectural changes may need human review
- Complex refactoring might be split across multiple commits
- External API integrations may need manual setup
- Large codebase analysis may take time

## Support

For issues with the skill itself, check:
- Issue file format matches the examples
- Git repository is properly initialized
- File paths in issues exist in your project
