#!/bin/bash
#
# 🌐 Claude Web 병렬 탭 실행 (Boris #2)
#
# 사용법: ./scripts/parallel-web.sh [탭수]
#
# 기본 5개 탭이 claude.ai에서 열립니다.
# 각 탭을 다른 작업에 활용하세요.

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 탭 수 (기본 5개, 최대 10개)
TAB_COUNT="${1:-5}"
if [ "$TAB_COUNT" -gt 10 ]; then
    TAB_COUNT=10
fi

CLAUDE_URL="https://claude.ai/new"

echo -e "${BLUE}🌐 Claude Web 병렬 탭 실행${NC}"
echo -e "${YELLOW}열릴 탭 수: ${TAB_COUNT}${NC}"
echo ""

# OS 감지 및 브라우저 열기 함수
open_url() {
    local url="$1"
    
    case "$(uname -s)" in
        Darwin)
            # macOS
            open "$url"
            ;;
        Linux)
            # Linux (WSL 포함)
            if grep -qi microsoft /proc/version 2>/dev/null; then
                # WSL
                cmd.exe /c start "$url" 2>/dev/null || powershell.exe -c "Start-Process '$url'" 2>/dev/null
            elif command -v xdg-open &> /dev/null; then
                xdg-open "$url"
            elif command -v gnome-open &> /dev/null; then
                gnome-open "$url"
            else
                echo -e "${RED}❌ 브라우저를 열 수 없습니다.${NC}"
                exit 1
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            # Windows (Git Bash, WSL 등)
            start "$url"
            ;;
        *)
            echo -e "${RED}❌ 지원하지 않는 OS입니다.${NC}"
            exit 1
            ;;
    esac
}

# 탭 역할 정의
TAB_ROLES=(
    "🎯 Main - 핵심 기능 구현"
    "🧪 Test - 테스트 작성"
    "🔧 Refactor - 리팩토링"
    "📝 Docs - 문서화"
    "👀 Review - 코드 리뷰"
    "🔍 Research - 라이브러리 조사"
    "🐛 Debug - 에러 디버깅"
    "🏗️ Architecture - 아키텍처 논의"
    "⚡ Performance - 성능 최적화"
    "🎨 UI/UX - 디자인 작업"
)

echo -e "${GREEN}탭 열기 시작...${NC}"
echo ""

for ((i=1; i<=TAB_COUNT; i++)); do
    role="${TAB_ROLES[$((i-1))]}"
    echo -e "  Tab $i: ${role}"
    open_url "$CLAUDE_URL"
    
    # 브라우저가 탭을 열 시간 확보 (너무 빠르면 충돌)
    sleep 0.5
done

echo ""
echo -e "${GREEN}✅ ${TAB_COUNT}개 탭 열기 완료!${NC}"
echo ""
echo -e "${BLUE}권장 사용법:${NC}"
echo "  Tab 1-3: 코드 작업 (프론트/백엔드/DB)"
echo "  Tab 4-5: 테스트/문서화"
echo "  Tab 6+:  리서치/디버깅"
echo ""
echo -e "${YELLOW}💡 팁: 각 탭에 역할 메모를 남겨두세요${NC}"
echo '  예: "이 탭은 테스트 전용입니다" 라고 첫 메시지로'
