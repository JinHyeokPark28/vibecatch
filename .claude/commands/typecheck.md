# /typecheck - TypeScript 검사

> 빠른 타입 체크. `/verify typecheck`의 단축 명령.

## 사용법

```bash
/typecheck
```

## 실행

```bash
pnpm typecheck
# 또는
pnpm tsc --noEmit
```

## 성공 시

```markdown
## ✅ TypeCheck 통과

| 항목 | 값 |
|------|-----|
| 에러 | 0 |
| 시간 | {X}s |
```

## 실패 시

```markdown
## ❌ TypeCheck 실패

```
src/{file}.ts:{line}:{col}
TS{code}: {message}
```

### 수정 필요
{구체적 안내}
```

## 팁

- 파일 수정 후 수시로 실행
- Gate 전 빠른 체크용
