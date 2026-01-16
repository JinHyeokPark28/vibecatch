# VibeCatch - Current Plan

## Metadata

| Key | Value |
|-----|-------|
| Created | 2026-01-16 |
| Task | F001 HN 수집 기능 |
| Status | LOCKED |
| ToT Score | 90 |
| Judge Score | 94% |
| PRD Reference | F001 콘텐츠 수집 |

---

## Scope Definition (Locked)

### In Scope

- HN Top Stories 수집 (상위 30개)
- DB 저장 (items 테이블)
- 중복 체크 (source + external_id)
- 에러 처리 및 로깅
- 기본 테스트

### Out of Scope (BACKLOG)

- Reddit 수집 (별도 계획)
- GitHub 수집 (별도 계획)
- Claude 요약 (F002)
- 스케줄러 설정 (전체 통합 시)

---

## Step List

### Step 0: 프로젝트 기본 구조 생성 (30min)

**목표**: FastAPI 앱 뼈대 + DB 초기화

**작업 내용**:
1. `requirements.txt` 생성
   - fastapi, uvicorn, httpx, jinja2, python-multipart
   - apscheduler, anthropic, pytest, ruff
2. `main.py` 생성 (FastAPI 앱 초기화)
3. `database.py` 생성 (SQLite 연결 + 테이블 생성)
4. `.env.example` 생성
5. `collectors/__init__.py` 생성

**검증**:
```bash
python -c "import main; print('OK')"
python -c "from database import init_db; init_db(); print('OK')"
```

**파일 목록**:
- [ ] requirements.txt (신규)
- [ ] main.py (신규)
- [ ] database.py (신규)
- [ ] .env.example (신규)
- [ ] collectors/__init__.py (신규)

---

### Step 1: HN 수집기 구현 (45min)

**목표**: Hacker News Top Stories 수집 함수

**작업 내용**:
1. `collectors/hackernews.py` 생성
2. HN API 호출 함수 (`fetch_top_stories`)
   - Top stories ID 목록 가져오기
   - 상위 30개 item 상세 정보 가져오기
3. 데이터 정규화 (title, url, external_id)
4. 에러 처리 (try-except + 로깅)

**HN API Endpoints**:
```
Top Stories: https://hacker-news.firebaseio.com/v0/topstories.json
Item Detail: https://hacker-news.firebaseio.com/v0/item/{id}.json
```

**검증**:
```bash
python -c "from collectors.hackernews import fetch_top_stories; import asyncio; items = asyncio.run(fetch_top_stories()); print(f'Fetched {len(items)} items')"
```

**파일 목록**:
- [ ] collectors/hackernews.py (신규)

---

### Step 2: DB 저장 로직 구현 (30min)

**목표**: 수집된 아이템 DB 저장 (중복 체크)

**작업 내용**:
1. `database.py`에 `save_items()` 함수 추가
2. INSERT OR IGNORE로 중복 처리
3. 저장 결과 로깅 (신규/중복 개수)
4. `collectors/hackernews.py`에 저장 로직 연결

**검증**:
```bash
python -c "from collectors.hackernews import collect_and_save; import asyncio; result = asyncio.run(collect_and_save()); print(result)"
```

**파일 목록**:
- [ ] database.py (수정 - save_items 추가)
- [ ] collectors/hackernews.py (수정 - collect_and_save 추가)

---

### Step 3: 테스트 및 Gate 검증 (30min)

**목표**: 테스트 작성 + Gate PASS

**작업 내용**:
1. `tests/` 폴더 생성
2. `tests/test_hackernews.py` 작성
   - fetch_top_stories 테스트 (mock 사용)
   - save_items 테스트
3. `pytest.ini` 설정
4. ruff 린트 수정
5. Gate 실행

**테스트 케이스**:
- [ ] fetch_top_stories: 정상 응답 처리
- [ ] fetch_top_stories: 네트워크 에러 처리
- [ ] save_items: 신규 아이템 저장
- [ ] save_items: 중복 아이템 스킵

**검증**:
```bash
ruff check .
pytest tests/ -v
python -m py_compile main.py collectors/hackernews.py database.py
```

**파일 목록**:
- [ ] tests/__init__.py (신규)
- [ ] tests/test_hackernews.py (신규)
- [ ] pytest.ini (신규)

---

## Summary

| Step | Task | Time | Files |
|------|------|------|-------|
| 0 | 프로젝트 기본 구조 | 30min | 5 files |
| 1 | HN 수집기 구현 | 45min | 1 file |
| 2 | DB 저장 로직 | 30min | 2 files |
| 3 | 테스트 + Gate | 30min | 3 files |

**Total**: ~2h 15min (PRD 예상 4h의 절반 - HN만 구현)

---

## Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| HN API 일시 장애 | Low | Medium | 재시도 로직, 로깅 |
| 네트워크 타임아웃 | Medium | Low | timeout 설정 (10s) |
| Item 상세 요청 과다 | Low | Low | 30개 제한, 병렬 요청 |

---

## Scope Lock Hash

```
SHA256: f001-hn-collector-v1-2026-01-16
```

**This plan is LOCKED. No scope changes allowed.**

---

## Next Steps (After Completion)

1. `/implement` - 이 계획 실행
2. `/gate` - 검증
3. `/plan F002` - AI 요약 기능 계획

