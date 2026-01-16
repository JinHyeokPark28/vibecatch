# VibeCatch PRD

## 메타 정보
- **버전:** 2.0
- **작성일:** 2026-01-16
- **상태:** Approved
- **변경:** 공개 배포 + Freemium 모델로 전환

---

## A. 문제 & 솔루션

### 한 줄 정의
> **바이브 코더들**을 위한 **HN/Reddit/GitHub 트렌드 수집기**로 **AI 요약 + 개인화된 선호도 학습**을 제공하는 **공개 서비스**.

### 고객 문제
1. **정보 과부하**: HN, Reddit, GitHub 트렌드를 매일 확인하기 번거로움
2. **시간 낭비**: 관심 없는 글까지 일일이 확인해야 함
3. **선호도 미반영**: 기존 도구들은 내 관심사 학습 안 함
4. **개인화 부재**: 모든 사람에게 같은 피드 제공

### 우리 솔루션
- 자동 수집 + Claude 요약으로 빠른 스캔
- 스와이프(좋아요/스킵) → 태그별 선호도 학습
- 다음 수집 시 선호 태그 우선 표시
- **개인별 데이터 분리** (UUID 기반)

### 검증 상태
| 검증 유형 | 상태 | 증거 |
|-----------|------|------|
| 문제 검증 | ✅ | 본인이 타겟 사용자 |
| 솔루션 검증 | ✅ | 직접 사용 후 만족 |
| 시장 검증 | 🔄 | 공개 배포 후 검증 예정 |

---

## B. 타겟 사용자

### Primary Persona
```yaml
이름: 바이브 코더
역할: AI 도구를 활용하는 개발자, 인디해커, 솔로 창업자
고통: 매일 트렌드 체크에 30분+ 소요, 관심 없는 글 필터링 수동
현재 해결책: 직접 HN/Reddit/GitHub 방문
우리 제품 사용 시: 5분 내 카드 리뷰로 트렌드 파악 + 선호도 자동 학습
```

### 핵심 관심 태그
- `ai` - AI/LLM 관련
- `vibe-code` - 바이브 코딩, AI 코딩 도구
- `solo` - 솔로 개발, 인디해커
- `saas` - SaaS 비즈니스
- `startup` - 스타트업 뉴스

---

## C. 기능 요구사항

### MVP v1.0 (완료)

| ID | 기능 | 설명 | 상태 |
|----|------|------|------|
| F001 | 콘텐츠 수집 | HN/Reddit/GitHub 트렌드 자동 수집 | ✅ Done |
| F002 | AI 요약 | Claude API로 제목+내용 요약 + 태그 추출 | ✅ Done |
| F003 | 카드 리뷰 UI | 좋아요/스킵 버튼이 있는 카드 리스트 | ✅ Done |
| F004 | 선호도 학습 | 태그별 점수 누적 | ✅ Done |
| F005 | 우선순위 정렬 | 선호 태그 점수 기반 표시 순서 | ✅ Done |

### v2.0 공개 배포 (진행 중)

| ID | 기능 | 설명 | 상태 |
|----|------|------|------|
| F010 | UUID 시스템 | 익명 유저 식별, 개인별 데이터 분리 | 🔄 진행 |
| F011 | Rate Limit | API 남용 방지 (일일 수집 횟수 제한) | ⬜ 대기 |
| F012 | UI 개선 | AI스럽지 않은 개성있는 디자인 | ⬜ 대기 |

### v3.0 Freemium (계획)

| ID | 기능 | 설명 | Tier |
|----|------|------|------|
| F020 | 로그인 연동 | UUID를 계정에 연결, 기기간 동기화 | 무료 |
| F021 | 후원 시스템 | Buy Me a Coffee / Patreon 연동 | - |
| F022 | 무제한 요약 | 후원자 전용 무제한 AI 요약 | 후원 |
| F023 | 추가 소스 | Product Hunt, Dev.to 등 | 후원 |
| F024 | 커스텀 태그 | 사용자 정의 태그 추가 | 후원 |

### v4.0+ (Nice to Have)
| ID | 기능 | 언제 추가 |
|----|------|-----------|
| F006 | 틴더 스타일 스와이프 | UI 개선 시 |
| F007 | 키워드 알림 | 특정 키워드 감지 시 알림 |
| F008 | Obsidian Export | 좋아요 항목 마크다운 내보내기 |
| F009 | 정규화 테이블 리팩토링 | 아이템 1000개+ 시 |

### Out of Scope
- ❌ 모바일 앱 (PWA로 대체 가능)
- ❌ 실시간 푸시 알림
- ❌ 팀/조직 기능

---

## D. 기술 명세

### 확정 스택

| 영역 | 선택 | 이유 |
|------|------|------|
| Backend | FastAPI | Clouvel과 통일, 익숙함 |
| Frontend | Jinja2 템플릿 | 분리 불필요, 단순함 |
| DB | SQLite | 솔로용, 파일 하나 |
| AI | Claude API | 이미 사용 중 |
| Scheduler | APScheduler | Python 내장, FastAPI와 통합 |

### 레이저 테스트 ✅
- Next.js? → 본인용 도구에 과함
- PostgreSQL? → SQLite면 충분
- 마이크로서비스? → 모놀리식 적정
- SQL JOIN 정렬? → Python 정렬로 충분 (MVP)

### 프로젝트 구조

```
vibecatch/
├── main.py              # FastAPI 앱 + 스케줄러
├── collectors/
│   ├── hackernews.py
│   ├── reddit.py
│   └── github.py
├── summarizer.py        # Claude API 요약 + 태그 추출
├── templates/
│   ├── index.html       # 카드 리뷰 UI
│   └── liked.html       # 좋아요 목록
├── static/
│   └── style.css
└── vibecatch.db         # SQLite
```

### DB 스키마

```sql
-- 유저 (UUID 기반)
CREATE TABLE users (
    uuid TEXT PRIMARY KEY,
    email TEXT,                  -- v3.0 로그인 시 연결
    tier TEXT DEFAULT 'free',    -- 'free', 'supporter'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen_at DATETIME
);

-- 수집된 콘텐츠 (공유)
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,        -- 'hn', 'reddit', 'github'
    external_id TEXT NOT NULL,   -- 원본 ID
    title TEXT NOT NULL,
    url TEXT,
    summary TEXT,                -- Claude 요약
    tags TEXT,                   -- JSON: ["ai", "vibe-code"]
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, external_id)
);

-- 유저별 아이템 상태 (개인)
CREATE TABLE user_items (
    user_uuid TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    status TEXT DEFAULT 'new',   -- 'new', 'liked', 'skipped'
    reviewed_at DATETIME,
    PRIMARY KEY (user_uuid, item_id),
    FOREIGN KEY (user_uuid) REFERENCES users(uuid),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

-- 유저별 태그 선호도 (개인)
CREATE TABLE preferences (
    user_uuid TEXT NOT NULL,
    tag TEXT NOT NULL,
    score INTEGER DEFAULT 0,     -- like: +1, skip: -1
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_uuid, tag),
    FOREIGN KEY (user_uuid) REFERENCES users(uuid)
);

-- Rate Limit 추적
CREATE TABLE rate_limits (
    user_uuid TEXT NOT NULL,
    date TEXT NOT NULL,          -- YYYY-MM-DD
    collect_count INTEGER DEFAULT 0,
    summarize_count INTEGER DEFAULT 0,
    PRIMARY KEY (user_uuid, date)
);
```

### Rate Limit 정책

| Tier | 일일 수집 | 일일 요약 |
|------|----------|----------|
| Free | 3회 | 30개 |
| Supporter | 무제한 | 무제한 |

### API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 리뷰할 카드 목록 (유저별, 선호도순 정렬) |
| POST | `/review/{id}` | 피드백 처리 `{action: 'like' \| 'skip'}` |
| GET | `/liked` | 좋아요한 항목 목록 (유저별) |
| GET | `/stats` | 태그별 선호도 현황 (유저별) |
| POST | `/collect` | 수동 수집 트리거 (Rate Limit 적용) |
| GET | `/health` | 헬스 체크 |

### 유저 식별 방식

```
[첫 방문]
1. 쿠키에 UUID 없음
2. 서버에서 UUID 생성 (uuid4)
3. users 테이블에 저장
4. Set-Cookie: user_uuid={uuid}; Max-Age=31536000; HttpOnly

[재방문]
1. Cookie: user_uuid={uuid} 읽기
2. users 테이블에서 확인
3. last_seen_at 업데이트
4. 해당 UUID의 데이터만 조회

[v3.0 로그인 연동]
1. 로그인 성공 시 email 연결
2. 다른 기기에서 로그인 → 기존 UUID 매핑
3. 기기간 데이터 동기화
```

### 핵심 로직

```
[수집 플로우]
APScheduler (매 6시간) → collectors/*.py 실행
→ 각 소스에서 상위 N개 가져오기
→ 중복 체크 (external_id)
→ Claude 요약 + 태그 추출
→ items 테이블에 저장 (공유)

[유저 초기화 플로우]
1. 쿠키에서 user_uuid 확인
2. 없으면 → UUID 생성 → users 테이블 저장 → 쿠키 설정
3. 있으면 → last_seen_at 업데이트
4. 새 아이템에 대해 user_items 레코드 생성 (status='new')

[리뷰 플로우 - GET /]
1. user_items JOIN items WHERE user_uuid={uuid} AND status='new'
2. preferences WHERE user_uuid={uuid} 로드
3. Python에서 각 item의 priority 계산
4. priority DESC로 정렬
5. 카드 UI 렌더링

[피드백 플로우 - POST /review/{id}]
1. user_items.status = 'liked' or 'skipped'
2. user_items.reviewed_at = now()
3. item.tags 각각에 대해:
   - like → preferences[user_uuid, tag].score += 1
   - skip → preferences[user_uuid, tag].score -= 1

[Rate Limit 플로우]
1. POST /collect 요청 시
2. rate_limits WHERE user_uuid AND date=today 조회
3. collect_count >= limit? → 429 Too Many Requests
4. 통과 → collect_count += 1
```

### 비용 추정

| 항목 | 계산 | 예상 비용 |
|------|------|-----------|
| HN 수집 | 30개 × 4회/일 = 120 요약/일 | |
| Reddit 수집 | 20개 × 4회/일 = 80 요약/일 | |
| GitHub 수집 | 10개 × 4회/일 = 40 요약/일 | |
| **총 API 호출** | ~240회/일 | |
| Claude Sonnet | ~$0.003/요약 | **~$0.72/일** |
| **월간 비용** | | **~$22/월** |

---

## E. 성공 지표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| 일일 리뷰 시간 | < 5분 | 체감 측정 |
| 좋아요 적중률 | 1주 후 50%+ | `liked / (liked + skipped) × 100` |
| 수집 안정성 | 하루 3회 이상 실패 없음 | 로그 모니터링 |

### 적중률 측정 (학습 효과 검증)
```
Week 1 적중률 vs Week 2 적중률 비교
→ 상승 = 선호도 학습 효과 있음

/stats 엔드포인트에서 제공:
- 전체 적중률
- 주간 적중률 추이
- 태그별 선호도 점수 TOP 10
```

---

## F. 타임라인

| Phase | 기간 | 목표 | 완료 조건 |
|-------|------|------|-----------|
| 1 | 1일 | 기본 구조 | FastAPI + DB + 템플릿 세팅 |
| 2 | 1일 | 수집기 | HN 수집 동작 |
| 3 | 0.5일 | 요약 | Claude 요약 + 태그 추출 |
| 4 | 0.5일 | 리뷰 UI | 카드 리스트 + 좋아요/스킵 |
| 5 | 0.5일 | 선호도 | 점수 누적 + Python 정렬 반영 |
| 6 | 0.5일 | 추가 소스 | Reddit, GitHub 수집 추가 |

**총 예상: 4일**

---

## G. 리스크

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| API 비용 초과 | 낮음 | 중 | 요약 캐싱, 수집 빈도 조절 |
| 소스 API 변경 | 중 | 중 | 각 수집기 독립 모듈화 |
| 태그 추출 부정확 | 중 | 낮음 | 프롬프트 튜닝으로 개선 |
| Python 정렬 성능 | 낮음 | 낮음 | 1000개+ 시 정규화 테이블 리팩토링 |

---

## H. 기술 결정 기록 (ADR)

### ADR-001: 태그 기반 정렬 방식

**상태**: Accepted

**컨텍스트**: 
- `items.tags`가 JSON 문자열 (`'["ai", "vibe-code"]'`)
- SQLite에서 JSON 배열과 직접 JOIN 불가

**옵션**:
1. **Python 정렬** - DB에서 전체 조회 후 Python에서 priority 계산/정렬
2. **정규화 테이블** - `item_tags` 테이블 추가, SQL JOIN으로 정렬

**결정**: 옵션 1 (Python 정렬)

**이유**:
- MVP 단계, 아이템 수 적음 (하루 ~240개, 누적 ~7000개/월)
- 구현 단순, DB 스키마 변경 불필요
- "일단 출시, 나중에 개선" 원칙

**리팩토링 트리거**: 아이템 1000개+ 도달 시 옵션 2로 전환

---

## 버전 히스토리

| 버전 | 날짜 | 변경 |
|------|------|------|
| 1.0 | 2026-01-16 | 초안 작성, 스택/스키마/API 확정 |
| 1.1 | 2026-01-16 | 정렬 로직 Python 방식으로 변경, 비용 추정 추가, 성공 지표 측정 방법 명확화, ADR-001 추가 |
| 2.0 | 2026-01-16 | **공개 배포 전환**: UUID 시스템, Rate Limit, Freemium 모델 추가. DB 스키마 재설계 (유저별 데이터 분리) |
