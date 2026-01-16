# VibeCatch

바이브 코더를 위한 HN/Reddit/GitHub 트렌드 수집기

AI 요약 + 선호도 학습으로 중요한 트렌드만 빠르게 파악하세요.

## Quick Start

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 설정
cp .env.example .env
# .env 파일에서 ANTHROPIC_API_KEY 설정

# 3. 서버 실행
uvicorn main:app --reload

# 4. 브라우저에서 확인
open http://localhost:8000
```

## 기능

| 기능 | 설명 |
|------|------|
| **콘텐츠 수집** | HN Top Stories, Reddit Hot Posts, GitHub Trending |
| **AI 요약** | Claude API로 한글 요약 + 태그 자동 추출 |
| **카드 리뷰** | Tinder 스타일 좋아요/건너뛰기 |
| **선호도 학습** | 태그 기반 우선순위 자동 조정 |
| **자동 수집** | 6시간마다 자동으로 새 콘텐츠 수집 |

## 스크린샷

```
┌─────────────────────────────────────┐
│  VibeCatch                          │
│  12개 리뷰 대기                      │
│  [새로 수집]                         │
│  리뷰 | 좋아요 | 통계                │
├─────────────────────────────────────┤
│  HN | 2026-01-16                    │
│  Show HN: AI 도구로 사이드 프로젝트...│
│                                     │
│         [건너뛰기] [좋아요]          │
└─────────────────────────────────────┘
```

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 카드 리뷰 UI |
| GET | `/liked` | 좋아요 목록 |
| GET | `/stats` | 태그별 선호도 통계 |
| POST | `/collect` | 수동 수집 트리거 |
| POST | `/review/{id}` | 좋아요/건너뛰기 |
| GET | `/scheduler/status` | 스케줄러 상태 |
| GET | `/health` | 헬스체크 |

## 환경변수

| 변수 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `ANTHROPIC_API_KEY` | O | - | Claude API 키 (요약용) |
| `DATABASE_PATH` | X | `vibecatch.db` | SQLite DB 경로 |
| `SCHEDULER_ENABLED` | X | `true` | 자동 수집 활성화 |
| `COLLECT_INTERVAL_HOURS` | X | `6` | 수집 간격 (시간) |
| `HN_FETCH_COUNT` | X | `30` | HN 수집 개수 |
| `REDDIT_FETCH_COUNT` | X | `20` | Reddit 수집 개수 |
| `GITHUB_FETCH_COUNT` | X | `20` | GitHub 수집 개수 |

## 프로젝트 구조

```
vibecatch/
├── main.py              # FastAPI 앱 + 스케줄러
├── database.py          # SQLite 데이터베이스
├── summarizer.py        # Claude API 요약
├── collectors/
│   ├── hackernews.py    # HN 수집
│   ├── reddit.py        # Reddit 수집
│   └── github.py        # GitHub 수집
├── templates/
│   ├── index.html       # 카드 리뷰 UI
│   ├── liked.html       # 좋아요 목록
│   └── stats.html       # 통계 페이지
├── static/
│   └── style.css
├── tests/
│   └── test_*.py
├── requirements.txt
└── .env.example
```

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | Python 3.11+, FastAPI |
| Database | SQLite |
| Template | Jinja2 |
| HTTP Client | httpx |
| Scheduler | APScheduler |
| AI | Claude API (Anthropic) |
| Testing | pytest |

## 개발

```bash
# 테스트 실행
pytest

# 린트
ruff check .

# 개발 서버
uvicorn main:app --reload
```

## Docker (선택)

```bash
# 빌드
docker build -t vibecatch .

# 실행
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=your_key vibecatch
```

## 라이선스

MIT
