# /lint - ESLint 검사

> 빠른 린트 체크. `/verify lint`의 단축 명령.

## 사용법

```bash
# 전체 린트
/lint

# 자동 수정
/lint --fix

# 특정 경로
/lint src/modules/auth
```

## 실행

```bash
pnpm lint
# 또는
pnpm eslint . --ext .ts,.tsx
```

## 성공 시

```markdown
## ✅ Lint 통과

| 항목 | 값 |
|------|-----|
| 에러 | 0 |
| 경고 | {N} |
```

## 실패 시

```markdown
## ❌ Lint 실패

```
src/{file}.ts
  {line}:{col}  error  {message}  {rule}
```

### 자동 수정 가능
```bash
pnpm lint --fix
```
```

## 팁

- `--fix`로 자동 수정 가능한 것들 먼저 처리
- Gate 전 빠른 체크용
