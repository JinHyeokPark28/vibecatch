# {프로젝트명} - Desktop App

> Shovel Development System v2 - Desktop Template (Electron)

---

## 📌 프로젝트 개요

| 항목 | 값 |
|------|-----|
| **프로젝트명** | {프로젝트명} |
| **타입** | Desktop Application |
| **환경** | PowerShell |
| **프레임워크** | Electron |
| **버전** | v0.0.1 |

---

## 🏛️ 한 줄 헌법

> **PRD가 법이다. Gate PASS만이 진실이다.**

---

## 🛠️ 필수 명령어

```powershell
# 개발 모드
pnpm dev

# Gate (완료 정의)
pnpm gate

# 개별 검증
pnpm lint
pnpm test
pnpm build

# 패키징
pnpm package
pnpm make
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
├── main/                   # Main Process
│   ├── index.ts            # Entry point
│   ├── ipc/                # IPC 핸들러
│   └── services/           # Main 서비스
│
├── preload/                # Preload Scripts
│   ├── index.ts
│   └── preload.d.ts        # 타입 정의
│
├── renderer/               # Renderer Process
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   └── App.tsx
│
├── core/                   # 공유 코어
│   ├── errors/
│   ├── logger/
│   └── config/
│
├── shared/                 # Main/Renderer 공유
│   ├── types/
│   ├── constants/
│   └── ipc-channels.ts     # IPC 채널 정의 (SSOT)
│
└── tests/
```

---

## ⚠️ 프로젝트 규칙

### 🚫 NEVER

```
NEVER Renderer에서 Node.js API 직접 사용
NEVER contextBridge 없이 preload expose
NEVER nodeIntegration: true
NEVER IPC 채널명 하드코딩 (shared/ipc-channels.ts 사용)
NEVER 시크릿 하드코딩
```

### ✅ ALWAYS

```
ALWAYS contextBridge로 API 노출
ALWAYS IPC 채널은 ipc-channels.ts에서 정의
ALWAYS Main/Renderer 타입 공유 (shared/types)
ALWAYS Gate PASS 후 커밋
ALWAYS 환경변수는 .env.example로 문서화
```

---

## 🔧 기술 스택

| 영역 | 기술 | 버전 |
|------|------|------|
| Framework | Electron | 33.x |
| Bundler | Electron Forge / Vite | latest |
| Language | TypeScript | 5.x |
| UI | React | 18.x |
| Testing | Vitest | 2.x |

---

## 📡 IPC 패턴

```typescript
// shared/ipc-channels.ts (SSOT)
export const IPC_CHANNELS = {
  GET_DATA: 'app:get-data',
  SAVE_FILE: 'app:save-file',
  // ...
} as const;

// main/ipc/handlers.ts
ipcMain.handle(IPC_CHANNELS.GET_DATA, async () => { ... });

// renderer/hooks/useIpc.ts
const data = await window.api.getData();
```

---

## 🔐 보안 체크리스트

- [ ] nodeIntegration: false
- [ ] contextIsolation: true
- [ ] sandbox: true
- [ ] webSecurity: true
- [ ] contextBridge 사용

---

## 🧪 테스트 규칙

```
최소 8개 테스트
├── Main Process 로직
├── IPC 핸들러
├── Renderer 컴포넌트
├── 에러 케이스
└── 통합 테스트
```

---

## 📦 빌드 타겟

| 플랫폼 | 포맷 | 명령어 |
|--------|------|--------|
| Windows | .exe (NSIS) | `pnpm make --platform=win32` |
| macOS | .dmg | `pnpm make --platform=darwin` |
| Linux | .deb, .rpm | `pnpm make --platform=linux` |

---

## 🚨 ERROR_LOG

<!-- 에러 발생 시 여기에 기록 -->

---

*Shovel Development System v2 - Desktop Template*
