---
description: Implement a feature from BACKLOG.md
---

Implement a feature from `BACKLOG.md`. User input: $ARGUMENTS

## Instructions

### Step 1: Identify the Feature

1. Read `BACKLOG.md` to get the list of pending features
2. Based on the user input:
   - **If no input provided**: List all pending features (unchecked items) and ask the user to specify which feature number (e.g., FEAT-0001) they want to implement
   - **If a feature number provided** (e.g., "FEAT-0001" or "0001"): Find that exact feature
   - **If a feature name/description provided**: Find the best matching feature, show it to the user, and ask them to confirm this is the correct feature before proceeding

### Step 2: Clarify Requirements

Before planning, ask clarifying questions to ensure you understand the feature completely:

1. Read any existing code related to the feature area
2. Identify ambiguities or implementation choices that need user input
3. Use the AskUserQuestion tool to gather:
   - Any unclear requirements
   - User preferences on implementation approach
   - Scope boundaries (what's in/out of this feature)
   - Any specific UI/UX preferences if applicable

Do NOT proceed to planning until you have enough information to implement the feature correctly.

### Step 3: Create Implementation Plan

1. Use EnterPlanMode to create a detailed implementation plan
2. The plan should include:
   - Files to modify or create
   - Key changes in each file
   - Order of implementation
   - Any database migrations needed
   - Frontend changes if applicable
3. Get user approval on the plan before proceeding

### Step 4: Create Feature Branch

Once the plan is approved, output (but do NOT run) the command to create a feature branch:

```bash
git checkout -b feature/FEAT-XXXX-short-description
```

Example: `git checkout -b feature/FEAT-0001-full-article-retrieval`

Let the user run the command themselves. Wait for confirmation before proceeding to implementation.

### Step 5: Implement the Feature

1. Follow the approved plan
2. Use TodoWrite to track progress through implementation steps
3. After completing implementation, update documentation:
   - Run `/update-docs` to update CLAUDE.md and README.md with any relevant changes

### Step 6: Review and Submit

1. **Local testing**: Ask the user to test the feature by running the app locally (`python main.py`)
2. **Distribution testing**: Ask the user to build and test the standalone app:
   ```bash
   python scripts/build_app.py
   ```
   Then test the DMG/app from `dist/` folder
3. **Once review is accepted**: Output (but do NOT run) the following commands:

   **Commit command** - Output a bash command to commit all changes:
   ```bash
   git add -A && git commit -m "$(cat <<'EOF'
   [FEAT-XXXX] Feature title

   Summary of changes...

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
   EOF
   )"
   ```

   **Pull request command** - Output a bash command to create a PR:
   ```bash
   git push -u origin feature/FEAT-XXXX-short-description && gh pr create --title "[FEAT-XXXX] Feature title" --body "$(cat <<'EOF'
   ## Summary
   - Bullet points of changes

   ## Test plan
   - [ ] Test steps

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

4. Let the user run the commands themselves to save tokens

### Step 7: Update BACKLOG.md

After the PR is created:

1. Move the feature from its current section to the **Completed** section
2. Change the checkbox from `- [ ]` to `- [x]`
3. Keep the feature ID and description intact

Example:
```markdown
## Completed

- [x] **[FEAT-0003] Thumbs up/down rating** - Allow users to rate articles with thumbs up or down
```

## Example Interactions

**No input:**
```
User: /implement-feature
Assistant: Here are the pending features in BACKLOG.md:

High Priority:
- FEAT-0001: Full article retrieval

Medium Priority:
- FEAT-0002: Notes & highlights
- FEAT-0003: Thumbs up/down rating
- FEAT-0004: Search
- FEAT-0005: Auto-refresh on startup

Which feature would you like to implement? Please provide the feature number (e.g., FEAT-0001).
```

**Feature name provided:**
```
User: /implement-feature search
Assistant: I found a matching feature:

**[FEAT-0004] Search** - Allow users to search for keywords within article titles and body content

Is this the feature you want to implement? (yes/no)
```

**Feature number provided:**
```
User: /implement-feature FEAT-0001
Assistant: I'll implement **[FEAT-0001] Full article retrieval** - Fetch complete article content from the source URL instead of just the RSS snippet.

Let me ask a few clarifying questions before we plan the implementation...
```