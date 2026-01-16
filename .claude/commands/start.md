# /start - 프로젝트 온보딩 (Shovel v2 + Boris Workflow)

> **핵심 원칙**
> - Boris Cherny 방식: 병렬 세션으로 생산성 극대화
> - Gate PASS만이 진실
> - PRD가 법

---

## 전체 플로우

```
/start
    │
    ├── Phase -1: 병렬 환경 세팅 (Boris #1) ⭐ NEW
    │   └── tmux 5개 창 + 세션 관리
    │
    ├── Phase 0: 프로젝트 상태 판별 (Dynamic Strategy)
    │   └── 복잡도에 따라 전략 결정
    │
    ├── Phase 1: 환경 스캔 (ReAct)
    │   └── Thought → Action → Observation 루프
    │
    ├── Phase 2: 프로젝트 타입 감지 (핵심 - 모든 이론 적용)
    │   ├── Tree of Thoughts: 다중 가설 탐색
    │   ├── Self-Consistency: 3가지 방법 투표
    │   ├── Chain of Verification: 독립적 검증
    │   └── LLM-as-Judge: 최종 자기 평가
    │
    ├── Phase 3: PRD 확인/생성
    ├── Phase 4: 아키텍처 결정 (Self-Reflection)
    ├── Phase 5: CLAUDE.md 생성
    ├── Phase 6: Gate 시스템 설정
    │
    └── Phase 7: 최종 검증 (Chain of Verification)
        └── 전체 결과 독립 검증
```

---

## Phase -1: 병렬 환경 세팅 (Boris Workflow) ⭐

> **Boris Cherny**: "스타크래프트처럼 - 유닛을 직접 조작하는 게 아니라 자율 유닛들을 지휘"

### -1.1 tmux 세션 확인

```bash
# 현재 세션 목록
tmux ls
```

### -1.2 신규 프로젝트면 세션 생성

```bash
# 프로젝트 폴더에서 실행 (tmux 밖에서!)
cd /your/project/path
./scripts/parallel-terminals.sh
```

**자동 생성되는 5개 창:**

| 창 | 용도 | 명령 예시 |
|---|------|---------|
| 1-Main | 핵심 기능 구현 | `claude "API 구현해줘"` |
| 2-Test | 테스트 작성 | `claude "테스트 작성해줘"` |
| 3-Refactor | 리팩토링 | `claude "정리해줘"` |
| 4-Docs | 문서화 | `claude "README 작성해줘"` |
| 5-Review | 코드 리뷰 | `claude "리뷰해줘"` |

### -1.3 기존 세션 있으면 연결

```bash
# 세션 연결
tmux attach -t {프로젝트명}

# 세션 간 전환 (tmux 안에서)
Ctrl+B, S  →  목록에서 선택
```

### -1.4 tmux 필수 단축키

| 키 | 기능 |
|---|------|
| `Ctrl+B, D` | 세션에서 나오기 (detach) |
| `Ctrl+B, S` | 세션 목록 (전환) |
| `Ctrl+B, N/P` | 다음/이전 창 |
| `Ctrl+B, 1-5` | 창 직접 이동 |

### -1.5 환경 준비 확인

```markdown
## ✅ 병렬 환경 체크리스트

- [ ] tmux 세션 생성됨
- [ ] 5개 창 확인됨
- [ ] 프로젝트 디렉토리에 있음

준비되었으면 Phase 0으로 진행!
```

---

## Phase 0: 프로젝트 상태 판별 + 전략 결정

### 0.1 기본 스캔

```bash
# CLAUDE.md 존재?
test -f CLAUDE.md && echo "EXISTS" || echo "NOT_FOUND"

# 소스 파일 수
FILE_COUNT=$(find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | wc -l)
echo "FILES: $FILE_COUNT"

# 디렉토리 깊이
MAX_DEPTH=$(find . -type d -not -path '*/node_modules/*' -not -path '*/.git/*' \
  2>/dev/null | awk -F/ '{print NF-1}' | sort -n | tail -1)
echo "DEPTH: $MAX_DEPTH"
```

### 0.2 Dynamic Strategy 결정 (DeepSeek-R1)

```
┌─────────────────────────────────────────────────────┐
│            복잡도 기반 전략 결정                      │
├─────────────────────────────────────────────────────┤
│ 복잡도   │ 파일 수    │ 전략        │ Phase 수     │
├─────────────────────────────────────────────────────┤
│ 단순     │ <20       │ Fast Track  │ 4 (압축)     │
│ 보통     │ 20-100    │ Standard    │ 7 (전체)     │
│ 복잡     │ 100+      │ Deep Scan   │ 8 (확장)     │
└─────────────────────────────────────────────────────┘
```

### 0.3 전략 적용

```markdown
## 🎯 Dynamic Strategy 선택

**감지된 복잡도**: {단순/보통/복잡}
**파일 수**: {N}개
**선택된 전략**: {Fast Track / Standard / Deep Scan}

### 전략별 차이

| 전략 | 감지 방법 수 | 검증 깊이 | 예상 시간 |
|------|------------|----------|----------|
| Fast Track | 2개 | 기본 | ~30초 |
| Standard | 3개 | CoVe 4단계 | ~1분 |
| Deep Scan | 4개 | ToT + 백트래킹 | ~2분 |

이 전략으로 진행할까요?
> **(y)** 진행
> **(c)** 전략 변경
```

---

## Phase 1: 환경 스캔 (ReAct 패턴)

### ReAct 루프 실행

```
┌─────────────────────────────────────────────────────┐
│ ReAct Loop: Thought → Action → Observation          │
└─────────────────────────────────────────────────────┘

[Thought 1]
현재 환경의 Node.js 버전을 확인해야 함

[Action 1]
node -v

[Observation 1]
v20.10.0

[Thought 2]
Node.js 20.x 확인됨. 패키지 매니저 확인 필요

[Action 2]
pnpm -v || npm -v

[Observation 2]
pnpm: 8.15.0

[Thought 3]
pnpm 8.x 확인됨. package.json 분석 필요

[Action 3]
cat package.json | head -50

[Observation 3]
{
  "name": "my-project",
  "dependencies": {
    "next": "15.0.0",
    ...
  }
}

[Thought 4]
Next.js 15 의존성 발견. 프로젝트 타입 감지 Phase로 이동
```

### 환경 스캔 결과

```markdown
## 📊 환경 스캔 결과 (ReAct)

| 항목 | 값 | 상태 |
|------|-----|------|
| Node.js | {버전} | ✅/❌ |
| Package Manager | {pnpm/npm} | ✅/❌ |
| TypeScript | {버전} | ✅/❌ |

### ReAct Trace
```
Thought → Action → Observation (반복)
총 {N}회 루프 실행
```
```

---

## Phase 2: 프로젝트 타입 감지 (핵심 - 모든 이론 적용)

### 2.1 Tree of Thoughts: 다중 가설 탐색

```
┌─────────────────────────────────────────────────────┐
│           Tree of Thoughts 탐색                      │
└─────────────────────────────────────────────────────┘

                    [Root: 프로젝트 타입?]
                            │
            ┌───────────────┼───────────────┐
            ↓               ↓               ↓
       [가설 A]        [가설 B]        [가설 C]
        Next.js         Electron         Vite
            │               │               │
     ┌──────┴──────┐   ┌───┴───┐      ┌───┴───┐
     ↓             ↓   ↓       ↓      ↓       ↓
 [App Router] [Pages]  [✗]    [✗]   [React] [Vue]
     │                                  │
    ✅                                 ✅
 확신도:90%                         확신도:70%
```

### ToT 탐색 실행

```bash
# 가설 A: Next.js 검증
echo "=== 가설 A: Next.js ===" 
test -f next.config.js -o -f next.config.ts && echo "next.config: YES" || echo "next.config: NO"
test -d app && echo "app/: YES" || echo "app/: NO"
test -d pages && echo "pages/: YES" || echo "pages/: NO"
grep -q '"next"' package.json && echo "dependency: YES" || echo "dependency: NO"

# 가설 B: Electron 검증
echo "=== 가설 B: Electron ===" 
test -d main && echo "main/: YES" || echo "main/: NO"
test -d renderer && echo "renderer/: YES" || echo "renderer/: NO"
grep -q '"electron"' package.json && echo "dependency: YES" || echo "dependency: NO"

# 가설 C: Vite (순수) 검증
echo "=== 가설 C: Vite ===" 
test -f vite.config.ts && echo "vite.config: YES" || echo "vite.config: NO"
! test -f next.config.ts && echo "not-next: YES" || echo "not-next: NO"
```

### ToT 결과 + 백트래킹

```markdown
## 🌳 Tree of Thoughts 결과

| 가설 | 증거 점수 | 확신도 | 상태 |
|------|----------|--------|------|
| A: Next.js | 4/4 | 95% | ✅ 선택 |
| B: Electron | 0/3 | 0% | ❌ 백트래킹 |
| C: Vite | 1/2 | 30% | ❌ 백트래킹 |

**ToT 결론**: Next.js (App Router)
```

---

### 2.2 Self-Consistency: 3가지 방법으로 투표

```
┌─────────────────────────────────────────────────────┐
│         Self-Consistency 다수결 투표                  │
└─────────────────────────────────────────────────────┘

방법 1: package.json 의존성 분석
  → 결과: Next.js

방법 2: 파일 구조 패턴 분석
  → 결과: Next.js

방법 3: import 패턴 분석
  → 결과: Next.js

투표 결과: Next.js (3/3) ✅ 만장일치
```

### Self-Consistency 실행

```bash
# 방법 1: 의존성 기반
METHOD1=$(cat package.json | grep -E '"next"|"electron"|"vite"' | head -1 | \
  sed 's/.*"next".*/Next.js/; s/.*"electron".*/Electron/; s/.*"vite".*/Vite/')

# 방법 2: 파일 구조 기반
if test -d app && test -f next.config.ts; then
  METHOD2="Next.js"
elif test -d main && test -d renderer; then
  METHOD2="Electron"
else
  METHOD2="Vite"
fi

# 방법 3: import 패턴 기반
METHOD3=$(grep -rh "from ['\"]next" src 2>/dev/null | head -1 | \
  awk '{if(NF>0) print "Next.js"; else print "Unknown"}')

echo "방법1: $METHOD1"
echo "방법2: $METHOD2"
echo "방법3: $METHOD3"
```

### 투표 결과

```markdown
## 🗳️ Self-Consistency 투표

| 방법 | 결과 | 확신도 |
|------|------|--------|
| 의존성 분석 | {결과} | {%} |
| 파일 구조 | {결과} | {%} |
| Import 패턴 | {결과} | {%} |

**투표 결과**: {최다 득표} ({N}/3)

| 일치도 | 판정 |
|--------|------|
| 3/3 | ✅ 확정 |
| 2/3 | ⚠️ 사용자 확인 |
| 1/3 | ❌ 재분석 필요 |
```

---

### 2.3 Chain of Verification (CoVe): 4단계 독립 검증

```
┌─────────────────────────────────────────────────────┐
│      Chain of Verification 4단계                     │
└─────────────────────────────────────────────────────┘

Step 1: 초안 (Draft)
────────────────────
"이 프로젝트는 Next.js App Router로 보임"

Step 2: 검증 질문 생성 (Plan)
────────────────────
Q1: package.json에 "next" 의존성이 있는가?
Q2: app/ 또는 pages/ 폴더가 존재하는가?
Q3: next.config.ts 또는 next.config.js가 있는가?
Q4: 'next/...'에서 import하는 파일이 있는가?

Step 3: 독립적 답변 (Execute) ← 초안 안 보고!
────────────────────
A1: Yes (next: "15.0.0")
A2: Yes (app/ 존재)
A3: Yes (next.config.ts)
A4: Yes (15개 파일에서 발견)

Step 4: 최종 검증 (Verify)
────────────────────
4/4 통과 → "Next.js 15 (App Router)" 확정
```

### CoVe 실행

```bash
# Step 3: 독립적 답변 (초안과 별개로 실행)
echo "=== CoVe Step 3: Independent Verification ==="

# Q1 독립 답변
Q1_ANSWER=$(grep '"next"' package.json 2>/dev/null && echo "YES" || echo "NO")

# Q2 독립 답변  
Q2_ANSWER=$(test -d app -o -d pages && echo "YES" || echo "NO")

# Q3 독립 답변
Q3_ANSWER=$(test -f next.config.ts -o -f next.config.js && echo "YES" || echo "NO")

# Q4 독립 답변
Q4_COUNT=$(grep -r "from ['\"]next" src 2>/dev/null | wc -l)
Q4_ANSWER=$([ $Q4_COUNT -gt 0 ] && echo "YES ($Q4_COUNT files)" || echo "NO")

echo "Q1: $Q1_ANSWER"
echo "Q2: $Q2_ANSWER"
echo "Q3: $Q3_ANSWER"
echo "Q4: $Q4_ANSWER"
```

### CoVe 결과

```markdown
## ✅ Chain of Verification 결과

| 질문 | 답변 | 상태 |
|------|------|------|
| next 의존성? | {답변} | ✅/❌ |
| app/pages 폴더? | {답변} | ✅/❌ |
| next.config 파일? | {답변} | ✅/❌ |
| next import? | {답변} | ✅/❌ |

**CoVe 점수**: {N}/4
**검증 결과**: {통과/실패}
```

---

### 2.4 LLM-as-Judge: 최종 자기 평가

```
┌─────────────────────────────────────────────────────┐
│           LLM-as-Judge 자기 평가                     │
└─────────────────────────────────────────────────────┘

[Judge 역할로 전환]

평가 대상:
- ToT 결론: Next.js (95%)
- Self-Consistency: Next.js (3/3)
- CoVe: 4/4 통과

Judge 체크리스트:
☑ ToT에서 백트래킹 필요했나? → 아니오, 첫 가설 확정
☑ 투표가 만장일치인가? → 예, 3/3
☑ CoVe 모든 질문 통과? → 예, 4/4
☑ 불일치하는 증거 있나? → 없음

Judge 판정: ✅ PASS
최종 확신도: 97%
```

### Judge 결과

```markdown
## ⚖️ LLM-as-Judge 판정

### 평가 항목

| 항목 | 결과 | 가중치 |
|------|------|--------|
| ToT 확신도 | {%} | 30% |
| Self-Consistency | {N}/3 | 30% |
| CoVe 통과율 | {N}/4 | 30% |
| 불일치 증거 | {없음/있음} | 10% |

### 최종 판정

**점수**: {종합 점수}%
**판정**: ✅ PASS / ⚠️ REVIEW / ❌ RETRY

| 점수 | 판정 | 조치 |
|------|------|------|
| 90%+ | PASS | 확정 |
| 70-89% | REVIEW | 사용자 확인 |
| <70% | RETRY | 재분석 |
```

---

### 2.5 Self-Reflection (DeepSeek-R1)

```markdown
## 🔍 Self-Reflection

### 이번 감지에서 배운 것

**잘된 점**:
- 3가지 방법 모두 일치
- CoVe 검증 통과

**개선점**:
- (있다면 ERROR_LOG에 기록)

### 판단 근거 요약

```
1차 감지 (ToT): Next.js → 확신도 95%
2차 확인 (Self-Consistency): 3/3 일치
3차 검증 (CoVe): 4/4 통과
최종 평가 (Judge): PASS

결론: Next.js 15 (App Router) 확정
```
```

---

## Phase 3: PRD 확인/생성

### 3.1 PRD 존재 확인

```bash
test -f docs/PRD.md -o -f PRD.md && echo "EXISTS" || echo "NOT_FOUND"
```

### 3.2 PRD 없으면 유도

```markdown
## ⚠️ PRD 없음

**PRD가 법입니다.** PRD 없이 구현은 불가합니다.

### 옵션 선택

> **(1)** 지금 PRD 인터뷰 시작 (권장)
> **(2)** claude.ai에서 PRD 작성 후 다시 /start
> **(3)** 간단한 PRD 자동 생성 (테스트용)

선택: ___
```

### 3.3 PRD 인터뷰 (옵션 1 선택 시)

```markdown
### PRD 인터뷰

**Q1. 프로젝트 이름?** ___
**Q2. 한 줄 설명?** ___
**Q3. 핵심 기능 3가지?**
  1. ___
  2. ___
  3. ___
**Q4. 타겟 사용자?** ___
**Q5. 기술 스택?** ___
```

---

## Phase 4: 아키텍처 결정 + Self-Reflection

### 4.1 복잡도 판정 (Dynamic Strategy 적용)

```
┌─────────────────────────────────────────────────────┐
│         아키텍처 Self-Reflection                     │
└─────────────────────────────────────────────────────┘

[Thought] 파일 수와 모듈 구조를 분석해야 함

[Action] 파일/폴더 구조 분석
find . -type f -name "*.ts" | wc -l
find . -type d -maxdepth 2 | head -20

[Observation]
- 파일: 45개
- 모듈: 4개 (auth, user, product, order)

[Self-Reflection]
"45개 파일, 4개 모듈 → '보통' 복잡도
Module 구조가 적절함"

[Re-evaluate]
"PRD의 기능 수(3개)와 모듈 수(4개)가 일치하지 않음
→ 사용자 확인 필요"
```

### 4.2 구조 결정

| 복잡도 | 구조 | 예시 |
|--------|------|------|
| 단순 (<20 파일) | Flat | src/{components,utils} |
| 보통 (20-100) | Module | src/{core,modules,app} |
| 복잡 (100+) | Fractal | src/modules/{feature}/{core,workers} |

### 4.3 사용자 확인

```markdown
### 🔍 아키텍처 확인

**복잡도**: {판정} ({파일 수}개)
**구조**: {Flat/Module/Fractal}

**Self-Reflection 결과**:
{개선점 또는 주의사항}

맞나요?
> **(y)** 맞음 → 진행
> **(n)** 수정

선택: ___
```

---

## Phase 5: CLAUDE.md 생성

### 5.1 템플릿 선택

```bash
# 타입에 맞는 템플릿
cp .claude/templates/{type}.claude.md CLAUDE.md
```

### 5.2 프로젝트 정보 주입

```markdown
# {프로젝트명}

> Shovel Development System v2

## 감지 결과 (7 Theories 적용)

| 이론 | 결과 |
|------|------|
| Tree of Thoughts | {확신도}% |
| Self-Consistency | {N}/3 |
| Chain of Verification | {N}/4 |
| LLM-as-Judge | {PASS/REVIEW} |

## 프로젝트 개요
- **타입**: {감지된 타입}
- **환경**: {WSL/PowerShell}
- **복잡도**: {판정}
- **전략**: {Fast Track/Standard/Deep Scan}

[... 나머지 템플릿 내용 ...]
```

---

## Phase 6: Gate 시스템 설정

### 6.1 package.json scripts 확인

```bash
cat package.json | grep -E '"lint"|"test"|"build"|"gate"'
```

### 6.2 없으면 추가

```markdown
### ⚠️ Gate 스크립트 필요

```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx",
    "test": "vitest run",
    "build": "tsc && vite build",
    "gate": "bash scripts/gate.sh"
  }
}
```

추가할까요? **(y/n)**
```

### 6.3 gate.sh 복사

```bash
mkdir -p scripts
cp .claude/templates/gate.sh scripts/gate.sh
chmod +x scripts/gate.sh
```

---

## Phase 7: 최종 검증 (Chain of Verification)

### 전체 /start 결과 검증

```
┌─────────────────────────────────────────────────────┐
│      Final Chain of Verification                     │
└─────────────────────────────────────────────────────┘

Step 1: /start 결과 초안
────────────────────
"Next.js 프로젝트, Module 구조, Standard 전략으로 설정 완료"

Step 2: 최종 검증 질문
────────────────────
Q1: CLAUDE.md가 생성되었는가?
Q2: 선택된 타입과 템플릿이 일치하는가?
Q3: Gate 스크립트가 설정되었는가?
Q4: PRD가 존재하거나 생성되었는가?
Q5: 이전 /start 실패 이력이 있다면 해결되었는가?

Step 3: 검증 실행
────────────────────
A1: ✅ CLAUDE.md 존재
A2: ✅ Next.js - web.claude.md
A3: ✅ scripts/gate.sh 존재
A4: ✅ docs/PRD.md 존재
A5: ✅ 이전 실패 없음 (또는 해결됨)

Step 4: 최종 판정
────────────────────
5/5 통과 → /start 성공
```

---

## 완료 메시지

```markdown
## ✅ Shovel v2 온보딩 완료

### 적용된 이론들

| 이론 | 적용 단계 | 결과 |
|------|----------|------|
| DeepSeek-R1 | Phase 0, 4 | Dynamic Strategy |
| ReAct | Phase 1 | Thought-Action-Obs |
| Tree of Thoughts | Phase 2 | {확신도}% |
| Self-Consistency | Phase 2 | {N}/3 |
| Chain of Verification | Phase 2, 7 | {N}/4 |
| LLM-as-Judge | Phase 2 | {PASS} |
| Reflexion | 전체 | ERROR_LOG 연동 |

### 감지 결과

| 항목 | 값 |
|------|-----|
| 타입 | {감지된 타입} |
| 환경 | {WSL/PowerShell} |
| 복잡도 | {판정} |
| 전략 | {선택된 전략} |
| 최종 확신도 | {%} |

### 생성된 파일

| 파일 | 용도 |
|------|------|
| `CLAUDE.md` | 프로젝트 규칙 |
| `scripts/gate.sh` | Gate 스크립트 |
| `.claude/evidence/detection.json` | 감지 증거 |

### 다음 단계

```
/plan → /implement → /gate → /review → 커밋
```

**Gate PASS만이 진실입니다.**
```

---

## Resume 플로우 (기존 프로젝트)

기존 프로젝트 감지 시:

### R1: Reflexion - 이전 상태 확인

```bash
# 이전 ERROR_LOG 확인
grep -A 5 "## ERROR_LOG" CLAUDE.md | head -10

# 이전 /start 실패 이력?
cat .claude/evidence/start-history.json 2>/dev/null | tail -5
```

### R2: 구조 분석 (ReAct)

```
[Thought] 기존 구조와 CLAUDE.md 일치 여부 확인 필요
[Action] find . -type d -maxdepth 3
[Observation] {실제 구조}
[Thought] CLAUDE.md의 구조와 비교 필요
```

### R3: 불일치 감지 (Self-Reflection)

```markdown
### CLAUDE.md vs 실제 구조

| 항목 | CLAUDE.md | 실제 | 일치 |
|------|-----------|------|------|
| 모듈 수 | {N} | {M} | ✅/❌ |
| 타입 | {기록} | {감지} | ✅/❌ |

불일치 항목이 있으면:
→ CLAUDE.md 업데이트 또는 구조 수정
```

### R4: 미완료 작업 식별

```bash
# TODO/FIXME
grep -rn "TODO\|FIXME" src --include="*.ts" | head -10

# Gate 실패 이력
cat EVIDENCE.md 2>/dev/null | grep "Status"
```

### R5: 다음 할 일 제안

```markdown
### 권장 다음 작업

1. **Gate 실패 수정** (실패 시)
2. **미완성 모듈 완료**
3. **TODO 처리**
4. **테스트 추가**

선택: ___
```

---

## ERROR_LOG 연동 (Reflexion)

### /start 실패 시

```markdown
## ERROR_LOG 업데이트

### 에러
- 시점: /start Phase {N}
- 증상: {증상}
- 원인: {원인}

### 5 Whys
1. 왜? {답}
2. 왜? {답}
...

### 학습된 규칙
**NEVER**: {다시는 하지 말 것}
**ALWAYS**: {항상 할 것}
```

이 내용은 CLAUDE.md의 ERROR_LOG 섹션에 자동 추가됩니다.

---

## 감지 증거 저장

### detection.json 형식

```json
{
  "timestamp": "2026-01-09T12:00:00Z",
  "version": "shovel-v2",
  "strategy": "Standard",
  "theories_applied": {
    "tree_of_thoughts": {
      "hypotheses": ["Next.js", "Electron", "Vite"],
      "selected": "Next.js",
      "confidence": 95
    },
    "self_consistency": {
      "method1": "Next.js",
      "method2": "Next.js", 
      "method3": "Next.js",
      "agreement": "3/3"
    },
    "chain_of_verification": {
      "q1": true,
      "q2": true,
      "q3": true,
      "q4": true,
      "score": "4/4"
    },
    "llm_as_judge": {
      "verdict": "PASS",
      "final_confidence": 97
    }
  },
  "result": {
    "type": "Next.js",
    "environment": "WSL",
    "template": "web.claude.md",
    "complexity": "보통",
    "architecture": "Module"
  }
}
```

---

## 이론별 적용 요약

| Phase | 적용 이론 | 목적 |
|-------|----------|------|
| 0 | DeepSeek-R1 (Dynamic Strategy) | 복잡도별 전략 결정 |
| 1 | ReAct | 환경 스캔 루프 |
| 2 | Tree of Thoughts | 다중 가설 탐색 |
| 2 | Self-Consistency | 3가지 방법 투표 |
| 2 | Chain of Verification | 4단계 독립 검증 |
| 2 | LLM-as-Judge | 최종 자기 평가 |
| 4 | DeepSeek-R1 (Self-Reflection) | 아키텍처 재평가 |
| 7 | Chain of Verification | 전체 결과 검증 |
| 전체 | Reflexion | 실패 시 학습 |
