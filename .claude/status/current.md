# VibeCatch - Current Status

> Last updated: 2026-01-16

---

## Project Info

| Key | Value |
|-----|-------|
| Project | VibeCatch |
| Type | Python/FastAPI API Server |
| Status | In Development |
| PRD | docs/PRD.md (v1.1 Approved) |

---

## Current State

**Phase**: F002 Handoff Complete
**Next Action**: /clear -> /verify -> commit

---

## Completed

- [x] /start onboarding
- [x] PRD review (v1.1 approved)
- [x] Project type detection (FastAPI + SQLite)
- [x] Architecture decision (Flat structure)
- [x] **F001 HN Collector** - COMMITTED (377ff84)
  - collectors/hackernews.py
  - database.py (init_db, save_items)
  - 7 tests passed
- [x] **F002 AI Summarizer** - Gate PASS
  - summarizer.py (Claude API)
  - database.py (update_item_summary, get_items_without_summary)
  - main.py (POST /collect)
  - 22 tests passed

---

## Next Tasks

1. [ ] /verify F002 (Context Bias-free)
2. [ ] Commit F002
3. [ ] /plan F003 (카드 리뷰 UI)

---

## MVP Progress

| ID | Feature | Status |
|----|---------|--------|
| F001 | 콘텐츠 수집 (HN) | ✅ Done |
| F002 | AI 요약 | ✅ Done |
| F003 | 카드 리뷰 UI | ⬜ Pending |
| F004 | 선호도 학습 | ⬜ Pending |
| F005 | 우선순위 정렬 | ⬜ Pending |

---

## Decision Log

| Date | Decision | Reason |
|------|----------|--------|
| 2026-01-16 | Python sorting for tags | ADR-001: MVP simplicity, <1000 items |
| 2026-01-16 | SQLite (not PostgreSQL) | Solo tool, file-based is enough |
| 2026-01-16 | Jinja2 (not React/Next) | Server-rendered, no SPA needed |
| 2026-01-16 | KNOWN_TAGS whitelist | 일관된 태그 체계, PRD 기반 |

---

## Blockers

None currently.

---

## Notes

- Estimated API cost: ~$22/month
- Refactoring trigger: 1000+ items -> normalize tags table
- ANTHROPIC_API_KEY 필수 (요약 기능)
