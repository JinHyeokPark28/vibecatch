# {프로젝트명} - API Server

> Shovel Development System v2 - API Template

---

## 📌 프로젝트 개요

| 항목 | 값 |
|------|-----|
| **프로젝트명** | {프로젝트명} |
| **타입** | API Server |
| **환경** | WSL |
| **프레임워크** | {Express / Fastify / Hono} |
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
pnpm db:migrate
pnpm db:seed
```

---

## 🏗️ 아키텍처

```
src/
├── app.ts                  # App 초기화
├── server.ts               # Server 시작
│
├── core/                   # 코어 레이어
│   ├── errors/             # ErrorManager
│   ├── logger/             # Logger
│   ├── config/             # Config (SSOT)
│   ├── middleware/         # 공통 미들웨어
│   └── db/                 # Database
│
├── modules/                # 기능 모듈
│   └── {module}/
│       ├── routes.ts       # 라우트 정의
│       ├── controller.ts   # 컨트롤러
│       ├── service.ts      # 비즈니스 로직
│       ├── repository.ts   # DB 접근
│       ├── schemas.ts      # Zod 스키마
│       └── types.ts
│
├── shared/                 # 공유
│   ├── types/
│   ├── constants/
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
NEVER 컨트롤러에 비즈니스 로직
NEVER 서비스에서 직접 DB 쿼리 (Repository 사용)
NEVER 입력 검증 없이 처리
NEVER SQL Injection 가능한 raw query
NEVER 시크릿 하드코딩
NEVER 테스트에서 실제 서버 listen
```

### ✅ ALWAYS

```
ALWAYS 라우트 → 컨트롤러 → 서비스 → 리포지토리 계층
ALWAYS Zod로 요청 body 검증
ALWAYS inject 테스트 (supertest 사용)
ALWAYS 에러는 ErrorManager 통해 처리
ALWAYS Gate PASS 후 커밋
```

---

## 🔧 기술 스택

| 영역 | 기술 | 버전 |
|------|------|------|
| Runtime | Node.js | 20.x |
| Framework | Fastify / Express | latest |
| Language | TypeScript | 5.x |
| Database | PostgreSQL | 16.x |
| ORM | Prisma / Drizzle | latest |
| Validation | Zod | 3.x |
| Testing | Vitest + Supertest | latest |

---

## 🧪 테스트 패턴

```typescript
// ✅ 좋은 테스트 (inject)
import { app } from '../src/app';

describe('POST /users', () => {
  it('should create user', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/users',
      payload: { name: 'Test' }
    });
    expect(response.statusCode).toBe(201);
  });
});

// ❌ 나쁜 테스트 (listen)
beforeAll(async () => {
  await app.listen(3000); // 포트 충돌 위험
});
```

---

## 🔐 보안 체크리스트

- [ ] 모든 엔드포인트 인증/인가 확인
- [ ] 입력 데이터 Zod 검증
- [ ] SQL Injection 방지
- [ ] Rate Limiting
- [ ] CORS 설정
- [ ] Helmet (보안 헤더)

---

## 🚨 ERROR_LOG

<!-- 에러 발생 시 여기에 기록 -->

---

*Shovel Development System v2 - API Template*
