# /build - 프로덕션 빌드

> 프로덕션 빌드 실행.

## 사용법

```bash
/build
```

## 실행

```bash
pnpm build
```

## 성공 시

```markdown
## ✅ Build 성공

| 항목 | 값 |
|------|-----|
| 시간 | {X}s |
| 출력 | dist/ |
| 크기 | {X}KB |
```

## 실패 시

```markdown
## ❌ Build 실패

```
{빌드 에러 메시지}
```

### 원인
{분석}

### 수정 방법
{제안}
```

## 빌드 전 확인

```bash
# 빌드 전 typecheck 권장
pnpm typecheck && pnpm build
```

## 팁

- 빌드 실패는 보통 타입 에러
- `pnpm typecheck` 먼저 실행 권장
