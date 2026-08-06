# Case Study

## Problem

The workflow starts with product copy and ends when localized strings are ready for engineering consumption. In the original process, several steps depended on manual checks:

- missing or inconsistent string keys
- placeholder preservation across languages
- terminology consistency
- length limits for compact UI surfaces
- post-generation formatting before delivery

The public version describes the method without exposing real company systems, project names, raw data or production records.

## Approach

I treated the workflow as an AI-assisted delivery system rather than a single translation prompt.

1. Build a baseline map of where delays and quality failures occur.
2. Split the system into Planner, Act Workers, Evaluation Gate and Delivery Adapter.
3. Put deterministic validation before model-based judging.
4. Create a golden set with edge cases instead of testing only average copy.
5. Feed badcases back into glossary, prompts and regression tests.

## What Is Demonstrated Here

This repository contains:

- architecture diagrams that show the system boundary and feedback loop
- an anonymized request format
- a small Python demo for request planning and rule validation
- tests for placeholder and key-format validation

This repository does not contain:

- real internal platform integrations
- production data
- private documents
- project-specific interview materials
- credentials, URLs, request schemas or screenshots

## Lessons

The most valuable design choice was to separate deterministic risk from generative quality. Placeholder loss, illegal key names and over-length strings should not wait for human review or LLM judging. They should fail fast with precise feedback. The LLM judge is then reserved for accuracy, fluency and brand consistency, where deterministic rules are not enough.
