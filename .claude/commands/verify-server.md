# /verify-server - 서버 로직 정밀 검증

> **목적**: 서버 코드, 환경변수, 설정을 코드 레벨에서 검증
> **트리거**: 서버 기능 완료 시 `/gate` 전에 실행
> **강점**: 로그 기반이 아닌 코드 직접 분석 (사전 예방)

---

## 사용법

```bash
/verify-server              # 전체 서버 검증
/verify-server --env        # 환경변수만
/verify-server --api        # API 라우트만
/verify-server --db         # DB 관련만
```

---

## 검증 플로우

```
/verify-server
    │
    ├── 1. 환경변수 검증
    │   ├── .env.example vs .env 비교
    │   ├── 하드코딩 시크릿 검사
    │   └── 필수값 누락 체크
    │
    ├── 2. 서버 구조 파악
    │   └── 엔트리포인트, 라우트 수집
    │
    ├── 3. API 라우트 검증
    │   ├── 에러 핸들링 존재?
    │   ├── 입력 검증 존재?
    │   └── 인증 미들웨어 적용?
    │
    ├── 4. 외부 의존성 검증
    │   ├── timeout 설정?
    │   ├── 에러 처리?
    │   └── rate limit 고려?
    │
    ├── 5. DB 검증 (있는 경우)
    │   └── 스키마, 관계, 인덱스
    │
    └── 6. 결과 리포트
```

---

## 1. 환경변수 검증

### 1.1 파일 비교

```bash
# .env.example 확인
cat .env.example 2>/dev/null || echo "⚠️ .env.example 없음"

# .env 확인 (값은 마스킹)
cat .env 2>/dev/null | sed 's/=.*/=***/' || echo "⚠️ .env 없음"
```

### 1.2 체크 항목

```markdown
### 환경변수 검증 결과

| 체크 | 상태 | 상세 |
|------|------|------|
| .env.example 존재 | ✅/❌ | |
| .env 존재 | ✅/❌ | |
| 모든 키 매칭 | ✅/❌ | 누락: X, Y |
| 빈 값 없음 | ✅/❌ | 빈 값: Z |
| 하드코딩 시크릿 | ✅/❌ | |

### 누락된 환경변수
```
.env.example에 있지만 .env에 없음:
- API_KEY
- DB_PASSWORD
```

### 하드코딩 검사
```bash
# 코드 내 하드코딩 시크릿 검색
grep -rn "password\|secret\|api_key\|token" --include="*.ts" src/ | grep -v ".env" | grep -v "process.env"
```
```

### 1.3 시작 시 검증 코드 확인

```bash
# 환경변수 검증 로직 존재 여부
grep -rn "process.env" --include="*.ts" src/ | head -20
grep -rn "validateEnv\|checkEnv\|requiredEnv" --include="*.ts" src/
```

```markdown
### 환경변수 검증 로직

| 상태 | 설명 |
|------|------|
| ✅ 있음 | src/config/env.ts에서 검증 |
| ❌ 없음 | 시작 시 검증 로직 필요 |

**권장 구현**:
```typescript
// src/config/validateEnv.ts
const required = ['API_KEY', 'DB_URL', 'JWT_SECRET'];

export function validateEnv() {
  const missing = required.filter(key => !process.env[key]);
  if (missing.length > 0) {
    throw new Error(`Missing env vars: ${missing.join(', ')}`);
  }
}
```
```

---

## 2. 서버 구조 파악

### 2.1 엔트리포인트 확인

```bash
# 서버 엔트리포인트 찾기
find . -type f \( -name "server.*" -o -name "app.*" -o -name "index.*" \) \
  -path "*/src/*" | head -10

# package.json scripts 확인
cat package.json | grep -A 5 '"scripts"'
```

### 2.2 라우트 수집

```bash
# Express/Fastify 라우트
grep -rn "router\.\|app\.\(get\|post\|put\|delete\|patch\)" \
  --include="*.ts" --include="*.js" src/ | head -30

# Next.js API 라우트
find . -path "*/api/*" -name "*.ts" | head -20
```

```markdown
### 서버 구조

**엔트리포인트**: src/server.ts
**프레임워크**: Express / Next.js / Fastify

**API 라우트 목록**:
| 메서드 | 경로 | 파일 |
|--------|------|------|
| GET | /api/users | src/routes/users.ts:12 |
| POST | /api/users | src/routes/users.ts:25 |
| GET | /api/builds/:id | src/routes/builds.ts:8 |
```

---

## 3. API 라우트 검증

### 3.1 각 라우트 체크

```markdown
### API 라우트 검증

#### GET /api/users (src/routes/users.ts:12)

| 체크 | 상태 | 상세 |
|------|------|------|
| try-catch / 에러 핸들러 | ✅/❌ | |
| 입력 검증 (query/params) | ✅/❌ | |
| 인증 미들웨어 | ✅/❌/N/A | |
| 응답 타입 정의 | ✅/❌ | |

**코드 스니펫**:
```typescript
// 현재 코드
router.get('/users', async (req, res) => {
  const users = await db.users.findAll();  // ❌ try-catch 없음
  res.json(users);
});
```

**권장 수정**:
```typescript
router.get('/users', async (req, res, next) => {
  try {
    const users = await db.users.findAll();
    res.json(users);
  } catch (error) {
    next(error);  // 에러 핸들러로 전달
  }
});
```
```

### 3.2 공통 패턴 검사

```bash
# 에러 핸들링 패턴 검사
grep -rn "try\|catch\|next(error)" --include="*.ts" src/routes/

# 입력 검증 패턴 검사
grep -rn "validate\|zod\|yup\|joi" --include="*.ts" src/

# 인증 미들웨어 검사
grep -rn "auth\|authenticate\|isLoggedIn" --include="*.ts" src/routes/
```

---

## 4. 외부 의존성 검증

### 4.1 외부 호출 수집

```bash
# fetch/axios 호출
grep -rn "fetch\|axios\|got" --include="*.ts" src/ | head -20

# 외부 서비스 클라이언트
grep -rn "prisma\|supabase\|firebase\|redis" --include="*.ts" src/
```

### 4.2 각 호출 체크

```markdown
### 외부 의존성 검증

#### Reddit API (src/services/reddit.ts:34)

| 체크 | 상태 | 상세 |
|------|------|------|
| timeout 설정 | ✅/❌ | |
| 에러 응답 처리 | ✅/❌ | |
| rate limit 처리 | ✅/❌ | |
| 재시도 로직 | ✅/❌/N/A | |

**현재 코드**:
```typescript
const response = await fetch(REDDIT_API_URL);  // ❌ timeout 없음
```

**권장 수정**:
```typescript
const response = await fetch(REDDIT_API_URL, {
  signal: AbortSignal.timeout(5000),  // 5초 timeout
  headers: { 'User-Agent': 'MyApp/1.0' }
});

if (!response.ok) {
  if (response.status === 429) {
    // Rate limit 처리
    await delay(1000);
    return retry();
  }
  throw new ExternalApiError(`Reddit API: ${response.status}`);
}
```
```

---

## 5. DB 검증 (있는 경우)

### 5.1 스키마 확인

```bash
# Prisma 스키마
cat prisma/schema.prisma 2>/dev/null | head -50

# TypeORM 엔티티
find . -name "*.entity.ts" -exec cat {} \;
```

### 5.2 체크 항목

```markdown
### DB 스키마 검증

| 체크 | 상태 | 상세 |
|------|------|------|
| 필수 필드 NOT NULL | ✅/❌ | |
| 관계 설정 올바름 | ✅/❌ | |
| 인덱스 설정 | ✅/❌ | |
| 마이그레이션 동기화 | ✅/❌ | |

**주의 필요**:
- User.email: unique 제약 없음
- Post.userId: 인덱스 없음 (쿼리 성능 저하 가능)
```

---

## 6. 결과 리포트

```markdown
## /verify-server 결과

### 요약
| 영역 | 통과 | 경고 | 실패 |
|------|------|------|------|
| 환경변수 | 3 | 1 | 0 |
| API 라우트 | 5 | 2 | 1 |
| 외부 의존성 | 2 | 1 | 0 |
| DB | 4 | 0 | 0 |
| **총계** | **14** | **4** | **1** |

### ❌ 실패 (즉시 수정 필요)

1. **GET /api/builds/:id** - 에러 핸들링 없음
   - 위치: src/routes/builds.ts:8
   - 수정: try-catch 추가

### ⚠️ 경고 (권장 수정)

1. **환경변수** - 시작 시 검증 로직 없음
2. **Reddit API** - timeout 미설정
3. **POST /api/users** - 입력 검증 없음

### ✅ 통과

- 환경변수 파일 일치
- 인증 미들웨어 적용
- DB 스키마 정상
- ...

---

### 다음 단계

1. ❌ 실패 항목 수정 (필수)
2. ⚠️ 경고 항목 검토 (권장)
3. 수정 후 `/verify-server` 재실행
4. 모두 통과 시 `/gate` 진행
```

---

## 자동 체크리스트 생성

프로젝트별 맞춤 체크리스트:

```markdown
## [프로젝트명] 서버 검증 체크리스트

### 환경변수
- [ ] API_KEY 설정됨
- [ ] DB_URL 설정됨
- [ ] JWT_SECRET 설정됨 (32자 이상)

### API 엔드포인트
- [ ] GET /api/builds - 인증 ✅, 에러처리 ✅
- [ ] POST /api/builds - 입력검증 ✅, 인증 ✅
- [ ] GET /api/users/:id - 권한체크 ✅

### 외부 서비스
- [ ] Reddit API - timeout 5s, rate limit 처리
- [ ] YouTube API - 할당량 체크, 에러 핸들링

이 체크리스트는 /verify-server 실행 시 자동 체크됩니다.
```

---

## 워크플로우 통합

```
기능 완료
    ↓
/check-complete (껍데기/연결 검사)
    ↓
/verify-server (서버 로직 검사) ← 🆕
    ↓
/gate (lint→test→build)
    ↓
/handoff → /clear → /verify
    ↓
커밋
```
