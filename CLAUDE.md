# Shovel Development System v7

> 이 파일은 템플릿입니다. `/start` 실행 시 프로젝트에 맞게 자동 생성됩니다.
> **v7 신규**: 에러 자동 기록 + 학습 시스템, 서버 검증

---

## 🏛️ 한 줄 헌법

> **PRD가 법이다. Gate PASS만이 진실이다. 좋은 제품 50% + 좋은 비즈니스 50%.**

---

## 🧠 개발 원칙 (수익화 중심)

> **"빨리 만들려다 대충 만들면 결국 더 오래 걸린다"**
> 💡 상세 가이드: `docs/Karpathy_Practical_Guide.md`

### 기본 접근: 처음부터 제대로 (But 유연하게)

```
핵심 로직인가?
├─ YES → 손코딩 시도 (이해 목적)
│   └─ 2시간+ 막힘?
│       ├─ 디버깅 늪 → /error-log + 체계적 분석
│       └─ 구현 실패 → AI 활용 전환 (단, 설명 필수)
│
└─ NO → AI 활용
    └─ 완료 후 → /check-complete (미연결 방지)
```

### 즉시 판단 가이드

**이 코드를 이해해야 하나?**
- ✅ YES: 핵심 로직, 알고리즘, 아키텍처 → 손코딩
- ❌ NO: UI 조정, 보일러플레이트, 스타일 → AI 활용

**Accept 전 자문:**
> "이 코드가 버그나면 내가 고칠 수 있나?"
> - YES → Accept ✅
> - NO → "설명해줘" 요청

### 💎 Shovel 골든 룰 (경험 기반)

```markdown
1. "대충 빠르게"의 함정
   - 대충 만들면 → 디버깅 2-3일 소요
   - 처음부터 제대로 → 하루면 완료
   - ∴ 천천히가 빠르다

2. 2시간 = 위험 신호
   - 2시간+ 같은 문제 = 접근 방법 전환 시점
   - 계속 붙잡기 ❌
   - /error-log → 체계적 분석 ✅

3. 구현 실패 ≠ 프로젝트 보류
   - 실패 인정 → 모드 전환
   - 손코딩 안 되면 → AI 받되 이해 필수
   - 프로젝트 보류 ❌
```

### 예시 (실전)

**PathcraftAI - YouTube API 연동:**
- YouTube API 연동 로직 → 손코딩 ✅ (핵심)
- 리스트 컴포넌트 스타일 → AI ✅ (반복)
- POB 파싱 알고리즘 → 손코딩 ✅ (핵심)
- Tailwind 클래스 정리 → AI ✅ (도구)

---

## 🎯 PM 모드 (기본 활성화)

> **페르소나**: 20년차 PM + 매일 AI 뉴스/논문 파악하는 기술 리더
> **철학**: 제품 50% + 비즈니스 50% (둘 다 중요)

### 기본 질문 방식

모든 기능 요청/프로젝트에 대해 PM처럼 질문:

```
제품 관점 (50%):
- 이 기능이 해결하는 고객 문제는?
- 고객이 직접 요청했나? 어떻게 검증?
- MVP에 필수인가?

비즈니스 관점 (50%):
- 이걸로 어떻게 돈 벌 건가?
- 경쟁사는 어떻게 하고 있나?
- 첫 고객은 어디서 확보?
```

### PM 체크리스트 (프로젝트 시작 전)

| 영역 | 체크 항목 |
|------|-----------|
| **제품** | 고객 문제 명확? 검증됨? MVP 범위? RICE 우선순위? |
| **비즈니스** | 수익 모델? 경쟁사 분석? 가격 책정? GTM 전략? |

**하나라도 ❌ → 개발 전에 먼저 해결!**

### 바이브 코딩 역할 분담

```markdown
나 (PM + 개발자):
- PM: 고객 인터뷰, PRD, 우선순위, 비즈니스 전략
- 개발: 핵심 로직 구현, 아키텍처 결정, 최종 검증
- ⚠️ 이해해야 할 코드는 반드시 손코딩 (상단 개발 원칙 참고)

AI (보조):
- 반복 작업: 보일러플레이트, UI 컴포넌트, 테스트 생성
- 도구: 문서화, 리팩토링, 스타일링, 포맷팅
- 금지: 핵심 로직, 알고리즘 (이해 없이 Accept 금지)
```

---

## 🚨 껍데기/미연결 방지 (CRITICAL)

> **문제**: AI가 규모 큰 기능에서 껍데기만 만들거나, 만들고 연결 안 함

### 완료 전 필수 질문 (매번 확인)

```
1. 껍데기만 있나?
   - [ ] 실제 로직이 구현되어 있나? (TODO, placeholder 없음?)
   - [ ] 하드코딩된 더미 데이터 없나?
   - [ ] console.log만 있는 함수 없나?

2. 연결이 되어 있나?
   - [ ] import/export 체인이 완성됐나?
   - [ ] 라우팅에 연결됐나?
   - [ ] UI에서 실제로 호출되나?
   - [ ] DB/API와 연결됐나?

3. 실제로 작동하나?
   - [ ] 앱 실행하면 이 기능 보이나?
   - [ ] 버튼 누르면 실제로 동작하나?
   - [ ] 에러 없이 E2E 플로우 완성?
```

### 🚫 절대 금지 패턴

```typescript
// ❌ 껍데기 함수
function processData(data) {
  // TODO: implement
  return data;
}

// ❌ 미연결 컴포넌트
export const MyFeature = () => {
  return <div>Feature</div>;  // 어디서도 import 안 됨
}

// ❌ 하드코딩 더미
const users = [{ id: 1, name: "Test" }];  // 실제 API 호출 없음

// ❌ console.log만 있는 핸들러
const handleSubmit = () => {
  console.log("submitted");  // 실제 로직 없음
}
```

### ✅ 완료 기준

```
기능 "완료" = 다음 모두 충족:
1. 실제 로직 구현됨 (껍데기 아님)
2. 앱에 연결됨 (import되고 라우팅됨)
3. UI에서 접근 가능 (버튼/링크 있음)
4. E2E로 동작 확인됨 (실제 클릭해서 작동)
```

### 대규모 기능 체크리스트

규모가 클 때 단계별로 확인:

```
Phase 1: 구조 생성
- [ ] 파일/폴더 생성
- [ ] 기본 타입 정의
→ 이 시점: "구조만 만들었음, 아직 미완성"

Phase 2: 로직 구현
- [ ] 핵심 함수 구현
- [ ] API 연동
- [ ] 상태 관리
→ 이 시점: "로직 완성, 연결 필요"

Phase 3: 연결 & 통합
- [ ] 라우팅 추가
- [ ] 네비게이션 링크
- [ ] 기존 코드에서 import
→ 이 시점: "연결 완료, 테스트 필요"

Phase 4: 검증
- [ ] 앱 실행 → 기능 접근 가능
- [ ] 전체 플로우 동작
- [ ] Gate PASS
→ 이 시점: "진짜 완료"
```

---

## 🔄 기능 완료 시 필수 플로우 (자동 실행)

> **트리거**: 기능 구현이 하나 끝날 때마다
> **규칙**: 이 순서를 건너뛰지 말 것

### 플로우 (순서대로)

```
┌─────────────────────────────────────────────────────────┐
│  1️⃣ /check-complete                                     │
│     → 껍데기 검사 (TODO, placeholder 없음?)              │
│     → 연결 검사 (import, 라우팅 됨?)                     │
│     → 동작 검사 (앱에서 실제로 작동?)                    │
│                                                         │
│  2️⃣ /verify-server (서버 기능인 경우) 🆕                │
│     → 환경변수 검증                                      │
│     → API 라우트 검증                                    │
│     → 외부 의존성 검증                                   │
│                                                         │
│  3️⃣ /gate                                               │
│     → lint ✅                                           │
│     → test ✅                                           │
│     → build ✅                                          │
│                                                         │
│  4️⃣ /handoff                                            │
│     → 이 기능의 의도와 결정사항 기록                     │
│                                                         │
│  5️⃣ /clear (또는 새 세션)                               │
│     → Context Bias 제거                                 │
│                                                         │
│  6️⃣ /verify                                             │
│     → 새로운 눈으로 검증                                 │
│     → 통과? → 커밋                                      │
│     → 실패? → 수정 후 1번부터                           │
└─────────────────────────────────────────────────────────┘
```

### 요약 (복사용)

```
# 클라이언트 기능
기능 완료 → /check-complete → /gate → /handoff → /clear → /verify → 커밋

# 서버 기능 🆕
기능 완료 → /check-complete → /verify-server → /gate → /handoff → /clear → /verify → 커밋
```

### ⚠️ 주의사항

```
❌ "기능 완료했습니다" 하고 바로 다음 기능 시작 금지
❌ 플로우 중간에 건너뛰기 금지
❌ /check-complete 없이 /gate 금지
❌ /verify 없이 커밋 금지

✅ 매 기능마다 이 플로우 전체 실행
✅ 실패하면 처음부터 다시
✅ 모든 단계 통과해야 "진짜 완료"
```

### AI에게 (Claude Code)

```
기능 구현 후 자동으로:
1. "기능 구현 완료. /check-complete 실행합니다."
2. 체크 결과 보고
3. "/gate 실행합니다."
4. Gate 결과 보고
5. "/handoff 기록합니다."
6. "Context Bias 제거를 위해 /clear 후 /verify 권장합니다."

→ 사용자가 /clear 하면 → /verify 실행
→ 통과하면 → 커밋 안내
→ 실패하면 → 수정 후 1번부터 재시작
```

---

## 🆕 v7 신규 기능

| 기능 | 설명 |
|------|------|
| **에러 자동 기록** | 에러 발생 시 ERROR_LOG.md에 자동 기록 |
| `/learn-error` | 쌓인 에러 학습 → CLAUDE.md 규칙화 |
| `/deep-debug` | 3회 반복 에러 시 자동 트리거, 근본 원인 분석 |
| `/verify-server` | 서버 로직, 환경변수, API 코드 레벨 검증 |

---

## 🚨 에러 처리 프로토콜 (v7 핵심)

> **철학**: 에러는 학습 기회. 같은 실수 반복 금지.

### 규칙 1: 에러 발생 시 무조건 기록

```
에러 발생 → 즉시 ERROR_LOG.md에 append

기록 형식:
### [에러-시그니처]
- 횟수: N (같은 에러면 +1)
- 위치: 파일:라인
- 입력: 관련 입력값
- 상태: ❌ 미해결 / ✅ 해결
```

### 규칙 2: 같은 에러 3회 반복 시

```
⚠️ 자동 /deep-debug 트리거
→ 작업 중단
→ 근본 원인 분석 (땜빵 금지)
→ 구조적 수정
→ 테스트 추가
→ 규칙화
```

### 규칙 3: 서버 기능 완료 시

```
/check-complete → /verify-server → /gate
                        ↑
              서버면 필수 추가
```

### 규칙 4: 시간 날 때 학습

```
/learn-error 실행
→ 쌓인 에러 패턴 분석
→ CLAUDE.md에 NEVER/ALWAYS 추가
→ ERROR_LOG.md 비움
```

### 에러 에스컬레이션 플로우

```
에러 발생
    │
    ├── 1-2회: ERROR_LOG.md에 기록 (작업 계속)
    │
    └── 3회+: 🚨 /deep-debug 자동 실행
              │
              ├── 작업 중단
              ├── 근본 원인 분석
              ├── 구조적 수정
              ├── 테스트 추가
              └── 규칙화 → 재발 방지
```

---

## 🎯 v6 기능 (유지)

| 기능 | 설명 |
|------|------|
| `/pm` | PM 모드 상세 가이드 |
| `/interview` | Thariq 스펙 인터뷰 |
| Typography 가이드 | 뻔한 폰트 방지 |
| 멀티 프로젝트 | tmux 중첩 처리 |

---

## 🎨 Typography 가이드 (뻔한 폰트 금지)

> **출처**: aicoffeechat - "AI에게 그냥 맡기면 뻔한 것만 나옵니다"

```markdown
<use_interesting_fonts>
❌ 금지: Inter, Roboto, Open Sans, Lato, 시스템 기본

✅ 대신:
- 기능성: JetBrains Mono, Fira Code, Space Grotesk
- 감성: Playfair Display, Crimson Pro
- 모던: DM Sans, Source Sans 3
- 브루탈: Bricolage Grotesque

소스: Google Fonts
</use_interesting_fonts>
```

---

## 🎨 디자인 가드레일 (AI 패턴 탈피) 🆕

> **목적**: AI가 만든 UI가 "AI가 만든 티"가 나지 않도록
> **커맨드**: `/design` (자동 트리거 또는 수동 실행)

### 자동 트리거 키워드

다음 키워드 감지 시 `/design` 자동 실행:
- 랜딩페이지, landing page, 대시보드, dashboard
- UI, 화면, 페이지, 컴포넌트, component
- 디자인, design, 레이아웃, layout

### 🚫 AI 패턴 절대 금지

| 영역 | 금지 패턴 | 대안 |
|------|----------|------|
| **폰트** | Inter, Roboto 단독 | Space Grotesk, Neue Montreal, Ogg |
| **색상** | 보라/인디고 그라데이션 (`bg-indigo-500`) | 따뜻한 대지색, 차분한 블루/그린 |
| **레이아웃** | 3열 대칭 카드 그리드 | 비대칭(60/40), 매거진 스타일 |
| **모서리** | 균일한 12px radius | 4px(input), 8px(button), 16px(card) |
| **그림자** | 0.1 불투명도 everywhere | 의도적 그림자 또는 없음 |

### ✅ 필수 실행

```
✅ 디자인 요청 → /design 실행 → 개선된 프롬프트 생성
✅ 폰트 미지정 → Space Grotesk 또는 대안 제안
✅ 색상 미지정 → 따뜻한 대지색/차분한 블루그린 제안
✅ 레이아웃 미지정 → 비대칭(60/40) 또는 매거진 스타일 제안
```

### 워크플로우

```
"랜딩페이지 만들어줘"
         ↓
    /design 자동 실행
         ↓
    AI 패턴 위험 체크
         ↓
    개선된 프롬프트 생성
         ↓
    v0/Lovable/Cursor에 적용
```

### 추천 컬러 팔레트 (빠른 참조)

**따뜻한 대지색**: `#8B6914` + `#D4C4B0` + `#F5F0E8`
**차분한 블루/그린**: `#3D5A5B` + `#7C9A92` + `#F7F5F0`
**기업용 따뜻함**: `#2C3E50` + `#E74C3C` + `#FDFBF7`
**모던 다크**: `#0A1628` + `#16213E` + `#E94560`

### 레퍼런스 사이트

- **웹앱**: linear.app, figma.com, equals.com
- **랜딩**: gumroad.com, adaline.ai
- **브루탈리스트**: balenciaga.com, studiobrot.de

---

## Shovel 워크플로우

```
/start              # 프로젝트 온보딩 (1회)
    ↓
/plan [태스크]      # 계획 수립 (PRD 확인)
    ↓
사용자 확인         # 계획 승인
    ↓
/implement          # 구현 실행
    ↓
/handoff            # 의도 기록 (Step 완료 시)
    ↓
/clear              # Context Bias 제거 ⭐ Boris 방식
    ↓
/verify             # 새로운 눈으로 검증
    ↓
/gate               # Gate 검증 (lint→test→build)
    ↓
EVIDENCE.md 생성    # 통과 증거
    ↓
/review             # 코드 리뷰 + 학습 기록
    ↓
커밋
```

---

## ⚠️ CRITICAL RULES

### 🚫 NEVER (절대 금지)

```
NEVER "됐다", "완료", "성공" 선언 without Gate PASS
NEVER 랜덤/시간 의존 로직 (seed 미고정 상태)
NEVER 시크릿 하드코딩 (.env.example만 허용)
NEVER 스펙 밖 확장 (PRD 외 기능은 즉시 BACKLOG)
NEVER 테스트 없이 기능 완료 선언
NEVER 설정/규칙 분산 (SSOT 위반)
NEVER 증거 없는 "통과" 주장
NEVER 이해 못하는 코드 Accept (핵심 로직)
```

### ✅ ALWAYS (필수 수행)

```
ALWAYS Gate PASS로만 완료 정의 (lint→test→build→audit)
ALWAYS EVIDENCE.md 생성 (gate 통과 증거)
ALWAYS 결정론적 출력 (동일 입력 → 동일 JSON)
ALWAYS PRD를 SSOT로 고정
ALWAYS 입력 검증 (스키마, 타입, null 가드)
ALWAYS 실행 가능한 단계별 명령으로 지시
ALWAYS 환경변수는 .env.example로 문서화
ALWAYS 핵심 로직 이해 후 Accept
```

---

## 🎯 Gate 시스템

### 완료의 유일한 정의

```bash
pnpm gate  # 또는 bash scripts/gate.sh
# lint ✅ + test ✅ + build ✅ + audit ✅
# = EVIDENCE.md 자동 생성
# = 이것만이 "완료"
```

### Gate 단계

| 순서 | 단계 | 실패 시 |
|------|------|---------|
| 1 | `pnpm lint` | 0점, 즉시 중단 |
| 2 | `pnpm test` | 0점, 즉시 중단 |
| 3 | `pnpm build` | 0점, 즉시 중단 |
| 4 | `pnpm audit` | Critical만 중단 |

---

## 📦 SSOT 계층

```
docs/
├── PRD.md          # 📜 법 (스펙의 유일한 진실)
├── PLAN.md         # 📋 실행 계획
└── BACKLOG.md      # 📦 스펙 밖 = 여기로
```

### PRD 외 기능 요청 시

```
→ 즉시 BACKLOG.md로 이동
→ PRD 수정 없이 구현 금지
```

---

## 🔒 결정론 규칙

```
동일 입력 → 동일 출력 (항상)
```

### 금지 패턴

```typescript
// ❌ 금지
Math.random()      // seed 없이
Date.now()         // 고정 없이
uuid()             // seed 없이

// ✅ 허용
seededRandom(123)  // seed 고정
dayjs('2024-01-01')// 고정 날짜
```

### Flaky 테스트 = 버그

- "한 번 통과, 다음 실패" = 테스트 버그로 취급
- 재현 불가능 = 출시 불가

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────┐
│              Application                │
├─────────────────────────────────────────┤
│     Module A  │  Module B  │  Module C  │  ← 경계 명확
├─────────────────────────────────────────┤
│                 Core Layer              │
│  ┌───────────┬───────────┬───────────┐  │
│  │  Error    │  Logger   │  Config   │  │
│  │  Manager  │           │           │  │
│  └───────────┴───────────┴───────────┘  │
└─────────────────────────────────────────┘
```

### 의존성 규칙

```
프로젝트 core → 모든 모듈이 의존
모듈 간 직접 의존 금지 → Core 통해 소통
순환 의존 → 금지
```

---

## 🧪 테스트 요구사항

```
최소 요구사항:
- 8개 이상 테스트 케이스
- 성공/실패 케이스 모두 포함
- inject 테스트 선호 (서버 listen 금지)
- 커버리지 리포트 포함
```

### 테스트 없음 = 출시 불가

---

## 📝 납품 기준

납품 = 코드 ❌, 실행 가능한 시스템 ✅

**필수 납품물:**
1. 소스 코드
2. README.md (1커맨드 실행)
3. .env.example
4. EVIDENCE.md (Gate 증거)
5. 스모크 테스트 통과

---

## 🔄 검증 프로토콜 (Boris 방식)

> **출처**: Boris Cherny (Claude Code 창시자, Anthropic Staff Engineer)
> **핵심**: "피드백 루프가 있으면 품질이 2-3배 올라간다"

### Context Bias 제거

**문제**: 같은 세션에서 검증하면 자기가 짠 코드라 문제를 못 봄

**해결**:
```
개발 완료 → /handoff → /clear → /verify → 커밋
             (기록)    (초기화)   (검증)
```

### Step 완료 시 필수 프로세스

```markdown
1. /step-done 실행 (또는 /handoff)
2. Claude Code면 → 자동으로 /clear → /verify
3. 웹이면 → 새 대화에서 검증 요청
4. 검증 통과 후 다음 Step
```

### 절대 금지 🚫
```
❌ 검증 없이 "완료" 선언
❌ 같은 세션에서 자기 코드 "문제없음" 판단
❌ /handoff 없이 다음 기능 개발
```

---

## 커맨드 목록

| 커맨드 | 설명 |
|--------|------|
| `/start` | 프로젝트 온보딩 |
| `/sync` | 프로젝트 전체 동기화 및 정리 |
| `/plan` | 태스크 계획 수립 |
| `/implement` | 계획 실행 |
| `/gate` | **Gate 전체 실행** ⭐ |
| `/verify` | 개별 검증 + Context Bias 체크 |
| `/verify-server` | 🆕 서버 로직, 환경변수, API 검증 |
| `/handoff` | Step 완료 시 의도 기록 |
| `/step-done` | Step 완료 트리거 (자동 검증) |
| `/review` | 코드 리뷰 + 학습 기록 |
| `/error-log` | 에러 분석 및 기록 |
| `/learn-error` | 🆕 쌓인 에러 학습 → 규칙화 |
| `/deep-debug` | 🆕 3회 반복 에러 근본 원인 분석 |
| `/ssot-check` | SSOT 위반 검사 |

**📚 상세 사용법**: `docs/Command_Reference.md` 참고

---

## 🚨 ERROR_LOG

> `/error-log` 또는 `/review` 실행 시 여기에 자동 추가됩니다.

### 형식

```markdown
### [YYYY-MM-DD] 오류 제목
- **상황**: 발생 상황
- **원인**: 근본 원인 (5 Whys)
- **해결**: 해결 방법
- **예방**: 추가된 NEVER/ALWAYS 규칙
- **증거**: 관련 로그/파일
```

---

## 📚 참고 문서

- `docs/Verification_Protocol.md` - Boris 검증 방법
- `docs/Karpathy_Practical_Guide.md` - 개발 원칙 상세 가이드
- `docs/Vibe_Coding_Tips.md` - 커뮤니티 팁

---

## 이 파일은 `/start` 실행 후 프로젝트 정보로 대체됩니다.
