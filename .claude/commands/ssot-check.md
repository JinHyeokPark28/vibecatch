# /ssot-check - SSOT 검사 (Shovel 방식)

> **"PRD가 법이다. 분산은 버그다."**
>
> 1. **Single Source of Truth** 위반 검사
> 2. 중복 타입/상수/설정 감지
> 3. PRD 외 기능 감지
> 4. 환경변수 문서화 검사

---

## 사용법

```bash
# 전체 SSOT 검사
/ssot-check

# 특정 항목만
/ssot-check types       # 타입 중복
/ssot-check constants   # 매직 넘버
/ssot-check env         # 환경변수
/ssot-check prd         # PRD 외 기능
```

---

## SSOT 항목별 위치

| 항목 | SSOT 위치 | 분산 금지 |
|------|-----------|-----------|
| 스펙/기능 | `docs/PRD.md` | 구두 합의, 채팅 |
| 타입 | `src/shared/types/` | 각 모듈에 중복 |
| 상수 | `src/shared/constants/` | 매직넘버, 하드코딩 |
| 설정 | `src/core/config/` | 여러 파일에 설정값 |
| 환경변수 | `.env.example` | 코드 내 기본값 |
| 스키마 | `src/shared/schemas/` | 각 라우트에 중복 |

---

## 검사 항목

### 1. 타입 중복 검사

```bash
# 중복 interface/type 검색
grep -rn "interface\|type " src --include="*.ts" | \
  grep -v "node_modules" | \
  sed 's/.*\(interface\|type\) \([A-Z][a-zA-Z]*\).*/\2/' | \
  sort | uniq -d
```

**결과 예시**:
```markdown
### 🔍 타입 중복 검사

**발견된 중복**:
| 타입명 | 위치 1 | 위치 2 |
|--------|--------|--------|
| User | src/auth/types.ts:5 | src/user/types.ts:3 |
| Config | src/app/types.ts:10 | src/core/types.ts:8 |

**위반**: 2개

**수정 방법**:
```typescript
// ❌ 현재 (중복)
// src/auth/types.ts
interface User { id: string; name: string; }

// src/user/types.ts  
interface User { id: string; name: string; }

// ✅ 수정 (SSOT)
// src/shared/types/user.ts
export interface User { id: string; name: string; }

// 사용처에서 import
import { User } from '@/shared/types/user';
```
```

### 2. 매직 넘버 검사

```bash
# 하드코딩된 숫자 검색
grep -rn "[0-9]\{2,\}" src --include="*.ts" | \
  grep -v "node_modules\|test\|\.d\.ts" | \
  grep -v "import\|export\|//\|const.*="
```

**결과 예시**:
```markdown
### 🔍 매직 넘버 검사

**발견된 매직 넘버**:
| 값 | 위치 | 컨텍스트 |
|----|------|----------|
| 3600 | src/auth/token.ts:23 | expiresIn: 3600 |
| 1000 | src/api/retry.ts:15 | delay: 1000 |
| 500 | src/utils/limit.ts:8 | maxItems: 500 |

**위반**: 3개

**수정 방법**:
```typescript
// ❌ 현재 (매직 넘버)
jwt.sign(payload, secret, { expiresIn: 3600 });

// ✅ 수정 (상수화)
// src/shared/constants/auth.ts
export const AUTH = {
  TOKEN_EXPIRY_SECONDS: 3600,
} as const;

// 사용처
import { AUTH } from '@/shared/constants/auth';
jwt.sign(payload, secret, { expiresIn: AUTH.TOKEN_EXPIRY_SECONDS });
```
```

### 3. 환경변수 검사

```bash
# 코드에서 사용되는 환경변수
grep -rn "process\.env\." src --include="*.ts" | \
  sed 's/.*process\.env\.\([A-Z_]*\).*/\1/' | \
  sort | uniq > /tmp/env_used.txt

# .env.example에 정의된 환경변수
cat .env.example | grep -v "^#" | cut -d= -f1 | sort > /tmp/env_defined.txt

# 차이 확인
comm -23 /tmp/env_used.txt /tmp/env_defined.txt
```

**결과 예시**:
```markdown
### 🔍 환경변수 검사

**.env.example 정의됨**:
- JWT_SECRET ✅
- DATABASE_URL ✅
- API_KEY ✅

**코드에서 사용되지만 .env.example에 없음**:
| 환경변수 | 사용 위치 |
|----------|----------|
| NEW_API_KEY | src/api/external.ts:12 |
| CACHE_TTL | src/cache/redis.ts:5 |

**위반**: 2개

**수정 방법**:
```bash
# .env.example에 추가
echo "NEW_API_KEY=your_api_key_here" >> .env.example
echo "CACHE_TTL=3600" >> .env.example
```
```

### 4. PRD 외 기능 검사

```bash
# 최근 변경된 파일에서 기능 추출
git diff --name-only HEAD~5 | xargs grep -l "export.*function\|export.*class"

# PRD에서 기능 목록 추출
grep -E "^- \[.\]|^### " docs/PRD.md
```

**결과 예시**:
```markdown
### 🔍 PRD 외 기능 검사

**PRD에 정의된 기능**:
1. 로그인/로그아웃
2. 사용자 프로필 조회
3. 비밀번호 변경

**최근 추가된 기능**:
| 기능 | 파일 | PRD 여부 |
|------|------|----------|
| login() | src/auth/login.ts | ✅ |
| logout() | src/auth/logout.ts | ✅ |
| deleteAccount() | src/auth/delete.ts | ❌ |

**위반**: 1개 (deleteAccount - PRD에 없음)

**조치**:
> **(b)** BACKLOG.md로 이동
> **(p)** PRD.md 업데이트 요청
> **(d)** 코드 삭제

선택: ___
```

---

## 전체 검사 결과

```markdown
## 📊 SSOT 검사 결과

### 요약
| 항목 | 위반 수 | 상태 |
|------|---------|------|
| 타입 중복 | 2 | ⚠️ |
| 매직 넘버 | 3 | ⚠️ |
| 환경변수 | 2 | ❌ |
| PRD 외 기능 | 1 | ❌ |
| **총계** | **8** | **수정 필요** |

### 심각도별
- 🔴 Critical (즉시 수정): 3개 (환경변수 2, PRD 1)
- 🟡 Warning (권장 수정): 5개 (타입 2, 매직넘버 3)

### 우선순위
1. **환경변수 문서화** - 런타임 에러 방지
2. **PRD 외 기능 처리** - SSOT 준수
3. **타입 중복 제거** - 유지보수성
4. **매직 넘버 상수화** - 가독성

### 자동 수정 가능
- 환경변수: `.env.example` 업데이트
- 매직 넘버: 일부 상수화 가능

자동 수정 실행하시겠습니까?
> **(y)** 자동 수정 (가능한 것만)
> **(n)** 수동 수정
```

---

## 자동 수정

```markdown
## 🔧 자동 수정 실행

### 환경변수 문서화
```bash
echo "NEW_API_KEY=your_api_key_here" >> .env.example
echo "CACHE_TTL=3600" >> .env.example
```
✅ 완료

### 매직 넘버 → 상수
❌ 수동 수정 필요 (컨텍스트 확인 필요)

### 완료된 수정
- .env.example 업데이트: 2개 추가

### 남은 수정 (수동 필요)
- 타입 중복: 2개
- 매직 넘버: 3개
- PRD 외 기능: 1개
```

---

## CI 통합 (권장)

```yaml
# .github/workflows/ssot-check.yml
name: SSOT Check

on: [push, pull_request]

jobs:
  ssot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check duplicate types
        run: |
          duplicates=$(grep -rn "interface\|type " src --include="*.ts" | ...)
          if [ -n "$duplicates" ]; then
            echo "::error::SSOT violation: Duplicate types found"
            exit 1
          fi
      - name: Check env documentation
        run: |
          # 환경변수 검사 스크립트
```

---

## 정기 검사 권장

| 시점 | 검사 항목 |
|------|----------|
| 파일 저장 시 | 해당 파일 타입 중복 |
| 커밋 전 | 환경변수 문서화 |
| PR 전 | 전체 SSOT 검사 |
| 주간 | PRD 동기화 확인 |
