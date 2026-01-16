# VibeCatch Progress

> 현재 프로젝트 상태 추적

---

## 현재 상태: 배포 준비 완료

**마지막 업데이트:** 2026-01-16

---

## 완료된 작업

### MVP 기능 (F001-F005)

| ID | 기능 | 상태 |
|----|------|------|
| F001 | HN Collector | ✅ 완료 |
| F002 | AI Summarizer | ✅ 완료 |
| F003 | Card Review UI | ✅ 완료 |
| F004 | Preference Learning | ✅ 완료 |
| F005 | Priority Sorting | ✅ 완료 |

### 추가 기능

| 기능 | 상태 |
|------|------|
| Reddit Collector | ✅ 완료 |
| GitHub Collector | ✅ 완료 |
| Stats Page | ✅ 완료 |
| Auto Scheduler | ✅ 완료 |

### 배포 준비

| 항목 | 상태 |
|------|------|
| Dockerfile | ✅ 완료 |
| README.md | ✅ 완료 |
| EVIDENCE.md | ✅ Gate PASS |
| .env.example | ✅ 완료 |

### 리팩토링 (2026-01-16)

| 항목 | 상태 |
|------|------|
| utils.py (parse_tags_json) | ✅ 완료 |
| collectors/base.py | ✅ 완료 |
| Collector 클래스 구조 | ✅ 완료 |
| main.py 중복 제거 | ✅ 완료 |

---

## 남은 작업

- [ ] 리팩토링 검증 (/verify)
- [ ] 최종 커밋

---

## Gate 결과 (최신)

```
Lint:   ✅ PASS (ruff check)
Test:   ✅ 64 passed (12.70s)
Syntax: ✅ PASS
```

---

## 알려진 이슈

없음

---

## 파일 구조

```
vibecatch/
├── main.py              # FastAPI 앱
├── database.py          # SQLite DB
├── summarizer.py        # Claude API
├── utils.py             # 🆕 공통 유틸리티
├── collectors/
│   ├── __init__.py
│   ├── base.py          # 🆕 BaseCollector
│   ├── hackernews.py    # ♻️ 리팩토링
│   ├── reddit.py        # ♻️ 리팩토링
│   └── github.py        # ♻️ 리팩토링
├── templates/
│   ├── index.html
│   ├── liked.html
│   └── stats.html
├── static/
│   └── style.css
├── tests/
│   └── test_*.py
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── EVIDENCE.md
└── PROGRESS.md          # 이 파일
```
