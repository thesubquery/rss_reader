---
description: Add a new feature to BACKLOG.md with a unique tracking ID
---

Add a new feature to `BACKLOG.md` based on the user's description: $ARGUMENTS

## Instructions

1. Read the current `BACKLOG.md` file
2. Generate a unique feature ID in the format `FEAT-XXXX` where XXXX is a 4-digit number
   - Scan existing features in BACKLOG.md to find the highest existing FEAT-XXXX number
   - Increment by 1 for the new feature
   - If no existing FEAT IDs, start with FEAT-0001
3. Add the new feature to the **Medium Priority** section (unless the user specifies otherwise)
4. Format the entry as:
   ```
   - [ ] **[FEAT-XXXX] Feature title** - Feature description
   ```
5. Show the user the added feature with its ID

## Example

Input: `keyboard shortcuts for navigation`

Output added to BACKLOG.md:
```
- [ ] **[FEAT-0005] Keyboard shortcuts** - Add keyboard shortcuts for navigation
```

Then tell the user:
"Added feature **FEAT-0005** to BACKLOG.md. Use this ID in commit messages and PR descriptions to track this feature."
