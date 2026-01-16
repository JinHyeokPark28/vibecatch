# VibeCatch - Current Status

> Last updated: 2026-01-17

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

**Phase**: MVP 완료 + UX 개선
**Next Action**: 배포 준비

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
- [x] B002: /stats 페이지 - COMMITTED (a8cb89a)
- [x] GitHub → Dev.to, Product Hunt, TLDR 변경 - COMMITTED (0a14c76)
- [x] For You 탭 + 스마트 만료 - COMMITTED (a37a8ca)
- [x] **UX 대개편** - COMMITTED (9c10e02)
  - Magazine 레이아웃 (Featured + Grid)
  - Catchball 로딩 애니메이션 (랜덤 방향 등장)
  - 카드 클릭 → 요약 floating overlay
  - 다른 카드 dim/blur 효과
  - Featured 카드 요약 버그 수정
  - 수집량 100개 (HN 25 + Reddit 25 + DevTo 20 + PH 15 + TLDR 15)
  - Rate limit 3 → 10/일
  - PORT 환경변수 지원

---

## Next Tasks

1. [ ] 배포 준비

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
