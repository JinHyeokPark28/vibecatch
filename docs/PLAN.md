# VibeCatch v2.0 - 공개 배포 계획

## Metadata

| Key | Value |
|-----|-------|
| Created | 2026-01-16 |
| Task | v2.0 공개 배포 (F010, F011, F012) |
| Status | ✅ COMPLETED |
| PRD Reference | PRD v2.0 |

---

## Scope Definition (Locked)

### In Scope

- F010: UUID 시스템 (유저별 데이터 분리)
- F011: Rate Limit (API 남용 방지)
- F012: UI 개선 (후순위, 이번 플랜 제외)

### Out of Scope (v3.0)

- F020: 로그인 연동
- F021-24: 후원 시스템, 프리미엄 기능

---

## 마이그레이션 전략

### 기존 → 신규 스키마

```
[기존]                    [신규]
items (status 포함)  →    items (status 제거, 공유)
                          user_items (유저별 상태)
preferences (글로벌) →    preferences (유저별)
                          users (신규)
                          rate_limits (신규)
```

### 기존 데이터 처리

1. 기존 items 데이터 → 유지 (공유 콘텐츠)
2. 기존 status/reviewed_at → 첫 유저(본인) user_items로 이동
3. 기존 preferences → 첫 유저 preferences로 이동

---

## Step List

### Step 1: DB 스키마 마이그레이션 (45min)

**목표**: v2.0 스키마로 전환

**작업 내용**:
1. `database.py` 수정
   - `init_db()`에 새 테이블 추가
   - 마이그레이션 로직 (기존 데이터 보존)

**신규 테이블**:
```sql
-- users
CREATE TABLE users (
    uuid TEXT PRIMARY KEY,
    email TEXT,
    tier TEXT DEFAULT 'free',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen_at DATETIME
);

-- user_items (유저별 아이템 상태)
CREATE TABLE user_items (
    user_uuid TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    status TEXT DEFAULT 'new',
    reviewed_at DATETIME,
    PRIMARY KEY (user_uuid, item_id)
);

-- rate_limits
CREATE TABLE rate_limits (
    user_uuid TEXT NOT NULL,
    date TEXT NOT NULL,
    collect_count INTEGER DEFAULT 0,
    PRIMARY KEY (user_uuid, date)
);
```

**마이그레이션 순서**:
1. 새 테이블 생성
2. items에서 status, reviewed_at 컬럼 유지 (하위호환)
3. preferences에 user_uuid 컬럼 추가 (기본값 'legacy')

**검증**:
```bash
python -c "from database import init_db; init_db()"
sqlite3 vibecatch.db ".schema"
```

**파일**:
- [x] database.py (수정)

---

### Step 2: UUID 미들웨어 구현 (30min)

**목표**: 모든 요청에서 유저 식별

**작업 내용**:
1. `main.py`에 미들웨어 추가
2. 쿠키에서 user_uuid 읽기/생성
3. `get_or_create_user(uuid)` 함수
4. Request.state에 user_uuid 저장

**로직**:
```python
@app.middleware("http")
async def user_middleware(request, call_next):
    user_uuid = request.cookies.get("user_uuid")
    if not user_uuid:
        user_uuid = str(uuid4())
        # DB에 저장
    request.state.user_uuid = user_uuid
    response = await call_next(request)
    response.set_cookie("user_uuid", user_uuid, max_age=31536000)
    return response
```

**검증**:
```bash
curl -v http://localhost:8000/ | grep Set-Cookie
```

**파일**:
- [x] main.py (수정)
- [x] database.py (수정 - get_or_create_user)

---

### Step 3: 유저별 데이터 조회 함수 (30min)

**목표**: 모든 조회를 유저별로 분리

**작업 내용**:
1. `get_user_items(user_uuid, status)` - 유저별 아이템
2. `get_user_preferences(user_uuid)` - 유저별 선호도
3. `review_item_for_user(user_uuid, item_id, action)` - 유저별 리뷰
4. `sync_new_items_for_user(user_uuid)` - 신규 아이템 동기화

**검증**:
```bash
pytest tests/test_database.py -v
```

**파일**:
- [x] database.py (수정)

---

### Step 4: API 엔드포인트 UUID 적용 (30min)

**목표**: 모든 API에서 user_uuid 사용

**작업 내용**:
1. `GET /` - user_uuid로 아이템 조회
2. `POST /review/{id}` - user_uuid로 리뷰
3. `GET /liked` - user_uuid로 조회
4. `GET /stats` - user_uuid로 통계

**검증**:
```bash
pytest tests/test_main.py -v
```

**파일**:
- [x] main.py (수정)

---

### Step 5: Rate Limit 구현 (30min)

**목표**: API 남용 방지

**작업 내용**:
1. `check_rate_limit(user_uuid, action)` 함수
2. `increment_rate_limit(user_uuid, action)` 함수
3. `/collect`에 Rate Limit 적용
4. 429 응답 처리

**정책**:
| Tier | 일일 수집 |
|------|----------|
| Free | 3회 |
| Supporter | 무제한 |

**검증**:
```bash
# 4번째 호출 시 429
for i in {1..4}; do curl -X POST http://localhost:8000/collect; done
```

**파일**:
- [x] database.py (수정)
- [x] main.py (수정)

---

### Step 6: 테스트 업데이트 (30min)

**목표**: 모든 테스트를 v2.0에 맞게 수정

**작업 내용**:
1. 테스트용 user_uuid fixture 추가
2. 기존 테스트 수정 (UUID 파라미터 추가)
3. Rate Limit 테스트 추가
4. 마이그레이션 테스트

**검증**:
```bash
pytest tests/ -v
```

**파일**:
- [x] tests/test_database.py (수정)
- [x] tests/test_main.py (수정)

---

### Step 7: Gate 검증 (10min)

**목표**: 전체 검증 + 배포

**검증**:
```bash
ruff check .
pytest tests/ -v
python -m py_compile main.py database.py
```

**배포**:
```bash
git add -A
git commit -m "feat: v2.0 UUID system + Rate Limit"
git push
```

---

## Summary

| Step | Task | Time |
|------|------|------|
| 1 | DB 스키마 마이그레이션 | 45min |
| 2 | UUID 미들웨어 | 30min |
| 3 | 유저별 데이터 조회 | 30min |
| 4 | API UUID 적용 | 30min |
| 5 | Rate Limit | 30min |
| 6 | 테스트 업데이트 | 30min |
| 7 | Gate 검증 | 10min |

**Total**: ~3.5h

---

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| 기존 데이터 손실 | High | 마이그레이션 시 백업, 롤백 가능 |
| 쿠키 차단 | Medium | localStorage 폴백 (v2.1) |
| Rate Limit 우회 | Low | IP 기반 추가 제한 (v2.1) |

---

## ALWAYS Rules (v2.0)

- ALWAYS 모든 요청에서 user_uuid 확인
- ALWAYS 쿠키 없으면 새 UUID 생성
- ALWAYS Rate Limit 초과 시 429 반환
- ALWAYS 기존 데이터 마이그레이션 보존

---

## Scope Lock

**This plan is LOCKED. No scope changes allowed.**

F012 (UI 개선)은 v2.0 완료 후 별도 플랜으로 진행.
