# /deep-debug - 반복 에러 근본 원인 정밀 분석

> **트리거**: 같은 에러 3회 반복 시 자동 실행 또는 수동 호출
> **목적**: 땜빵이 아닌 근본적 해결
> **원칙**: 작업 중단 → 정밀 분석 → 구조적 수정

---

## 사용법

```bash
/deep-debug                          # 가장 빈번한 반복 에러 분석
/deep-debug "TypeError-undefined"    # 특정 에러 분석
/deep-debug --file src/api/user.ts   # 특정 파일 집중 분석
```

---

## 자동 트리거 조건

```markdown
ERROR_LOG.md에서 감지:

### [에러-시그니처] 
- **횟수**: 3+ ⚠️

→ 🚨 자동으로 /deep-debug 실행
→ 작업 중단
→ 근본 원인 해결 후 재개
```

---

## 실행 프로세스

```
🚨 3회 반복 에러 감지
    │
    ├── Step 1: 작업 중단 선언
    │
    ├── Step 2: 에러 컨텍스트 수집
    │   ├── ERROR_LOG.md에서 상세 정보
    │   ├── 관련 파일 전체 읽기
    │   └── 호출 체인 추적
    │
    ├── Step 3: 데이터 플로우 분석
    │   └── 입력 → 처리 → 출력 추적
    │
    ├── Step 4: 근본 원인 분류
    │
    ├── Step 5: 구조적 수정 제안
    │   └── ❌ 땜빵 금지
    │
    └── Step 6: 검증 + 규칙화
```

---

## Step 1: 작업 중단 선언

```markdown
## 🚨 반복 에러 감지 - 작업 중단

**에러**: TypeError: Cannot read property 'name' of undefined
**반복 횟수**: 3회
**위치**: src/api/user.ts

---

⚠️ **땜빵으로 넘어가지 않습니다.**

근본 원인을 찾아 구조적으로 해결합니다.
예상 소요: 15-30분
```

---

## Step 2: 에러 컨텍스트 수집

### 2.1 ERROR_LOG.md에서 수집

```bash
# 해당 에러 상세 정보
cat ERROR_LOG.md | grep -A 10 "[에러-시그니처]"
```

```markdown
### 수집된 정보

**발생 이력**:
| 시각 | 입력 | 상황 |
|------|------|------|
| 14:30 | userId: null | API 호출 |
| 15:10 | userId: undefined | 테스트 |
| 15:45 | userId: "" | 폼 제출 |

**공통점**: userId가 falsy 값일 때 발생
```

### 2.2 관련 코드 전체 읽기

```bash
# 에러 발생 파일
cat src/api/user.ts

# 이 함수를 호출하는 곳
grep -rn "getUserName\|getUser" --include="*.ts" src/

# 타입 정의
cat src/types/user.ts
```

### 2.3 호출 체인 추적

```markdown
### 호출 체인

```
UserPage.tsx
    └── useUser() hook
        └── fetchUser(userId)
            └── api/user.ts:getUserName() ← 에러 발생
                └── response.data.user.name
```

**문제 지점**: userId 검증 없이 API 호출
```

---

## Step 3: 데이터 플로우 분석

```markdown
### 데이터 플로우

```
입력: userId (from URL param)
      │
      ├─ 정상: "abc123"
      │       ↓
      │   fetchUser("abc123")
      │       ↓
      │   response.data.user.name ✅
      │
      └─ 비정상: null | undefined | ""
              ↓
          fetchUser(null)  ← 검증 없음!
              ↓
          API 404 or null response
              ↓
          response.data.user.name ❌ TypeError
```

### 문제점
1. **입력 검증 없음**: userId가 falsy여도 API 호출
2. **응답 검증 없음**: response.data.user가 null일 수 있음
3. **에러 핸들링 없음**: try-catch 없음
```

---

## Step 4: 근본 원인 분류

```markdown
### 🎯 근본 원인 체크리스트

- [x] **타입 문제** - null/undefined/falsy 미처리
- [ ] 비동기 처리 - race condition
- [ ] 외부 의존성 - API 응답 불일치
- [ ] 로직 오류 - 잘못된 조건문
- [ ] 엣지 케이스 - 경계값 미처리
- [ ] 환경 설정 - 환경변수 누락

### 근본 원인
**입력/응답 모두에서 null 안전성 미확보**

단순히 `if (!user) return;` 추가는 땜빵.
입력-처리-출력 전체에 타입 가드 필요.
```

---

## Step 5: 구조적 수정 제안

### ❌ 땜빵 (금지)

```typescript
// 이렇게 하면 안 됨 - 문제 숨기기만 함
function getUserName(userId: string) {
  if (!userId) return 'Unknown';  // ❌ 땜빵
  const response = await fetchUser(userId);
  if (!response.data?.user) return 'Unknown';  // ❌ 땜빵
  return response.data.user.name;
}
```

### ✅ 구조적 수정

```typescript
// 1. 입력 검증 레이어
function validateUserId(userId: unknown): string {
  if (typeof userId !== 'string' || userId.trim() === '') {
    throw new ValidationError('Invalid userId');
  }
  return userId;
}

// 2. API 응답 타입 가드
interface UserResponse {
  data: { user: { name: string } } | null;
}

function isValidUserResponse(res: unknown): res is UserResponse {
  return res !== null 
    && typeof res === 'object'
    && 'data' in res
    && res.data !== null
    && 'user' in res.data;
}

// 3. 안전한 함수
async function getUserName(rawUserId: unknown): Promise<string> {
  const userId = validateUserId(rawUserId);
  
  const response = await fetchUser(userId);
  
  if (!isValidUserResponse(response)) {
    throw new ApiError('Invalid user response');
  }
  
  return response.data.user.name;
}

// 4. 호출부에서 에러 핸들링
try {
  const name = await getUserName(userId);
  setUserName(name);
} catch (error) {
  if (error instanceof ValidationError) {
    showError('잘못된 사용자 ID');
  } else if (error instanceof ApiError) {
    showError('사용자 정보를 불러올 수 없음');
  }
}
```

### 수정 범위

```markdown
| 파일 | 수정 내용 |
|------|-----------|
| src/utils/validation.ts | validateUserId 추가 |
| src/types/guards.ts | isValidUserResponse 추가 |
| src/api/user.ts | 타입 가드 적용 |
| src/pages/UserPage.tsx | try-catch 추가 |
| src/api/user.test.ts | 테스트 케이스 추가 |
```

---

## Step 6: 검증 + 규칙화

### 6.1 테스트 케이스 추가

```typescript
// src/api/user.test.ts
describe('getUserName', () => {
  // 정상 케이스
  it('returns name for valid userId', async () => {
    const name = await getUserName('abc123');
    expect(name).toBe('John');
  });

  // 에러 케이스 - 이전에 실패했던 것들
  it('throws ValidationError for null userId', async () => {
    await expect(getUserName(null)).rejects.toThrow(ValidationError);
  });

  it('throws ValidationError for empty userId', async () => {
    await expect(getUserName('')).rejects.toThrow(ValidationError);
  });

  it('throws ApiError for invalid response', async () => {
    mockFetchUser.mockResolvedValue({ data: null });
    await expect(getUserName('abc')).rejects.toThrow(ApiError);
  });
});
```

### 6.2 CLAUDE.md 규칙 추가

```markdown
### 추가할 규칙

**NEVER**:
- NEVER 외부 입력(URL param, form) 직접 사용 without validation
- NEVER API 응답 직접 접근 without type guard

**ALWAYS**:
- ALWAYS 외부 입력은 validateX() 함수 통과
- ALWAYS API 응답은 isValidXResponse() 체크 후 사용
- ALWAYS 에러 케이스별 구체적 핸들링
```

### 6.3 ERROR_LOG.md 업데이트

```markdown
### [TypeError-undefined-api]
- **횟수**: 3
- **상태**: ✅ 해결
- **해결 방법**: 입력 검증 + 타입 가드 + 에러 핸들링
- **테스트 추가**: 3개
- **규칙 추가**: NEVER 2개, ALWAYS 3개
```

---

## 완료 메시지

```markdown
## ✅ /deep-debug 완료

### 에러
- **시그니처**: TypeError-undefined-api
- **반복 횟수**: 3회 → 해결됨

### 근본 원인
- 입력/응답 null 안전성 미확보

### 수정 내용
| 항목 | 상세 |
|------|------|
| 파일 수정 | 5개 |
| 테스트 추가 | 3개 |
| 규칙 추가 | NEVER 2, ALWAYS 3 |

### 검증
- [x] 기존 에러 케이스 테스트 통과
- [x] 새 테스트 케이스 통과
- [x] /gate PASS

### ERROR_LOG.md
- 해당 에러: ✅ 해결 표시

---

**이 에러는 다시 발생하지 않습니다.**

작업을 재개하세요.
```

---

## ⚠️ 주의사항

```markdown
❌ /deep-debug 없이 3회 반복 에러 무시 금지
❌ 땜빵으로 "일단 넘어가기" 금지
❌ 테스트 없이 수정 완료 선언 금지

✅ 반드시 근본 원인까지 파악
✅ 구조적 수정 (입력-처리-출력 전체)
✅ 테스트로 검증
✅ 규칙으로 재발 방지
```
