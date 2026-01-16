---
name: step-done
description: Step/기능 완료 시 호출 - 필수 플로우 자동 시작
---

# Step Done - 필수 플로우 트리거

> **규칙**: 기능 완료 = 플로우 전체 실행. 건너뛰기 금지.

## 🔄 필수 플로우 (순서대로)

```
기능 완료
   ↓
1️⃣ /check-complete  ← 껍데기/미연결 검사
   ↓
2️⃣ /gate            ← lint, test, build
   ↓
3️⃣ /handoff         ← 의도 기록
   ↓
4️⃣ /clear           ← Context Bias 제거
   ↓
5️⃣ /verify          ← 새 눈으로 검증
   ↓
✅ 커밋
```

---

## 플로우 실행

### 1️⃣ /check-complete 실행

**껍데기 검사:**
- [ ] TODO/FIXME 없음
- [ ] 모든 함수에 실제 로직
- [ ] 하드코딩 더미 없음
- [ ] console.log만 있는 핸들러 없음

**연결 검사:**
- [ ] export → import 체인 완성
- [ ] 라우팅 등록됨
- [ ] UI에서 접근 가능

**동작 검사:**
- [ ] 앱 실행 성공
- [ ] 해당 기능 접근 가능
- [ ] 핵심 동작 확인됨

### 2️⃣ /gate 실행

```bash
pnpm lint && pnpm test && pnpm build
```

### 3️⃣ /handoff 기록

```markdown
## 이 기능의 기록

### 의도
{무엇을 왜 만들었는지}

### 결정사항
{어떤 선택을 왜 했는지}

### 주의점
{다음에 알아야 할 것}
```

### 4️⃣ /clear 권장

```
Context Bias 제거를 위해 /clear 실행을 권장합니다.

[Claude Code] /clear 명령어 실행
[claude.ai 웹] 새 대화 시작
```

### 5️⃣ /verify 실행

새로운 눈으로 검증:
- 기능이 의도대로?
- 엣지 케이스?
- 에러 핸들링?
- 코드 품질?

---

## ⚠️ 주의

```
❌ 플로우 중간에 건너뛰기 금지
❌ check-complete 없이 gate 금지
❌ verify 없이 커밋 금지

✅ 매 기능마다 전체 플로우 실행
✅ 실패하면 처음부터
✅ 전체 통과 = 진짜 완료
```
