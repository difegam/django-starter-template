---
description: This file describes the tooling and verification rules for the project.
applyTo: '**'
excludeAgent: 'code-review'
---

# Tooling and Verification Rules

Use these tools when generating, validating, or reviewing implementation steps.

## Documentation lookup

- When asked for setup instructions, API usage, or library behavior, use Context7 before relying on memory.
- Prefer official documentation and primary sources.

## Search engine usage

- When documentation lookup is insufficient, use search engines to find relevant information.

## Browser verification

- Validate user-facing behavior using browser automation (Playwright MCP or equivalent).
- Check console errors and network failures during verification.
- Confirm implemented behavior in the actual rendered UI, not only through static inspection.

## Validation mindset

- Favor reproducible command sequences.
- Record assumptions and unknowns explicitly when verification is incomplete.
