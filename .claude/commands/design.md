# /design - AI스러운 UI 탈피 가이드

## 트리거
다음 키워드 감지 시 자동 실행:
- 랜딩페이지, landing page, 대시보드, dashboard
- UI, 화면, 페이지, 컴포넌트, component
- 디자인, design, 레이아웃, layout

---

## 1단계: 요청 분석

```markdown
🎨 디자인 검사
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 요청: "[사용자 요청]"

🔍 분석:
- 타입: [랜딩페이지/대시보드/컴포넌트/앱]
- 플랫폼: [v0/Lovable/Cursor/직접코딩]
```

---

## 2단계: AI 패턴 위험 체크

### 체크리스트

```markdown
⚠️ AI 패턴 위험 요소:

타이포그래피:
□ 폰트 미지정 → Inter 기본값 위험
□ 웨이트 미지정 → 400/600만 사용 위험

색상:
□ 색상 미지정 → 보라 그라데이션 위험
□ "모던", "깔끔" 키워드 → bg-indigo-500 위험

레이아웃:
□ 레이아웃 미지정 → 3열 카드 그리드 위험
□ "피처 섹션" → 아이콘+제목+설명 반복 위험

컴포넌트:
□ 스타일 미지정 → 균일한 둥근 모서리 위험
□ 그림자 미지정 → 0.1 불투명도 드롭섀도우 위험
```

---

## 3단계: 개선된 프롬프트 생성

### 기본 템플릿

```markdown
✅ 개선된 프롬프트:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Build [타입] for [서비스/사용자].

Design constraints:
- Font: [추천 폰트] (NO Inter, Roboto)
- Colors: [추천 팔레트] (NO purple gradients)
- Layout: [추천 레이아웃] (NO 3-column grid)
- Corners: 4px inputs, 8px buttons, 16px cards (NO uniform radius)

Style keywords: [미학 키워드]

Avoid: Inter, Roboto, bg-indigo-500, uniform grids, soft shadows everywhere
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 폰트 추천

### 산세리프 (Inter/Roboto 대신)

| 폰트 | 특징 | 용도 |
|------|------|------|
| **Space Grotesk** | 미래적, 기하학적 | 테크, SaaS |
| **Neue Montreal** | 도시적 세련미 | 스타트업 |
| **Graphik** | 다양한 너비 | 복잡한 UI |
| **Apercu** | 독특한 캐릭터 | 크리에이티브 |

### 세리프 (헤드라인용)

| 폰트 | 특징 | 용도 |
|------|------|------|
| **Instrument Serif** | 클래식+모던 | UI/브랜딩 |
| **GT Super** | 개성 있는 현대 | 프리미엄 |
| **Ogg** | 고대비 에디토리얼 | 럭셔리 |

### 추천 조합

| 용도 | 헤드라인 | 본문 |
|------|----------|------|
| 스타트업/SaaS | Space Grotesk | Lato |
| 프리미엄 | Ogg | Graphik |
| 에디토리얼 | GT Super | Tiempos Text |
| 개발자 도구 | JetBrains Mono | Inter Variable |

---

## 컬러 팔레트 추천

### 보라 그라데이션 대신

**1. 따뜻한 대지색**
```
Primary:    #8B6914 (모카)
Secondary:  #D4C4B0 (샌드)
Background: #F5F0E8 (크림)
Accent:     #B8860B (골드)
```

**2. 차분한 블루/그린**
```
Primary:    #3D5A5B (딥 틸)
Secondary:  #7C9A92 (세이지)
Background: #F7F5F0 (오프화이트)
Accent:     #D4A574 (따뜻한 탄)
```

**3. 기업용 따뜻함**
```
Primary:    #2C3E50 (다크 슬레이트)
Secondary:  #E74C3C (코랄 레드)
Background: #FDFBF7 (따뜻한 화이트)
Accent:     #F39C12 (골드)
```

**4. 모던 다크**
```
Primary:    #0A1628 (딥 네이비)
Secondary:  #16213E (미드나잇)
Background: #0A1628
Accent:     #E94560 (코랄)
```

---

## 레이아웃 추천

### 3열 카드 그리드 대신

**1. 비대칭 2열 (60/40)**
```css
grid-template-columns: 1.5fr 1fr;
```

**2. 매거진 스타일**
- 피처드 아이템 크게
- 나머지 작게 배치
- 불균일한 그리드

**3. 단일 열 내러티브**
- 풀 너비 콘텐츠
- 대형 타이포그래피
- 여유로운 공간

**4. 오버래핑**
- 이미지가 텍스트에 겹침
- z-index로 깊이감

---

## 플랫폼별 프롬프트 예시

### v0

```
Build a SaaS landing page for a productivity tool.

Design constraints:
- Font: Space Grotesk (headlines), Lato (body)
- Colors: #2C3E50 primary, #E74C3C accent, #FDFBF7 background
- Layout: Asymmetric hero (60/40 split), staggered feature cards
- Corners: 4px inputs, 8px buttons, 16px cards

Style: Clean but warm, professional yet approachable
Avoid: Inter, purple gradients, 3-column symmetric grids
```

### Lovable

```
Design a dashboard with premium, cinematic feel.

Use: layered depth, translucent surfaces, dramatic contrast
Font: Instrument Serif (headlines), Graphik (body)
Colors: deep navy #0A1628, coral accent #E94560
Layout: Asymmetric panels, varied card sizes

Keywords: cinematic, layered, translucent, dramatic
```

### Cursor

```
Create a component library with these constraints:

Typography:
- Headlines: Space Grotesk, 700 weight
- Body: Lato, 400 weight
- Size contrast: 3x between h1 and body

Colors:
- Primary: #3D5A5B
- Accent: #D4A574
- Background: #F7F5F0

Layout:
- Asymmetric grids preferred
- Varied corner radius (4/8/16px)
- Intentional whitespace imbalance
```

---

## 출력 형식

```markdown
🎨 디자인 검사 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 요청: "[원본 요청]"

⚠️ 감지된 AI 패턴 위험:
  • [위험 요소 1]
  • [위험 요소 2]
  • [위험 요소 3]

✅ 개선된 프롬프트:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[개선된 프롬프트 전문]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📎 위 프롬프트를 v0/Lovable/Cursor에 복사해서 사용하세요.

💡 추가 팁:
  • 레퍼런스 사이트: linear.app, figma.com, gumroad.com
  • 폰트 확인: fonts.google.com, pangram.com
  • 컬러 확인: coolors.co
```
