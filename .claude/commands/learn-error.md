# /learn-error - 에러 학습 자동화

> **목적**: ERROR_LOG.md에 쌓인 에러 → 패턴 분석 → CLAUDE.md 규칙화 → 로그 비움
> **트리거**: 사용자가 시간 날 때 수동 실행

---

## 사용법

```bash
/learn-error           # 전체 에러 학습
/learn-error --preview # 미리보기만 (적용 안 함)
```

---

## 실행 프로세스

```
/learn-error
    │
    ├── Phase 1: 에러 수집
    │   └── ERROR_LOG.md 읽기
    │
    ├── Phase 2: 패턴 분석
    │   ├── 유형별 그룹화
    │   ├── 반복 패턴 식별
    │   └── 근본 원인 추정
    │
    ├── Phase 3: 규칙 생성
    │   └── NEVER/ALWAYS 형식
    │
    ├── Phase 4: 적용
    │   ├── CLAUDE.md에 규칙 추가
    │   └── ERROR_LOG.md 비움
    │
    └── Phase 5: 리포트
```

---

## Phase 1: 에러 수집

```bash
# ERROR_LOG.md 읽기
cat ERROR_LOG.md
```

### 출력 형식

```markdown
## 📊 에러 현황

| 시그니처 | 횟수 | 상태 | 최근 |
|----------|------|------|------|
| TypeError-undefined-api | 3 | ❌ | 01-15 14:30 |
| 429-rate-limit-reddit | 2 | ✅ | 01-15 12:00 |
| ENOENT-env-missing | 1 | ❌ | 01-15 10:00 |

**총**: 3종류, 6건
**미해결**: 2종류
**3회+ 반복**: 1종류 ⚠️
```

---

## Phase 2: 패턴 분석

### 2.1 유형별 그룹화

```markdown
### 🔍 패턴 분석

**타입 에러 (1종류, 3건)**
- TypeError-undefined-api
- 공통점: null/undefined 체크 누락

**외부 API (1종류, 2건)**
- 429-rate-limit-reddit
- 공통점: Rate limit 미처리

**환경 설정 (1종류, 1건)**
- ENOENT-env-missing
- 공통점: 환경변수 검증 없음
```

### 2.2 근본 원인 추정

```markdown
### 🎯 근본 원인

1. **타입 안전성 부족**
   - null/undefined 가드 미적용
   - 영향: 런타임 에러

2. **외부 API 방어 부족**
   - Rate limit, timeout 미설정
   - 영향: 서비스 불안정

3. **환경 검증 누락**
   - 필수 환경변수 체크 없음
   - 영향: 배포 시 장애
```

---

## Phase 3: 규칙 생성

### 3.1 NEVER 규칙

```markdown
### 🚫 추가할 NEVER 규칙

1. **NEVER** 외부 데이터 사용 without null 체크
   ```typescript
   // ❌ NEVER
   const name = response.data.user.name;
   
   // ✅ INSTEAD
   const name = response.data?.user?.name ?? 'Unknown';
   ```

2. **NEVER** 외부 API 호출 without rate limit 처리
   ```typescript
   // ❌ NEVER
   for (const id of ids) {
     await fetchData(id);
   }
   
   // ✅ INSTEAD
   await rateLimitedFetch(ids, { delay: 100 });
   ```
```

### 3.2 ALWAYS 규칙

```markdown
### ✅ 추가할 ALWAYS 규칙

1. **ALWAYS** 서버 시작 시 필수 환경변수 검증
   ```typescript
   // src/config/validateEnv.ts
   const required = ['API_KEY', 'DB_URL'];
   required.forEach(key => {
     if (!process.env[key]) throw new Error(`Missing: ${key}`);
   });
   ```

2. **ALWAYS** 외부 API 호출 시 timeout 설정
   ```typescript
   fetch(url, { signal: AbortSignal.timeout(5000) })
   ```
```

---

## Phase 4: 적용

### 4.1 사용자 확인

```markdown
## 📝 적용 내용 확인

### CLAUDE.md에 추가될 규칙
- NEVER 2개
- ALWAYS 2개

### ERROR_LOG.md
- 해결된 에러: 비움
- 미해결 에러: 유지 (해결 방안 제시)

---

적용하시겠습니까?

> **(y)** 적용
> **(n)** 취소
> **(e)** 수정 후 적용
```

### 4.2 적용 실행

```bash
# CLAUDE.md ERROR_LOG 섹션에 규칙 추가
# ERROR_LOG.md 해결된 항목 제거
```

---

## Phase 5: 리포트

```markdown
## ✅ 에러 학습 완료

### 요약
| 항목 | 값 |
|------|-----|
| 처리된 에러 | 3종류 (6건) |
| 추가된 NEVER | 2개 |
| 추가된 ALWAYS | 2개 |
| 미해결 에러 | 1종류 (해결 방안 제시됨) |

### 적용된 규칙
1. NEVER 외부 데이터 without null 체크
2. NEVER 외부 API without rate limit
3. ALWAYS 서버 시작 시 환경변수 검증
4. ALWAYS API 호출 시 timeout

### 미해결 에러 처리
- `TypeError-undefined-api` (3회 반복)
  → `/deep-debug` 실행 권장

### ERROR_LOG.md
- 비워짐 ✅
- 새 에러 계속 기록됨

---

**다음 /learn-error**: 에러가 쌓이면 다시 실행
```

---

## 미해결 에러 처리

미해결 에러가 있을 경우:

```markdown
## ⚠️ 미해결 에러

### TypeError-undefined-api (3회 반복)
- **상태**: ❌ 미해결
- **근본 원인**: API 응답 구조 불일치
- **권장 조치**: `/deep-debug TypeError-undefined-api`

ERROR_LOG.md에 유지됩니다.
해결 후 `/learn-error` 재실행하세요.
```

---

## 예시 전체 플로우

```markdown
## /learn-error 실행 결과

### 1. 에러 현황
- TypeError-undefined-api: 3회 ⚠️
- 429-rate-limit-reddit: 2회 ✅ (해결됨)

### 2. 패턴 분석
- 타입 에러: null 체크 누락
- API 에러: rate limit 추가로 해결됨

### 3. 규칙 생성
- NEVER: 1개 (null 체크)
- ALWAYS: 0개

### 4. 적용
- CLAUDE.md 업데이트 ✅
- ERROR_LOG.md: 해결된 항목 제거 ✅

### 5. 미해결
- TypeError-undefined-api → /deep-debug 권장

---

학습 완료. 이 에러 패턴은 다시 발생하지 않습니다.
```
