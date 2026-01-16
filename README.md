# Shovel Development System v7

> **"좋은 제품 50% + 좋은 비즈니스 50%"**
>
> 20년차 PM 관점 + Boris 워크플로우 + Thariq 인터뷰
> **v7 신규**: 에러 자동 기록 + 학습 시스템, 서버 검증

## Quick Start (30초)

```bash
# 1. 이 폴더를 프로젝트에 복사
cp -r shovel-setup/.claude your-project/
cp -r shovel-setup/scripts your-project/
cp shovel-setup/CLAUDE.md your-project/

# 2. 스크립트 실행 권한 부여
chmod +x your-project/scripts/*.sh

# 3. 프로젝트로 이동
cd your-project

# 4. Claude Code에서 실행
/start
```

끝. Claude가 프로젝트를 분석하고 Shovel 시스템을 적용합니다.

---

## 핵심 철학

| 원칙 | 설명 |
|------|------|
| **Gate PASS = 완료** | "됐다" 금지. lint→test→build→audit 전부 통과만이 완료 |
| **Context Bias 제거** | /clear 후 검증해야 진짜 검증 (Boris 방식) |
| **증거주의** | EVIDENCE.md 없이 "통과" 주장 불가 |
| **결정론** | 동일 입력 → 동일 출력. Flaky = 버그 |
| **SSOT** | 설정/타입/상수 분산 금지. PRD가 법 |
| **보안 기본값** | 시크릿 하드코딩 = 즉시 실패 |

---

## 요구사항

| 항목 | 버전 | 확인 방법 |
|------|------|----------|
| Node.js | 20+ | `node -v` |
| pnpm | 8+ | `pnpm -v` |
| Claude Code | 최신 | Claude Code 앱에서 확인 |

### 설치 안 되어 있으면

```bash
# Node.js (nvm 권장)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install 20

# pnpm
npm install -g pnpm
```

---

## 파일 구조

```
shovel-setup-v7/
├── CLAUDE.md              # 메인 규칙 (PM 모드, 에러 프로토콜 포함)
├── ERROR_LOG.md           # 🆕 에러 자동 기록 파일
├── README.md              # 이 파일
├── scripts/
│   ├── gate.sh            # Gate 검증
│   ├── parallel-terminals.sh   # tmux 5개 (중첩 처리)
│   ├── parallel-terminals.ps1  # Windows Terminal 5개
│   ├── parallel-web.sh    # 웹 브라우저 탭
│   └── start-parallel.sh  # 병렬 환경 시작
├── docs/
│   ├── Verification_Protocol.md  # 검증 프로토콜
│   └── Vibe_Coding_Tips.md       # 바이브 코딩 팁
└── .claude/
    ├── settings.json
    ├── commands/
    │   ├── pm.md          # PM 모드
    │   ├── interview.md   # 스펙 인터뷰
    │   ├── start.md
    │   ├── gate.md
    │   ├── plan.md
    │   ├── implement.md
    │   ├── verify.md
    │   ├── verify-server.md   # 🆕 서버 검증
    │   ├── handoff.md
    │   ├── step-done.md
    │   ├── review.md
    │   ├── error-log.md
    │   ├── learn-error.md     # 🆕 에러 학습
    │   ├── deep-debug.md      # 🆕 반복 에러 분석
    │   ├── ssot-check.md
    │   └── commit.md
    ├── templates/
    │   ├── PRD.template.md
    │   ├── web.claude.md
    │   ├── desktop.claude.md
    │   ├── api.claude.md
    │   └── fullstack.claude.md
    ├── logs/
    ├── plans/
    └── evidence/
```

---

## 워크플로우

```
/start              # 프로젝트 온보딩 (1회)
    ↓
/plan [태스크]      # 계획 수립 (PRD 확인)
    ↓
(사용자 확인)       # 계획 승인
    ↓
/implement          # 구현 실행
    ↓
/handoff            # 의도 기록 (Step 완료 시)
    ↓
/clear              # Context Bias 제거 ⭐ Boris 방식
    ↓
/verify             # 새로운 눈으로 검증
    ↓
/gate               # Gate 검증 (lint→test→build→audit)
    ↓
EVIDENCE.md 생성    # 통과 증거
    ↓
/review             # 코드 리뷰 + 학습 기록
    ↓
커밋
```

---

## 커맨드 요약

| 커맨드 | 설명 | 언제 사용 |
|--------|------|----------|
| `/start` | 프로젝트 온보딩 | 처음 1회 |
| `/pm` | PM 모드 가이드 | 비즈니스 관점 필요 시 |
| `/interview` | 스펙 인터뷰 (Thariq) | 복잡한 기능 시작 전 |
| `/plan` | 태스크 계획 | 새 작업 시작 전 |
| `/implement` | 계획 실행 | 계획 승인 후 |
| `/check-complete` | 껍데기/미연결 검사 | "완료" 전 필수! |
| `/verify-server` | 🆕 서버 검증 | 서버 기능 완료 시 |
| `/handoff` | 의도 기록 | Step 완료 시 |
| `/step-done` | 검증 트리거 | Step 완료 시 (자동) |
| `/verify` | 검증 + Context Bias 체크 | /clear 후 |
| `/gate` | **Gate 전체 실행** | 구현 완료 후 (핵심!) |
| `/review` | 코드 리뷰 | 커밋 전 |
| `/error-log` | 에러 분석 및 기록 | 에러 발생 시 |
| `/learn-error` | 🆕 에러 학습 → 규칙화 | 에러 쌓였을 때 |
| `/deep-debug` | 🆕 반복 에러 근본 분석 | 3회 반복 시 자동 |
| `/ssot-check` | SSOT 위반 검사 | 설정/타입 변경 시 |
| `/commit` | 스마트 커밋 | 검증 통과 후 |

---

## Gate 시스템

### Gate = 유일한 완료 정의

```bash
pnpm gate
# 또는
bash scripts/gate.sh
```

### Gate 단계 (순서 고정)

| 순서 | 단계 | 실패 시 |
|------|------|---------|
| 1 | `pnpm lint` | 0점, 즉시 중단 |
| 2 | `pnpm test` | 0점, 즉시 중단 |
| 3 | `pnpm build` | 0점, 즉시 중단 |
| 4 | `pnpm audit` | Critical만 중단 |

### EVIDENCE.md 자동 생성

Gate PASS 시:
```markdown
# Gate Evidence Report
> Status: PASS
> Timestamp: 2026-01-09T14:30:00Z
> Commit: abc1234

| Step | Result |
|------|--------|
| Lint | ✅ PASS |
| Test | ✅ 12 passed |
| Build | ✅ |
| Audit | ✅ |
```

---

## 프로젝트 타입별

| 타입 | 템플릿 | 특징 | 환경 |
|------|--------|------|------|
| Web | `web.claude.md` | Next.js, React, Vue | WSL |
| Desktop | `desktop.claude.md` | Electron | PowerShell |
| API | `api.claude.md` | Express, Fastify | WSL |
| Fullstack | `fullstack.claude.md` | Next.js + API | WSL |

`/start` 실행 시 자동 감지하여 적용.

---

## SSOT 계층

```
docs/
├── PRD.md          # 📜 법 (여기 없는 기능 = 구현 금지)
├── PLAN.md         # 📋 실행 계획
└── BACKLOG.md      # 📦 스펙 밖 = 여기로
```

**PRD 외 기능 요청 시**: 즉시 BACKLOG로 이동. PRD 수정 없이 구현 금지.

---

## Compounding Engineering

> **"모든 실수가 규칙이 된다"**

### v7 에러 학습 시스템

```
에러 발생 → ERROR_LOG.md 자동 기록
    │
    ├── 1-2회: 기록만 (작업 계속)
    │
    └── 3회 반복: 🚨 /deep-debug 자동 트리거
                  │
                  └── 근본 원인 분석 → 구조적 수정
```

### /learn-error 사용

```bash
# 에러 쌓였을 때 (시간 날 때)
/learn-error
# → 패턴 분석
# → CLAUDE.md에 NEVER/ALWAYS 추가
# → ERROR_LOG.md 비움
```

### /deep-debug 사용

```bash
# 자동: 3회 반복 에러 시
# 수동: 복잡한 에러 분석 필요 시
/deep-debug "TypeError-undefined"
# → 작업 중단
# → 근본 원인 분석 (땜빵 금지)
# → 테스트 추가
# → 규칙화
```

---

## 기존 프로젝트 재개

이미 진행 중인 프로젝트에서:

```bash
# 1. .claude 폴더 복사
cp -r shovel-setup/.claude ./

# 2. /start 실행 → 자동으로 "기존 프로젝트" 감지
/start

# 3. 현재 상태 분석 + CLAUDE.md 생성/업데이트
```

---

## 문제 해결

### pnpm이 없다고 나올 때

```bash
npm install -g pnpm
```

### Gate 실패 시

```bash
# 1. 에러 분석
/error-log

# 2. 수정 후 재실행
pnpm gate
```

### 권한 에러

```bash
chmod -R 755 .claude
chmod +x scripts/*.sh
```

---

## 향후 자동화 (예정)

```json
{
  "pre-commit": "pnpm gate",
  "on-error": "auto-log",
  "ssot-check": "env-undocumented"
}
```

---

## 🚀 병렬 터미널 (Boris 방식)

### Linux/Mac (tmux)

```bash
cd your-project
chmod +x scripts/*.sh
./scripts/parallel-terminals.sh
```

5개 터미널: `1-Main`, `2-Test`, `3-Refactor`, `4-Docs`, `5-Review`

### Windows (PowerShell)

```powershell
.\scripts\parallel-terminals.ps1
```

### tmux 단축키

| 단축키 | 동작 |
|--------|------|
| `Ctrl+b n` | 다음 윈도우 |
| `Ctrl+b s` | 세션 목록 (프로젝트 전환) |
| `Ctrl+b d` | 세션 분리 |

### 멀티 프로젝트 동시 운용

```bash
# tmux 안에서도 다른 프로젝트 세션 생성 가능!
cd /mnt/d/[다른프로젝트]
./scripts/parallel-terminals.sh
# → 자동으로 새 세션 생성 후 전환
```

---

## 버전

- **v7.0.0** (2026-01-15): 에러 학습 시스템
  - 🆕 ERROR_LOG.md - 에러 자동 기록 파일
  - 🆕 `/learn-error` - 쌓인 에러 학습 → 규칙화
  - 🆕 `/deep-debug` - 3회 반복 에러 근본 원인 분석
  - 🆕 `/verify-server` - 서버 로직, 환경변수, API 검증
  - 🆕 에러 에스컬레이션 (3회 반복 → 자동 분석)
  - 🔄 기능 완료 플로우에 서버 검증 추가

- **v6.2.0** (2026-01-14): 프로젝트 동기화 시스템
  - `/sync` - 전체 프로젝트 동기화 및 정리
  - `docs/Command_Reference.md` - 명령어 상세 가이드
  - 우선순위 자동 재계산 (RICE)
  - TODO.md, IMPROVEMENTS.md 자동 생성
  - 중복/모순 자동 감지

- **v6.1.0** (2026-01-14): Karpathy 개발 원칙 통합
  - 개발 원칙 (CLAUDE.md 최상단)
  - `docs/Karpathy_Practical_Guide.md` - 수익화 중심 실전 가이드
  - 2시간 룰 (디버깅 늪 탈출)
  - Speed/Quality 모드 선택
  - 손코딩 vs AI 활용 판단 기준
  - 바이브 코딩 역할 분담 명확화

- **v6.0.0** (2026-01-14): Shovel System v6
  - PM 모드 (제품 50% + 비즈니스 50%)
  - `/pm` - PM 가이드
  - `/interview` - Thariq 스펙 인터뷰
  - Typography 가이드
  - tmux 중첩 처리 (멀티 프로젝트)
  - Windows PowerShell 지원
  
- **v2.1.0** (2026-01-13): 검증 프로토콜 (Boris 방식)
- **v2.0.0** (2026-01-09): Gate PASS 시스템

---

## 라이선스

MIT
