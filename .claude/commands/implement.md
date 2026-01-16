# /implement - 구현 실행 (Shovel 방식)

> **원칙**
> 1. **계획 승인 후**만 실행
> 2. **Step 단위**로 진행
> 3. 각 Step 후 **검증**
> 4. 실패 시 **즉시 중단**

---

## 사용법

```bash
# 전체 계획 실행
/implement

# 특정 Step만
/implement step 1
/implement step 2

# 범위 지정
/implement step 1-3

# 이어서 실행 (중단된 곳부터)
/implement continue
```

---

## 사전 조건 확인

### 계획 존재 확인

```bash
# 최신 계획 파일
ls -t .claude/plans/*.md | head -1
```

### 계획 없으면

```markdown
## ⚠️ 계획 없음

`/implement`는 승인된 계획이 필요합니다.

### 먼저 실행
```bash
/plan [태스크]
```

계획 승인 후 다시 실행하세요.
```

---

## 구현 프로세스

```
/implement
    │
    ├── 계획 로드
    │   └── .claude/plans/plan-{latest}.md
    │
    ├── Step 1 실행
    │   ├── 작업 수행
    │   ├── 검증 실행
    │   └── 성공? → Step 2 / 실패? → 중단
    │
    ├── Step 2 실행
    │   └── ...
    │
    ├── Step N 실행
    │   └── ...
    │
    └── 완료 → Gate 안내
```

---

## Step 실행 형식

### Step 시작

```markdown
## 🔨 Step {N}/{Total}: {제목}

### 작업 내용
{계획에서 가져온 작업 내용}

### 대상 파일
- `{파일 경로}`

### 시작합니다...
```

### 구현 중

```typescript
// 실제 코드 작성/수정
```

### Step 검증

```bash
# 계획에 정의된 검증 명령 실행
{검증 명령}
```

### Step 완료

```markdown
## ✅ Step {N} 완료

| 항목 | 결과 |
|------|------|
| 작업 | 완료 |
| 검증 | ✅ 통과 |
| 시간 | {실제 소요 시간} |

→ Step {N+1}로 진행
```

### Step 실패

```markdown
## ❌ Step {N} 실패

### 실패 내용
```
{에러 내용}
```

### 원인 분석
{원인}

### 수정 방안
1. {방안}

### 선택
> **(r)** 재시도
> **(s)** 스킵 (비권장)
> **(a)** 중단

선택: ___
```

---

## 중간 저장

### 진행 상황 저장

```bash
# 진행 상황 저장
cat > .claude/plans/progress.json << 'EOF'
{
  "plan": "plan-20260109-143000.md",
  "currentStep": 2,
  "totalSteps": 5,
  "completed": [1],
  "failed": [],
  "timestamp": "2026-01-09T14:45:00Z"
}
EOF
```

### 이어서 실행

```markdown
## 📂 기존 진행 상황 발견

**계획**: plan-20260109-143000.md
**진행**: Step 2/5 (Step 1 완료)

이어서 실행하시겠습니까?

> **(y)** Step 2부터 이어서
> **(r)** 처음부터 다시
> **(c)** 취소

선택: ___
```

---

## 전체 완료 → 자동 플로우 시작

```markdown
## 🎉 구현 완료

### 요약
| 항목 | 값 |
|------|-----|
| 계획 | {계획명} |
| 총 Step | {N}개 |
| 완료 | {N}개 |
| 실패 | 0개 |
| 총 시간 | {X}h |

### 변경된 파일
1. `src/modules/auth/login.ts` (modified)
2. `src/modules/auth/types.ts` (new)
3. `src/modules/auth/login.test.ts` (new)

---

## 🔄 필수 플로우 시작 (자동)

구현 완료 ≠ 진짜 완료
아래 플로우 전체 통과 = 진짜 완료

### 1️⃣ /check-complete 실행합니다...

[껍데기 검사]
- [ ] TODO/FIXME 없음
- [ ] 모든 함수에 실제 로직 있음
- [ ] 하드코딩 더미 없음

[연결 검사]
- [ ] export → import 체인 완성
- [ ] 라우팅 등록됨
- [ ] UI에서 접근 가능

[동작 검사]
- [ ] 앱 실행 가능
- [ ] 해당 기능 작동 확인

### 2️⃣ /gate 실행합니다...

```bash
pnpm lint && pnpm test && pnpm build
```

### 3️⃣ /handoff 기록합니다...

{이 기능의 의도, 결정사항, 주의점 기록}

### 4️⃣ Context Bias 제거 권장

```
/clear 후 /verify 실행을 권장합니다.
새로운 눈으로 검증해야 품질 2-3배 향상!
```

### 다음 단계 (순서대로)
```
현재 위치: 구현 완료
   ↓
1. /check-complete ← 지금
2. /gate
3. /handoff  
4. /clear
5. /verify
6. 커밋
```
```

---

## 팁

### Step 크기

```
✅ 좋은 Step: 30분 이내, 단일 파일, 검증 가능
❌ 나쁜 Step: 2시간, 여러 파일, 검증 불분명
```

### 검증 빈도

```
Step 1 → 검증 ✅
Step 2 → 검증 ✅
Step 3 → 검증 ✅
...
최종 → /gate ✅
```

### 실패 시 대응

```
실패 → 원인 분석 → 수정 → 재시도
    ↓
3회 실패 → 계획 재검토 (/plan 다시)
```

---

## 자동 검증 (권장)

각 Step 후 자동 검증:

```bash
# Step 완료 후 자동 실행
pnpm typecheck && pnpm lint
```

Gate 전 빠른 피드백으로 시간 절약.
