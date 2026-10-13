# Architecture Decision Records

One decision per file: `NNNN-short-title.md`, with three sections: **Context**, **Decision** and **Consequences**.

| ADR | Decision | Status |
|---|---|---|
| 0001 | Session state: in-memory vs DynamoDB (Day 5) | Pending |
| 0002 | Keep the LLM out of the recommendation hot path (Day 6) | Pending |
| 0003 | moto + Lambda RIE + Ollama instead of LocalStack for local development | Pending |
| 0004 | Lambda zip package from S3 instead of a container image | Pending |

## Template

```markdown
# NNNN. Title

- Status: proposed | accepted | superseded by NNNN
- Date: YYYY-MM-DD

## Context
What problem are we solving? What constraints and forces are at play?

## Decision
What we decided, stated plainly.

## Consequences
What gets easier, what gets harder, and what we must watch.
```
