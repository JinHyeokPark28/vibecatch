#!/bin/bash
#
# 🔥 Claude Code 풀 병렬 환경 실행 (Boris #1 + #2)
#
# 사용법: ./scripts/start-parallel.sh [프로젝트경로] [웹탭수]
#
# 실행되는 것:
#   - tmux 5개 터미널 세션
#   - 웹 브라우저 탭 (기본 5개)
#
# 한 번에 10개 Claude 인스턴스로 작업 가능!

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 인자 처리
PROJECT_DIR="${1:-$(pwd)}"
WEB_TABS="${2:-5}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

clear

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🔥 CLAUDE CODE PARALLEL MODE 🔥                            ║"
echo "║                                                               ║"
echo "║   Boris Cherny 방식 - 최대 생산성 환경                        ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

echo -e "${BLUE}📁 프로젝트:${NC} $PROJECT_DIR"
echo -e "${BLUE}🖥️  터미널:${NC}  5개 (tmux)"
echo -e "${BLUE}🌐 웹 탭:${NC}   ${WEB_TABS}개"
echo ""

# 확인 프롬프트
echo -e "${YELLOW}이 설정으로 시작할까요? (Y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Nn]$ ]]; then
    echo "취소되었습니다."
    exit 0
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}STEP 1: 웹 브라우저 탭 열기${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# 웹 탭 열기
if [ -f "$SCRIPT_DIR/parallel-web.sh" ]; then
    bash "$SCRIPT_DIR/parallel-web.sh" "$WEB_TABS"
else
    echo -e "${YELLOW}⚠️  parallel-web.sh 없음, 수동으로 claude.ai 열어주세요${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}STEP 2: tmux 터미널 세션 시작${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

sleep 2  # 웹 탭이 열릴 시간

# 터미널 세션 시작
if [ -f "$SCRIPT_DIR/parallel-terminals.sh" ]; then
    bash "$SCRIPT_DIR/parallel-terminals.sh" "$PROJECT_DIR"
else
    echo -e "${RED}❌ parallel-terminals.sh 없음${NC}"
    exit 1
fi
