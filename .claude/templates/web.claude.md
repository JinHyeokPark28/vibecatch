# {프로젝트명} - Web Project

> Shovel Development System v2 - Web Template

---

## 📌 프로젝트 개요

| 항목 | 값 |
|------|-----|
| **프로젝트명** | {프로젝트명} |
| **타입** | Web Application |
| **환경** | WSL |
| **프레임워크** | {Next.js / React / Vue} |
| **버전** | v0.0.1 |

---

## 🏛️ 한 줄 헌법

> **PRD가 법이다. Gate PASS만이 진실이다.**

---

## 🛠️ 필수 명령어

```bash
# 개발 서버
pnpm dev

# Gate (완료 정의)
pnpm gate

# 개별 검증
pnpm lint
pnpm test
pnpm build
pnpm typecheck
```

---

## 📦 SSOT 계층

```
docs/
├── PRD.md          # 📜 법
├── PLAN.md         # 📋 계획
└── BACKLOG.md      # 📦 스펙 밖
```

---

## 🏗️ 아키텍처

```
src/
├── app/                    # Next.js App Router
│   ├── (routes)/           # 라우트 그룹
│   ├── api/                # API Routes
│   └── layout.tsx
│
├── core/                   # 코어 레이어
│   ├── errors/             # ErrorManager
│   ├── logger/             # Logger
│   └── config/             # Config (SSOT)
│
├── modules/                # 기능 모듈
│   └── {module}/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── types.ts
│
├── shared/                 # 공유
│   ├── types/              # 타입 (SSOT)
│   ├── constants/          # 상수 (SSOT)
│   ├── schemas/            # Zod 스키마 (SSOT)
│   └── utils/
│
└── tests/
    ├── unit/
    └── integration/
```

---

## ⚠️ 프로젝트 규칙

### 🚫 NEVER

```
NEVER 서버 컴포넌트에서 클라이언트 상태 사용
NEVER useEffect에서 데이터 fetching (Server Component 사용)
NEVER any 타입
NEVER console.log (프로덕션)
NEVER 매직 넘버 하드코딩
```

### ✅ ALWAYS

```
ALWAYS 서버 컴포넌트 우선
ALWAYS Zod로 API 입력 검증
ALWAYS TypeScript strict mode
ALWAYS Gate PASS 후 커밋
```

---

## 🔧 기술 스택

| 영역 | 기술 | 버전 |
|------|------|------|
| Framework | Next.js | 15.x |
| Language | TypeScript | 5.x |
| Styling | Tailwind CSS | 3.x |
| Validation | Zod | 3.x |
| Testing | Vitest | 2.x |
| Linting | ESLint | 9.x |

---

## 🧪 테스트 규칙

```
최소 8개 테스트
├── 컴포넌트 렌더링
├── API 라우트
├── 유틸리티 함수
├── 에러 케이스
└── 통합 테스트
```

---

## 🚨 ERROR_LOG

<!-- 에러 발생 시 여기에 기록 -->

---

*Shovel Development System v2 - Web Template*
