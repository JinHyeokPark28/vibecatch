# {프로젝트명} - Fullstack

> Shovel Development System v2 - Fullstack Template (Next.js)

---

## 📌 프로젝트 개요

| 항목 | 값 |
|------|-----|
| **프로젝트명** | {프로젝트명} |
| **타입** | Fullstack Application |
| **환경** | WSL |
| **프레임워크** | Next.js (App Router) |
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

# 데이터베이스
pnpm db:push
pnpm db:studio
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
│   ├── (routes)/           # 페이지 라우트
│   │   ├── page.tsx
│   │   └── layout.tsx
│   ├── api/                # API Routes
│   │   └── {resource}/
│   │       └── route.ts
│   └── layout.tsx
│
├── core/                   # 코어 레이어
│   ├── errors/             # ErrorManager
│   ├── logger/             # Logger
│   ├── config/             # Config (SSOT)
│   └── db/                 # Database
│       ├── client.ts       # Prisma/Drizzle Client
│       └── schema.ts       # DB Schema (SSOT)
│
├── modules/                # 기능 모듈
│   └── {module}/
│       ├── components/     # UI 컴포넌트
│       ├── hooks/          # 클라이언트 훅
│       ├── actions/        # Server Actions
│       ├── services/       # 비즈니스 로직
│       ├── repository/     # DB 접근
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
    ├── integration/
    └── e2e/
```

---

## ⚠️ 프로젝트 규칙

### 🚫 NEVER

```
NEVER 클라이언트에서 직접 DB 접근
NEVER Server Action에서 인증 검증 누락
NEVER SQL Injection 가능한 raw query
NEVER 민감 정보 클라이언트 노출
NEVER any 타입
```

### ✅ ALWAYS

```
ALWAYS Server Component 우선
ALWAYS Server Action 사용 (API Route 대신)
ALWAYS Zod로 입력 검증
ALWAYS Repository 패턴으로 DB 접근
ALWAYS Gate PASS 후 커밋
```

---

## 🔧 기술 스택

| 영역 | 기술 | 버전 |
|------|------|------|
| Framework | Next.js | 15.x |
| Language | TypeScript | 5.x |
| Database | PostgreSQL | 16.x |
| ORM | Prisma / Drizzle | latest |
| Validation | Zod | 3.x |
| Auth | NextAuth.js | 5.x |
| Testing | Vitest | 2.x |

---

## 📊 데이터 흐름

```
[Client]
    ↓ Server Action / API Route
[Modules/Actions]
    ↓ 비즈니스 로직
[Modules/Services]
    ↓ DB 접근
[Modules/Repository]
    ↓ ORM
[Core/DB/Client]
    ↓
[Database]
```

---

## 🔐 보안 체크리스트

- [ ] 모든 Server Action에 인증 검증
- [ ] 입력 데이터 Zod 검증
- [ ] SQL Injection 방지 (ORM 사용)
- [ ] XSS 방지 (React 기본)
- [ ] CSRF 방지 (Server Action 기본)
- [ ] 환경변수 .env.example 문서화

---

## 🧪 테스트 규칙

```
최소 8개 테스트
├── Server Actions
├── Services (비즈니스 로직)
├── Repository (DB 접근)
├── API Routes
├── 컴포넌트
└── E2E (Critical Path)
```

---

## 📡 Server Action 패턴

```typescript
// modules/user/actions/createUser.ts
'use server';

import { z } from 'zod';
import { userService } from '../services/userService';
import { CreateUserSchema } from '@/shared/schemas/user';

export async function createUser(data: z.infer<typeof CreateUserSchema>) {
  // 1. 입력 검증
  const validated = CreateUserSchema.parse(data);
  
  // 2. 인증 확인
  const session = await getSession();
  if (!session) throw new Error('Unauthorized');
  
  // 3. 비즈니스 로직
  return userService.create(validated);
}
```

---

## 🚨 ERROR_LOG

<!-- 에러 발생 시 여기에 기록 -->

---

*Shovel Development System v2 - Fullstack Template*
