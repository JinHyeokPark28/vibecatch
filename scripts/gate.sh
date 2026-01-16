#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Shovel Gate Script v2
# "Gate PASS만이 진실이다"
# ═══════════════════════════════════════════════════════════════

set -e

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

EVIDENCE_FILE="EVIDENCE.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "no-git")
GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-branch")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Results
LINT_RESULT=""
LINT_DETAILS=""
TEST_RESULT=""
TEST_DETAILS=""
BUILD_RESULT=""
BUILD_DETAILS=""
AUDIT_RESULT=""
AUDIT_DETAILS=""
GATE_STATUS="PASS"

# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════

print_header() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║             SHOVEL GATE SYSTEM v2                             ║"
    echo "║           'Gate PASS만이 진실이다'                             ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Timestamp: $TIMESTAMP"
    echo "Commit: $GIT_HASH"
    echo "Branch: $GIT_BRANCH"
    echo ""
}

log_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

log_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_fail() {
    echo -e "${RED}❌ $1${NC}"
    GATE_STATUS="FAIL"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# ═══════════════════════════════════════════════════════════════
# Gate Steps
# ═══════════════════════════════════════════════════════════════

run_lint() {
    log_step "Step 1/4: LINT"
    
    local output_file="/tmp/lint_output_$$.txt"
    
    if pnpm lint 2>&1 | tee "$output_file"; then
        local warnings=$(grep -c "warning" "$output_file" 2>/dev/null || echo "0")
        LINT_RESULT="✅ PASS"
        LINT_DETAILS="0 errors, $warnings warnings"
        log_pass "Lint passed ($LINT_DETAILS)"
        return 0
    else
        LINT_RESULT="❌ FAIL"
        LINT_DETAILS="See output above"
        log_fail "Lint failed - Gate 중단"
        return 1
    fi
}

run_test() {
    log_step "Step 2/4: TEST"
    
    local output_file="/tmp/test_output_$$.txt"
    
    # Check if tests exist
    local test_count=$(find . -name "*.test.*" -o -name "*.spec.*" 2>/dev/null | grep -v node_modules | wc -l)
    
    if [ "$test_count" -eq 0 ]; then
        LINT_RESULT="❌ FAIL"
        LINT_DETAILS="No tests found (minimum 8 required)"
        log_fail "No tests found - Shovel requires tests"
        echo ""
        echo -e "${YELLOW}테스트가 없습니다. Shovel 시스템은 최소 8개 테스트를 요구합니다.${NC}"
        return 1
    fi
    
    if pnpm test 2>&1 | tee "$output_file"; then
        local passed=$(grep -oE "[0-9]+ passed" "$output_file" | head -1 || echo "passed")
        LINT_RESULT="✅ PASS"
        LINT_DETAILS="$passed"
        log_pass "Tests passed ($LINT_DETAILS)"
        return 0
    else
        LINT_RESULT="❌ FAIL"
        LINT_DETAILS="Test failures - see output"
        log_fail "Tests failed - Gate 중단"
        return 1
    fi
}

run_build() {
    log_step "Step 3/4: BUILD"
    
    local output_file="/tmp/build_output_$$.txt"
    local start_time=$(date +%s)
    
    if pnpm build 2>&1 | tee "$output_file"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        BUILD_RESULT="✅ PASS"
        BUILD_DETAILS="${duration}s"
        log_pass "Build succeeded (${duration}s)"
        return 0
    else
        BUILD_RESULT="❌ FAIL"
        BUILD_DETAILS="Build errors - see output"
        log_fail "Build failed - Gate 중단"
        return 1
    fi
}

run_audit() {
    log_step "Step 4/4: AUDIT"
    
    local output_file="/tmp/audit_output_$$.txt"
    
    pnpm audit 2>&1 | tee "$output_file" || true
    
    local critical_count=$(grep -ci "critical" "$output_file" 2>/dev/null || echo "0")
    local high_count=$(grep -ci "high" "$output_file" 2>/dev/null || echo "0")
    
    if [ "$critical_count" -gt 0 ]; then
        AUDIT_RESULT="❌ FAIL"
        AUDIT_DETAILS="$critical_count critical vulnerabilities"
        log_fail "Critical vulnerabilities found - Gate 중단"
        return 1
    elif [ "$high_count" -gt 0 ]; then
        AUDIT_RESULT="⚠️ WARN"
        AUDIT_DETAILS="$high_count high (non-blocking)"
        log_warn "High vulnerabilities found (non-blocking)"
        return 0
    else
        AUDIT_RESULT="✅ PASS"
        AUDIT_DETAILS="No vulnerabilities"
        log_pass "Audit passed"
        return 0
    fi
}

# ═══════════════════════════════════════════════════════════════
# Evidence Generation
# ═══════════════════════════════════════════════════════════════

generate_evidence() {
    log_step "Generating EVIDENCE.md"
    
    cat > "$EVIDENCE_FILE" << EOF
# Gate Evidence Report

> **Generated**: $TIMESTAMP
> **Status**: $GATE_STATUS

---

## 📋 Summary

| Step | Result | Details |
|------|--------|---------|
| Lint | $LINT_RESULT | $LINT_DETAILS |
| Test | $TEST_RESULT | $TEST_DETAILS |
| Build | $BUILD_RESULT | $BUILD_DETAILS |
| Audit | $AUDIT_RESULT | $AUDIT_DETAILS |

---

## 🔍 Environment

| Property | Value |
|----------|-------|
| Timestamp | $TIMESTAMP |
| Git Commit | \`$GIT_HASH\` |
| Git Branch | \`$GIT_BRANCH\` |
| Node Version | $(node -v 2>/dev/null || echo "N/A") |
| pnpm Version | $(pnpm -v 2>/dev/null || echo "N/A") |
| OS | $(uname -s) |

---

## 📊 Detailed Logs

### Lint
\`\`\`
$(cat /tmp/lint_output_$$.txt 2>/dev/null | tail -20 || echo "No output")
\`\`\`

### Test
\`\`\`
$(cat /tmp/test_output_$$.txt 2>/dev/null | tail -30 || echo "No output")
\`\`\`

### Build
\`\`\`
$(cat /tmp/build_output_$$.txt 2>/dev/null | tail -20 || echo "No output")
\`\`\`

### Audit
\`\`\`
$(cat /tmp/audit_output_$$.txt 2>/dev/null | tail -20 || echo "No output")
\`\`\`

---

## ✅ Gate Result

EOF

    if [ "$GATE_STATUS" = "PASS" ]; then
        cat >> "$EVIDENCE_FILE" << 'EOF'
```
 ██████╗  █████╗ ████████╗███████╗    ██████╗  █████╗ ███████╗███████╗
██╔════╝ ██╔══██╗╚══██╔══╝██╔════╝    ██╔══██╗██╔══██╗██╔════╝██╔════╝
██║  ███╗███████║   ██║   █████╗      ██████╔╝███████║███████╗███████╗
██║   ██║██╔══██║   ██║   ██╔══╝      ██╔═══╝ ██╔══██║╚════██║╚════██║
╚██████╔╝██║  ██║   ██║   ███████╗    ██║     ██║  ██║███████║███████║
 ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝    ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝
```

**이 프로젝트는 Gate를 통과했습니다.**
**배포/납품 준비 완료.**
EOF
    else
        cat >> "$EVIDENCE_FILE" << 'EOF'
```
 ██████╗  █████╗ ████████╗███████╗    ███████╗ █████╗ ██╗██╗     
██╔════╝ ██╔══██╗╚══██╔══╝██╔════╝    ██╔════╝██╔══██╗██║██║     
██║  ███╗███████║   ██║   █████╗      █████╗  ███████║██║██║     
██║   ██║██╔══██║   ██║   ██╔══╝      ██╔══╝  ██╔══██║██║██║     
╚██████╔╝██║  ██║   ██║   ███████╗    ██║     ██║  ██║██║███████╗
 ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝
```

**Gate 실패.**
**위의 오류를 수정한 후 다시 실행하세요.**
EOF
    fi

    cat >> "$EVIDENCE_FILE" << EOF

---

*Generated by Shovel Gate System v2*
*"Gate PASS만이 진실이다"*
EOF

    echo -e "\n${GREEN}📄 Evidence saved to: $EVIDENCE_FILE${NC}"
}

# ═══════════════════════════════════════════════════════════════
# Cleanup
# ═══════════════════════════════════════════════════════════════

cleanup() {
    rm -f /tmp/lint_output_$$.txt
    rm -f /tmp/test_output_$$.txt
    rm -f /tmp/build_output_$$.txt
    rm -f /tmp/audit_output_$$.txt
}

trap cleanup EXIT

# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

main() {
    print_header
    
    # Run all gates
    if ! run_lint; then
        generate_evidence
        print_fail_message
        exit 1
    fi
    
    if ! run_test; then
        generate_evidence
        print_fail_message
        exit 1
    fi
    
    if ! run_build; then
        generate_evidence
        print_fail_message
        exit 1
    fi
    
    if ! run_audit; then
        generate_evidence
        print_fail_message
        exit 1
    fi
    
    # All passed
    generate_evidence
    print_pass_message
    exit 0
}

print_pass_message() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}"
    echo "  ✅ GATE PASS"
    echo ""
    echo "  모든 검증을 통과했습니다."
    echo "  EVIDENCE.md가 생성되었습니다."
    echo ""
    echo "  다음 단계:"
    echo "    /review    - 코드 리뷰"
    echo "    git commit - 커밋"
    echo -e "${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
}

print_fail_message() {
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}"
    echo "  ❌ GATE FAIL"
    echo ""
    echo "  검증에 실패했습니다."
    echo "  위의 오류를 수정한 후 다시 실행하세요."
    echo ""
    echo "  에러 분석: /error-log"
    echo "  재실행:    pnpm gate"
    echo -e "${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
}

# Run
main "$@"
