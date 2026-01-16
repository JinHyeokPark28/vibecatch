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

**Phase**: MVP 완료
**Next Action**: 추가 기능 또는 배포 준비

---

## Completed

- [x] /start onboarding
- [x] PRD review (v1.1 approved)
- [x] Project type detection (FastAPI + SQLite)
- [x] Architecture decision (Flat structure)
- [x] **F001 HN Collector** - COMMITTED (377ff84)
- [x] **F002 AI Summarizer** - COMMITTED (238656b)
- [x] **F003 Card Review UI** - COMMITTED (fb3ef77, afb8622, ab81ec7)
- [x] **F004 Preference Learning** - COMMITTED (fb3ef77)
- [x] **F005 Priority Sorting** - COMMITTED (c910eef)
- [x] **Reddit Collector** - COMMITTED (63a588e)
- [x] **/liked 페이지** - COMMITTED (274e21e)

---

## Next Tasks

1. [x] B002: /stats 페이지 - COMMITTED (a8cb89a)
2. [x] GitHub Collector - COMMITTED (aa1dc3a)
3. [ ] 배포 준비

---

## MVP Progress

| ID | Feature | Status |
|----|---------|--------|
| F001 | 콘텐츠 수집 (HN/Reddit) | ✅ Done |
| F002 | AI 요약 | ✅ Done |
| F003 | 카드 리뷰 UI | ✅ Done |
| F004 | 선호도 학습 | ✅ Done |
| F005 | 우선순위 정렬 | ✅ Done |

**MVP 완료!** 모든 핵심 기능 구현됨.

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
