# /design - AI스러운 UI 탈피 가이드

## 트리거

다음 키워드 감지 시 자동 실행:

**디자인 요청:**
- 랜딩페이지, landing page, 대시보드, dashboard
- UI, 화면, 페이지, 컴포넌트, component
- 디자인, design, 레이아웃, layout
- 프로덕트 페이지, 상세페이지, 소개페이지

**불만 표현:**
- 구려, 구리다, 뻔해, 뻔하다
- AI스럽, 똑같아, 별로

---

## 1단계: 요청 분석

```markdown
🎨 디자인 검사
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 요청: "[사용자 요청]"

🔍 분석:
- 타입: [랜딩페이지/대시보드/프로덕트페이지/컴포넌트/앱]
- 플랫폼: [v0/Lovable/Cursor/직접코딩]
- 스크롤 인터랙션 필요: [Y/N]
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

인터랙션:
□ 스크롤 효과 미지정 → 정적인 페이지 위험
□ 애니메이션 미지정 → 밋밋한 UX 위험
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
- Scroll: [스크롤 인터랙션]

Style keywords: [미학 키워드]

Avoid: Inter, Roboto, bg-indigo-500, uniform grids, soft shadows everywhere
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🎯 설득학적 랜딩페이지 섹션 구조

> **출처**: heroooo_landing - "홈페이지 첫 화면은 우리 회사의 첫 인상입니다"

**랜딩페이지 요청 시 자동으로 이 구조 제안:**

```markdown
🎯 설득학적 섹션 구성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **Hero** (첫인상)
   - 임팩트 있는 헤드라인 (감정 자극)
   - 서브텍스트: 핵심 가치 한 줄
   - CTA 2개: Primary + Secondary
   - 고급스러운 이미지/영상

2. **Pain Point** (공감)
   - 고객의 현재 고통 3가지
   - "이런 경험 있으시죠?" 공감대 형성
   - 문제의 심각성 강조

3. **Solution** (해결책)
   - "우리가 해결책입니다" 포지셔닝
   - Before → After 대비
   - 핵심 차별점 강조

4. **Social Proof** (신뢰)
   - 숫자로 증명: "10,000+ 고객", "98% 만족"
   - 실제 후기/테스티모니얼
   - 로고 월 (파트너/미디어)

5. **Features** (가치)
   - 핵심 기능/혜택 3가지
   - 아이콘 + 제목 + 설명
   - "왜 우리인가" 답변

6. **CTA** (행동 유도)
   - 명확한 행동 요청
   - 긴급성/희소성 추가
   - 리스크 제거 (무료 체험, 환불 보장)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 설득학적 프롬프트 예시

```
Build a landing page for [서비스] with persuasive section flow:

1. Hero: Emotional headline that challenges status quo
   - Example: "Not a tour. Seven days of Seoul citizenship."
   - Subtext: refined value proposition
   - Two CTAs: "Request Invitation" + "Explore"

2. Pain: 3 problems target customers face
3. Solution: How we solve it differently  
4. Proof: Numbers + testimonials + logos
5. Features: 3 core benefits with icons
6. Final CTA: Clear action + urgency + risk removal

Design: Premium, warm accents (#E74C3C), asymmetric layout
Font: Instrument Serif (headlines) + Graphik (body)
```

---

## 🍎 스토리텔링 스크롤 (Apple 스타일)

> **프로덕트 상세페이지, 기능 소개에 적합**
> 아이폰 제품 페이지처럼 스크롤하면 반응형으로 이미지/정보가 나타나는 효과

### 패턴 종류

| 패턴 | 설명 | 사용처 |
|------|------|--------|
| **Sticky + Content Swap** | 이미지 고정, 텍스트만 스크롤 | 스펙 비교, 기능 설명 |
| **Scroll-triggered Reveal** | 스크롤하면 요소 순차 등장 | 피처 소개 |
| **Parallax Depth** | 레이어별 다른 스크롤 속도 | 히어로, 배경 |
| **Progress Animation** | 스크롤 진행도에 따라 애니메이션 | 제품 회전, 컬러 변경 |
| **Section Snap** | 섹션 단위로 스냅 스크롤 | 한 화면 = 한 메시지 |

### 세부 설명

**1. Sticky + Content Swap**
```
┌─────────────────────────────────┐
│  [이미지 고정]    │  텍스트 1   │
│                   │  ↓ 스크롤   │
│  (움직이지 않음)  │  텍스트 2   │
│                   │  ↓ 스크롤   │
│                   │  텍스트 3   │
└─────────────────────────────────┘
```

**2. Scroll-triggered Reveal**
```
스크롤 진행 →
  ↓
[요소1 fade-in] → [요소2 slide-up] → [요소3 scale-in]
```

**3. Parallax Depth**
```
배경 레이어: 느리게 스크롤 (0.3x)
중간 레이어: 보통 스크롤 (0.7x)
전경 레이어: 빠르게 스크롤 (1x)
→ 깊이감 연출
```

**4. Progress Animation**
```
스크롤 0%   → 제품 정면
스크롤 50%  → 제품 45도 회전
스크롤 100% → 제품 측면 + 내부 구조
```

**5. Section Snap**
```
[섹션 1: 전체 화면] ─snap→ [섹션 2: 전체 화면] ─snap→ [섹션 3]
```

### 스크롤 인터랙션 프롬프트 예시

```
Build a product showcase page with Apple-style scroll interactions:

Scroll Behavior:
- Sticky hero image that stays fixed while text content scrolls beside it
- Scroll-triggered fade-in for each feature section
- Parallax effect on background elements (0.5x speed)
- Section snap scrolling for key feature highlights

Animations:
- Elements fade and slide up as they enter viewport
- Product image scales from 0.8 to 1.0 on scroll
- Color/theme transitions between sections
- Progress indicator shows current section

Technical:
- Use Framer Motion for React
- Or GSAP ScrollTrigger for vanilla JS
- Intersection Observer for reveal triggers
- CSS scroll-snap for section snapping

Sections:
1. Hero with parallax background
2. Key feature 1 (sticky image + scrolling text)
3. Key feature 2 (scroll-triggered reveal)
4. Key feature 3 (progress animation)
5. Specs comparison (snap scroll)
6. CTA with final animation
```

### 구현 키워드 (v0/Lovable/Cursor용)

```markdown
필수 키워드:
- "scroll-triggered animation"
- "sticky section with content swap"
- "parallax scrolling effect"
- "intersection observer animations"
- "scroll-linked animations"
- "section snap scroll"

라이브러리 지정:
- "use Framer Motion scroll animations"
- "use GSAP ScrollTrigger"
- "use AOS (Animate On Scroll)"
- "use Lenis smooth scroll"
```

### 스크롤 인터랙션 체크리스트

```markdown
□ Hero에 Parallax 적용?
□ 주요 섹션에 Sticky + Content Swap?
□ 요소 등장에 Scroll-triggered Reveal?
□ 제품 이미지에 Progress Animation?
□ 섹션 간 Snap Scroll?
□ Smooth Scroll 라이브러리 사용?
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
- Scroll: Parallax hero, scroll-triggered feature reveals

Style: Clean but warm, professional yet approachable
Avoid: Inter, purple gradients, 3-column symmetric grids
```

### Lovable

```
Design a product page with premium, cinematic feel and Apple-style scroll.

Use: layered depth, translucent surfaces, dramatic contrast
Font: Instrument Serif (headlines), Graphik (body)
Colors: deep navy #0A1628, coral accent #E94560
Layout: Asymmetric panels, varied card sizes

Scroll interactions:
- Sticky product image with scrolling specs
- Scroll-triggered animations for features
- Section snap between key highlights

Keywords: cinematic, layered, translucent, dramatic, scroll-driven
```

### Cursor

```
Create a product showcase with these constraints:

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

Scroll:
- Use Framer Motion for scroll animations
- Implement sticky sections for feature comparison
- Add parallax to hero background
- Scroll-triggered reveals for all sections
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

🎯 설득학적 섹션 구성: (랜딩페이지인 경우)
  1. Hero → 2. Pain → 3. Solution → 4. Proof → 5. Features → 6. CTA

🍎 스크롤 인터랙션 추천: (프로덕트 페이지인 경우)
  • Hero: Parallax background
  • Features: Sticky + Content Swap
  • Specs: Scroll-triggered Reveal
  • Sections: Snap Scroll

✅ 개선된 프롬프트:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[개선된 프롬프트 전문]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📎 위 프롬프트를 v0/Lovable/Cursor에 복사해서 사용하세요.

💡 추가 팁:
  • 레퍼런스: apple.com/iphone, linear.app, figma.com
  • 폰트: fonts.google.com, pangram.com
  • 컬러: coolors.co
  • 스크롤: Framer Motion, GSAP ScrollTrigger
```

---

## 레퍼런스 사이트

### 스크롤 인터랙션 참고
- **apple.com/iphone** - Sticky + Progress Animation
- **stripe.com** - Scroll-triggered Reveals
- **linear.app** - Smooth transitions
- **lusion.co** - Creative scroll effects

### 랜딩페이지 참고
- **gumroad.com** - 설득학적 구조
- **figma.com** - 깔끔한 SaaS
- **notion.so** - 기능 중심

### 디자인 영감
- **awwwards.com** - 트렌드
- **dribbble.com** - UI 패턴
- **mobbin.com** - 앱 UI
