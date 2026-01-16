# VibeCatch - Current Plan

## Metadata

| Key | Value |
|-----|-------|
| Created | 2026-01-16 |
| Task | F002 AI 요약 |
| Status | 🔒 LOCKED |
| ToT Score | 90 |
| Judge Score | 94% |
| PRD Reference | F002 Claude API로 제목+내용 요약 + 태그 추출 |

---

## Scope Definition (Locked)

### In Scope

- summarizer.py 생성 (Claude API 호출)
- 태그 추출 (ai, vibe-code, solo, saas, startup 등)
- database.py에 update_item_summary() 함수 추가
- /collect 라우트 구현 (수집 + 요약 통합)
- 테스트 작성

### Out of Scope (BACKLOG)

- Reddit 수집 (별도 계획)
- GitHub 수집 (별도 계획)
- 스케줄러 설정 (전체 통합 시)
- 카드 리뷰 UI (F003)

---

## Step List

### Step 1: summarizer.py 생성 (30min)

**목표**: Claude API를 사용한 요약 + 태그 추출

**작업 내용**:
1. `summarizer.py` 생성
2. `summarize_item(title, url)` 함수
   - Claude API 호출 (anthropic 패키지)
   - 프롬프트: 2-3문장 요약 + 태그 추출
   - 반환: `{summary: str, tags: list[str]}`
3. Rate limit 처리 (try-except)
4. 요약 실패 시 원본 제목 유지 (ALWAYS 규칙)

**검증**:
```bash
python -m py_compile summarizer.py
```

**파일 목록**:
- [ ] summarizer.py (신규)

---

### Step 2: database.py update 함수 추가 (15min)

**목표**: 요약 결과 DB 저장

**작업 내용**:
1. `update_item_summary(item_id, summary, tags)` 함수 추가
2. summary, tags 컬럼 업데이트

**검증**:
```bash
pytest tests/test_database.py -v
```

**파일 목록**:
- [ ] database.py (수정)
- [ ] tests/test_database.py (신규)

---

### Step 3: summarize_new_items 배치 함수 (20min)

**목표**: 미요약 아이템 일괄 처리

**작업 내용**:
1. `summarize_new_items(limit=10)` 함수
   - summary IS NULL인 아이템 조회
   - 각각 summarize_item() 호출
   - DB 업데이트
2. 결과 반환: `{total, summarized, failed}`

**검증**:
```bash
python -c "from summarizer import summarize_new_items; import asyncio; print(asyncio.run(summarize_new_items(1)))"
```

**파일 목록**:
- [ ] summarizer.py (수정)

---

### Step 4: /collect 라우트 구현 (20min)

**목표**: 수집 + 요약 통합 엔드포인트

**작업 내용**:
1. `main.py`에 POST /collect 라우트 추가
2. collect_and_save() 호출 (HN 수집)
3. summarize_new_items() 호출
4. 결과 반환: `{collected, summarized}`

**검증**:
```bash
curl -X POST http://localhost:8000/collect
```

**파일 목록**:
- [ ] main.py (수정)

---

### Step 5: 테스트 작성 (20min)

**목표**: 요약 기능 테스트

**작업 내용**:
1. `tests/test_summarizer.py` 생성
2. Mock Claude API 응답
3. 태그 추출 검증
4. 에러 핸들링 검증

**테스트 케이스**:
- [ ] summarize_item: 정상 응답
- [ ] summarize_item: API 에러 시 None 반환
- [ ] update_item_summary: DB 업데이트
- [ ] summarize_new_items: 배치 처리

**검증**:
```bash
pytest tests/test_summarizer.py -v
```

**파일 목록**:
- [ ] tests/test_summarizer.py (신규)

---

### Step 6: Gate 검증 (10min)

**목표**: 전체 검증 + EVIDENCE.md

**검증**:
```bash
ruff check .
pytest tests/ -v
python -m py_compile main.py summarizer.py database.py
```

---

## Summary

| Step | Task | Time | Files |
|------|------|------|-------|
| 1 | summarizer.py 생성 | 30min | 1 file |
| 2 | database.py update 함수 | 15min | 2 files |
| 3 | summarize_new_items | 20min | 1 file |
| 4 | /collect 라우트 | 20min | 1 file |
| 5 | 테스트 작성 | 20min | 1 file |
| 6 | Gate 검증 | 10min | - |

**Total**: ~2h (PRD 예상 2h)

---

## Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Claude API Rate Limit | Medium | Medium | try-except, 재시도 로직 |
| 태그 추출 부정확 | Medium | Low | 프롬프트 튜닝, 빈 배열 fallback |
| API 키 누락 | Low | High | .env.example 문서화 |

---

## Scope Lock Hash

```
SHA256: f002-ai-summarizer-v1-2026-01-16
```

**This plan is LOCKED. No scope changes allowed.**

---

## ALWAYS Rules (F002)

- ALWAYS 요약 실패 시 원본 제목 유지
- ALWAYS 태그 추출 실패 시 빈 배열 [] 반환
- ALWAYS Claude API 호출 시 try-except 처리
- ALWAYS Rate limit 고려 (limit 파라미터)

