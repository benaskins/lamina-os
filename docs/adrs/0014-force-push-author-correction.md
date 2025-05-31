# ADR-0014: Retrospective - Force Push for Author Email Correction

**Status:** ACCEPTED  
**Date:** 2025-01-31  
**Type:** Retrospective  
**Authors:** Luthier  
**Authorized By:** Ben Askins  

## Context

Git history contained commits with author email `baskins@squareup.com` from work-related git configuration. This created inappropriate attribution linking personal open-source contributions to employer email.

## Decision

Executed authorized force push to rewrite git history, changing all instances of `baskins@squareup.com` to `ben.askins@gmail.com`.

## Implementation

1. Created backup branch before rewriting
2. Used `git filter-branch` to correct author emails
3. Force pushed to main and feature branches with explicit authorization
4. Cleaned up temporary branches

## Consequences

- **Positive:** Clear separation between personal and work contributions
- **Positive:** Proper attribution for open-source work
- **Negative:** One-time history rewrite requiring downstream users to re-clone

## Authorization

This force push was explicitly authorized by repository owner Ben Askins on 2025-01-31 to correct attribution issues.

---

*Documented retrospectively by Luthier*