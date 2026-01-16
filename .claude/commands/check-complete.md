---
name: check-complete
description: 껍데기/미연결 코드 검사 - 진짜 완료인지 확인
---

# 🔍 완료 검증 (껍데기/미연결 방지)

> **목적**: "완료"라고 하기 전에 진짜 완료인지 확인
> **트리거**: 기능 구현 후, 특히 규모가 큰 작업 후

---

## 1. 껍데기 검사

다음 패턴이 있는지 확인:

```
검색할 것:
- "TODO"
- "FIXME"
- "placeholder"
- "implement"
- "not implemented"
- 빈 함수 body: { }
- console.log만 있는 함수
- 하드코딩된 더미 배열: [{ id: 1, ... }]
- return null 또는 return undefined만 있는 함수
```

### 실행

```bash
# TODO/FIXME 검색
grep -r "TODO\|FIXME\|placeholder\|not implemented" src/

# 빈 함수 찾기
grep -rn "() => {}" src/
grep -rn "{ }" src/
```

---

## 2. 미연결 검사

### 컴포넌트/함수가 실제로 사용되는지 확인

```
확인할 것:
- [ ] export한 것이 어디선가 import 되는가?
- [ ] 라우팅에 등록되어 있는가?
- [ ] 네비게이션/메뉴에서 접근 가능한가?
- [ ] 버튼/링크가 이 기능을 호출하는가?
```

### 실행

```bash
# 특정 export가 import 되는지 확인
grep -r "import.*MyComponent" src/

# 라우팅 확인
grep -r "path.*my-feature\|route.*my-feature" src/
```

---

## 3. E2E 동작 확인

### 직접 확인 (가장 중요!)

```
1. 앱 실행 (pnpm dev)
2. 해당 기능으로 이동 가능한가?
   - URL 직접 입력으로?
   - 메뉴/네비게이션으로?
3. 기능이 실제로 작동하는가?
   - 버튼 클릭 → 반응 있음?
   - 폼 제출 → 데이터 저장?
   - API 호출 → 응답 표시?
```

---

## 4. 체크리스트 (복사해서 사용)

```markdown
## [기능명] 완료 체크

### 껍데기 검사
- [ ] TODO/FIXME 없음
- [ ] 모든 함수에 실제 로직 있음
- [ ] 하드코딩 더미 데이터 없음
- [ ] console.log만 있는 핸들러 없음

### 연결 검사
- [ ] export → import 체인 완성
- [ ] 라우팅 등록됨
- [ ] 네비게이션에서 접근 가능
- [ ] 기존 UI에서 호출됨

### 동작 검사
- [ ] 앱 실행 성공
- [ ] 해당 페이지 접근 가능
- [ ] 핵심 기능 동작 확인
- [ ] 에러 없음

### 최종
- [ ] Gate PASS (lint, test, build)
```

---

## 5. 대규모 기능일 때

규모가 클 때는 단계별로 상태 명시:

```
현재 상태: [선택]
□ Phase 1: 구조만 생성 (껍데기)
□ Phase 2: 로직 구현 완료 (미연결)
□ Phase 3: 연결 완료 (테스트 필요)
□ Phase 4: 검증 완료 (진짜 완료) ✅
```

---

## ⚠️ 주의

```
"완료"라고 말하기 전에 반드시:
1. 이 체크리스트 실행
2. 직접 앱에서 확인
3. Gate PASS 확인

셋 다 통과해야 "완료"
```
