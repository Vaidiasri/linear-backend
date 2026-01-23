---
description: Pro-level review of recent features/changes with a strict focus on reducing complexity to 1.
---

# Pro Feature Review & Complexity Reduction

This workflow evaluates recent work for architectural elegance and strict simplicity.

## Step 1: Context & Scope

Identify the recently modified files and the feature goal.

- What was the user's intent?
- Which files were touched?

## Step 2: "Complexity 1" Analysis

Target: **Cyclomatic Complexity ~ 1**.
Scan the code for:

- `if/else` nesting (Depth > 1 is bad).
- Loops inside loops.
- Complex boolean logic in a single line.

**Goal**: Every function should ideally read like a flat list of instructions (Linear flow).

- Use **Early Returns** (Guard Clauses) to eliminate `else`.
- Extract complex conditions into variable names or helper functions.
- Flatten list comprehensions if they get readable but complex.

## Step 3: Pro Dev Standards

- **Naming**: Is it self-documenting? (e.g., `is_active` vs `check`).
- **Data Flow**: Is mutation avoided?
- **DB**: Are we doing in Python what SQL could do faster? (e.g., aggregations).
- **Security**: Are inputs trusted blindly?

## Step 4: Refactoring Suggestions

Provide concrete refactoring steps to achieve Complexity 1.

- Show "Before" vs "After".
- Explain _why_ the simplified version is better (maintenance, reasoning).
