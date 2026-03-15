# Lessons Learned

This file tracks patterns, mistakes, and corrections to improve future performance.

## Patterns to Avoid
- **Using outdated model IDs without verifying**: Gemini 1.5 Flash was retired April 2025. Always check official docs for current model IDs before writing code. Use `models.list` API or docs pages.

## Patterns to Follow
- **Always research latest model availability** before hardcoding model IDs. Check official docs: ai.google.dev/gemini-api/docs/models and console.groq.com/docs/models
