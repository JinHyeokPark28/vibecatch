# /commit - 커밋 (Gate PASS 필수)

> Gate PASS 확인 후 커밋 + 푸시

## 사용법

```bash
# 기본 커밋
/commit

# 메시지 지정
/commit "feat(auth): add login"

# 푸시 포함
/commit --push
```

## 사전 조건

```markdown
## ⚠️ Gate PASS 필수

커밋 전 Gate가 통과되어야 합니다.

EVIDENCE.md 확인:
- 존재 여부
- 최신 여부 (오늘 날짜)
- PASS 상태
```

## 프로세스

```
/commit
    │
    ├── EVIDENCE.md 확인
    │   ├── 없음 → Gate 먼저 실행 안내
    │   └── 있음 → 날짜/상태 확인
    │
    ├── 변경사항 확인
    │   └── git status
    │
    ├── 커밋 메시지 제안
    │   └── Conventional Commits 형식
    │
    └── 커밋 + (옵션: 푸시)
```

## EVIDENCE.md 확인

```bash
# 존재 확인
test -f EVIDENCE.md && echo "EXISTS" || echo "NOT_FOUND"

# 상태 확인
grep -q "Status.*PASS" EVIDENCE.md && echo "PASS" || echo "FAIL"

# 날짜 확인
grep "Generated" EVIDENCE.md | head -1
```

## EVIDENCE.md 없거나 오래됨

```markdown
## ❌ 커밋 불가

### 사유
{EVIDENCE.md 없음 / Gate FAIL / 날짜 오래됨}

### 필요한 조치
```bash
pnpm gate
```

Gate PASS 후 다시 `/commit` 실행하세요.
```

## 커밋 메시지 제안

```markdown
## 📝 커밋 메시지 제안

### 변경된 파일
```
modified: src/auth/login.ts
new file: src/auth/types.ts
new file: src/auth/login.test.ts
```

### 제안 메시지
```
feat(auth): add user authentication

- Implement login/logout functionality
- Add JWT token handling
- Add input validation with Zod
- Add unit tests (8 cases)

Gate: PASS (2026-01-09T14:30:00Z)
```

### 선택
> **(y)** 이 메시지로 커밋
> **(e)** 수정
> **(c)** 취소

선택: ___
```

## Conventional Commits 형식

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Type

| Type | 설명 |
|------|------|
| feat | 새 기능 |
| fix | 버그 수정 |
| refactor | 리팩토링 |
| test | 테스트 추가 |
| docs | 문서 변경 |
| chore | 기타 변경 |

## 커밋 실행

```bash
git add .
git commit -m "{메시지}"
```

## 푸시 (옵션)

```bash
git push origin $(git branch --show-current)
```

## 완료

```markdown
## ✅ 커밋 완료

- Commit: `{hash}`
- Branch: `{branch}`
- Message: `{message}`

### Gate Evidence 포함됨
EVIDENCE.md가 커밋에 포함되어
Gate PASS 증거가 기록됩니다.

### 다음 단계
- PR 생성 (필요시)
- 다음 태스크 진행
```
