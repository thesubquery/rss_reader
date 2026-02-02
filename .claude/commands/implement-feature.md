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

1. **Check for existing plan**: Search in `.claude/plans/` directory for a file matching the feature number (e.g., `FEAT-0001-*.md`)
   - **If a plan exists**: Read it and use it as the starting point. Ask the user if they want to proceed with this plan or modify it.
   - **If no plan exists**: Continue to create a new plan.

2. Use EnterPlanMode to create a detailed implementation plan. The plan should include:
   - Files to modify or create
   - Key changes in each file
   - Order of implementation
   - Any database migrations needed
   - Frontend changes if applicable

3. **Save the plan**: Once the plan is finalized, save it to `.claude/plans/` with the filename format:
   ```
   FEAT-XXXX-feature-name.md
   ```
   Example: `FEAT-0001-full-article-retrieval.md`

   The plan file should include:
   - Feature ID and title
   - Original feature description from BACKLOG.md
   - Clarified requirements from Step 2
   - The complete implementation plan
   - Any notes or decisions made during planning

4. Get user approval on the plan before proceeding

### Step 4: Create Feature Branch

Once the plan is approved:

1. Ensure git working directory is clean (warn user if there are uncommitted changes)
2. Create a new branch from main with the naming convention:
   ```
   feature/FEAT-XXXX-short-description
   ```
   Example: `feature/FEAT-0001-full-article-retrieval`
3. Confirm branch creation to the user

### Step 5: Implement the Feature

1. Follow the approved plan
2. Use TodoWrite to track progress through implementation steps
3. Make atomic commits with messages referencing the feature ID:
   ```
   [FEAT-XXXX] Commit message describing the change
   ```
4. After completing implementation, remind the user to:
   - Test the feature
   - Update BACKLOG.md to mark the feature as completed (move to Completed section)
   - Create a PR when ready

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