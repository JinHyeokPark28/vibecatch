#!/bin/bash
#
# 🚀 Claude Code 병렬 터미널 실행 (Boris #1)
# 
# 사용법: ./scripts/parallel-terminals.sh [프로젝트경로]
#
# 5개 터미널이 역할별로 자동 생성됩니다:
#   1. Main     - 핵심 기능 구현
#   2. Test     - 테스트 작성/실행
#   3. Refactor - 리팩토링/정리
#   4. Docs     - 문서화
#   5. Review   - 코드 리뷰/버그 탐지

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 경로 (인자 또는 현재 디렉토리)
PROJECT_DIR="${1:-$(pwd)}"

# 세션 이름: 프로젝트 폴더명 사용
SESSION_NAME=$(basename "$PROJECT_DIR")

echo -e "${BLUE}🚀 Claude Code 병렬 터미널 시작${NC}"
echo -e "${YELLOW}프로젝트: ${PROJECT_DIR}${NC}"
echo -e "${YELLOW}세션명: ${SESSION_NAME}${NC}"
echo ""

# tmux 설치 확인
if ! command -v tmux &> /dev/null; then
    echo -e "${RED}❌ tmux가 설치되어 있지 않습니다.${NC}"
    echo ""
    echo "설치 방법:"
    echo "  macOS:  brew install tmux"
    echo "  Ubuntu: sudo apt install tmux"
    echo "  Arch:   sudo pacman -S tmux"
    exit 1
fi

# 이미 tmux 세션 안에 있는지 확인
if [ -n "$TMUX" ]; then
    CURRENT_SESSION=$(tmux display-message -p '#S')
    
    # 같은 프로젝트면 안내
    if [ "$CURRENT_SESSION" = "$SESSION_NAME" ]; then
        echo -e "${YELLOW}⚠️  이미 ${SESSION_NAME} 세션에 있습니다.${NC}"
        exit 0
    fi
    
    # 다른 프로젝트 세션이 있으면 전환
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${GREEN}✅ ${SESSION_NAME} 세션으로 전환합니다.${NC}"
        tmux switch-client -t "$SESSION_NAME"
        exit 0
    fi
    
    # 없으면 새로 만들고 전환
    echo -e "${GREEN}✅ ${SESSION_NAME} 세션 생성 중...${NC}"
    
    tmux new-session -d -s "$SESSION_NAME" -n "1-Main" -c "$PROJECT_DIR"
    tmux send-keys -t "$SESSION_NAME:1-Main" "echo '🎯 [Main] 핵심 기능 구현'" Enter
    
    tmux new-window -t "$SESSION_NAME" -n "2-Test" -c "$PROJECT_DIR"
    tmux new-window -t "$SESSION_NAME" -n "3-Refactor" -c "$PROJECT_DIR"
    tmux new-window -t "$SESSION_NAME" -n "4-Docs" -c "$PROJECT_DIR"
    tmux new-window -t "$SESSION_NAME" -n "5-Review" -c "$PROJECT_DIR"
    
    tmux select-window -t "$SESSION_NAME:1-Main"
    
    echo -e "${GREEN}✅ 전환합니다.${NC}"
    tmux switch-client -t "$SESSION_NAME"
    exit 0
fi

# 기존 세션 확인
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  기존 세션 발견. 연결합니다...${NC}"
    tmux attach-session -t "$SESSION_NAME"
    exit 0
fi

# 새 세션 생성
echo -e "${GREEN}✅ 5개 터미널 생성 중...${NC}"

# 세션 생성 + 첫 번째 윈도우 (Main)
tmux new-session -d -s "$SESSION_NAME" -n "1-Main" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION_NAME:1-Main" "echo '🎯 [Main] 핵심 기능 구현 터미널'" Enter
tmux send-keys -t "$SESSION_NAME:1-Main" "echo '명령어: claude \"[기능] 구현해줘\"'" Enter
tmux send-keys -t "$SESSION_NAME:1-Main" "clear" Enter

# 두 번째 윈도우 (Test)
tmux new-window -t "$SESSION_NAME" -n "2-Test" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION_NAME:2-Test" "echo '🧪 [Test] 테스트 작성/실행 터미널'" Enter
tmux send-keys -t "$SESSION_NAME:2-Test" "echo '명령어: claude \"[기능] 테스트 작성해줘\"'" Enter
tmux send-keys -t "$SESSION_NAME:2-Test" "clear" Enter

# 세 번째 윈도우 (Refactor)
tmux new-window -t "$SESSION_NAME" -n "3-Refactor" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION_NAME:3-Refactor" "echo '🔧 [Refactor] 리팩토링/정리 터미널'" Enter
tmux send-keys -t "$SESSION_NAME:3-Refactor" "echo '명령어: claude \"[파일/폴더] 리팩토링해줘\"'" Enter
tmux send-keys -t "$SESSION_NAME:3-Refactor" "clear" Enter

# 네 번째 윈도우 (Docs)
tmux new-window -t "$SESSION_NAME" -n "4-Docs" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION_NAME:4-Docs" "echo '📝 [Docs] 문서화 터미널'" Enter
tmux send-keys -t "$SESSION_NAME:4-Docs" "echo '명령어: claude \"[모듈] 문서 작성해줘\"'" Enter
tmux send-keys -t "$SESSION_NAME:4-Docs" "clear" Enter

# 다섯 번째 윈도우 (Review)
tmux new-window -t "$SESSION_NAME" -n "5-Review" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION_NAME:5-Review" "echo '👀 [Review] 코드 리뷰/버그 탐지 터미널'" Enter
tmux send-keys -t "$SESSION_NAME:5-Review" "echo '명령어: claude \"[파일/폴더] 리뷰해줘\"'" Enter
tmux send-keys -t "$SESSION_NAME:5-Review" "clear" Enter

# 첫 번째 윈도우로 이동
tmux select-window -t "$SESSION_NAME:1-Main"

echo ""
echo -e "${GREEN}✅ 5개 터미널 생성 완료!${NC}"
echo ""
echo -e "${BLUE}tmux 단축키:${NC}"
echo "  Ctrl+b n     다음 윈도우"
echo "  Ctrl+b p     이전 윈도우"
echo "  Ctrl+b 1-5   윈도우 직접 이동"
echo "  Ctrl+b d     세션 분리 (백그라운드)"
echo "  Ctrl+b s     세션 목록 (전환)"
echo "  Ctrl+b &     윈도우 닫기"
echo ""
echo -e "${YELLOW}세션 재연결: tmux attach -t $SESSION_NAME${NC}"
echo ""

# 세션 연결
tmux attach-session -t "$SESSION_NAME"
