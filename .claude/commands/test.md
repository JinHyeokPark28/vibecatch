# /test - 테스트 실행

> 테스트 실행. `/verify test`의 단축 명령.

## 사용법

```bash
# 전체 테스트
/test

# 특정 파일/패턴
/test auth
/test src/modules/auth

# Watch 모드
/test --watch
```

## 실행

```bash
pnpm test
# 또는
pnpm vitest run
```

## 성공 시

```markdown
## ✅ Test 통과

```
Test Files  {N} passed
     Tests  {M} passed
  Duration  {X}s
```
```

## 실패 시

```markdown
## ❌ Test 실패

```
FAIL  src/{file}.test.ts > {test name}
AssertionError: expected X to equal Y
```

### 분석
{원인}

### 수정 방안
{제안}
```

## 테스트 요구사항

```
최소 8개 테스트
├── 성공 케이스
├── 실패 케이스
├── 에러 핸들링
└── 엣지 케이스
```

## 팁

- `--watch`로 개발 중 자동 실행
- 테스트 없음 = Gate 실패
