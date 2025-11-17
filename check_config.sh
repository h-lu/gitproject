#!/bin/bash
# ============================================================
# 配置检查和诊断脚本
# ============================================================
# 用途：检查 hw1-template 和 hw1-tests 是否可以直接使用
# 运行：./check_config.sh
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查标记
ALL_OK=true

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🔍 Gitea 自动评分系统配置检查                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================
# 1. 检查必需的配置项
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 1. 检查关键配置项"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_var() {
    local var_name=$1
    local var_value=${!var_name}
    local is_required=$2
    
    if [ -n "$var_value" ] && [ "$var_value" != "your_admin_token_here" ] && [ "$var_value" != "your_deepseek_api_key_here" ]; then
        echo -e "${GREEN}✓${NC} $var_name = $var_value"
        return 0
    else
        if [ "$is_required" = "required" ]; then
            echo -e "${RED}✗${NC} $var_name 未配置或使用默认值"
            ALL_OK=false
            return 1
        else
            echo -e "${YELLOW}⚠${NC} $var_name 未配置（可选）"
            return 0
        fi
    fi
}

check_var "GITEA_URL" "required"
check_var "GITEA_ADMIN_TOKEN" "required"
check_var "ORGANIZATION" "required"
check_var "TEMPLATE_REPO" "required"
check_var "TESTS_REPO" "optional"
check_var "PREFIX" "required"
check_var "DEEPSEEK_API_KEY" "optional"

echo ""

# ============================================================
# 2. 检查 Gitea 连接
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 2. 检查 Gitea 服务器连接"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$GITEA_URL" ]; then
    if curl -s -o /dev/null -w "%{http_code}" "$GITEA_URL" | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓${NC} Gitea 服务器可访问: $GITEA_URL"
    else
        echo -e "${RED}✗${NC} Gitea 服务器无法访问: $GITEA_URL"
        ALL_OK=false
    fi
    
    # 检查 API
    if [ -n "$GITEA_ADMIN_TOKEN" ] && [ "$GITEA_ADMIN_TOKEN" != "your_admin_token_here" ]; then
        API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: token $GITEA_ADMIN_TOKEN" \
            "$GITEA_URL/api/v1/user")
        
        if [ "$API_RESPONSE" = "200" ]; then
            echo -e "${GREEN}✓${NC} API Token 有效"
        else
            echo -e "${RED}✗${NC} API Token 无效或权限不足 (HTTP $API_RESPONSE)"
            ALL_OK=false
        fi
    fi
fi

echo ""

# ============================================================
# 3. 检查 hw1-template 仓库
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 3. 检查 hw1-template 仓库"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "hw1-template" ]; then
    echo -e "${GREEN}✓${NC} hw1-template 目录存在"
    
    # 检查关键文件
    declare -a required_files=(
        "hw1-template/.gitea/workflows/grade.yml"
        "hw1-template/.gitea/workflows/llm_autograde.yml"
        "hw1-template/.autograde/grade.py"
        "hw1-template/.autograde/run_tests.py"
        "hw1-template/.autograde/create_minimal_metadata.py"
        "hw1-template/.autograde/post_comment.py"
        "hw1-template/problem.yaml"
        "hw1-template/README.md"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}  ✓${NC} $file"
        else
            echo -e "${RED}  ✗${NC} $file 缺失"
            ALL_OK=false
        fi
    done
    
    # 检查源代码
    if [ -f "hw1-template/src/models/logistic_regression.py" ]; then
        echo -e "${GREEN}  ✓${NC} 源代码文件存在"
    else
        echo -e "${YELLOW}  ⚠${NC} 源代码文件不完整（学生需要实现）"
    fi
    
    # 检查测试
    if [ -d "hw1-template/tests_public" ]; then
        TEST_COUNT=$(find hw1-template/tests_public -name "test_*.py" | wc -l)
        echo -e "${GREEN}  ✓${NC} 公开测试: $TEST_COUNT 个文件"
    else
        echo -e "${RED}  ✗${NC} tests_public 目录不存在"
        ALL_OK=false
    fi
    
    # 检查示例
    if [ -d "hw1-template/examples" ]; then
        echo -e "${GREEN}  ✓${NC} 多语言示例目录存在"
        [ -d "hw1-template/examples/java_example" ] && echo -e "${GREEN}    ✓${NC} Java 示例"
        [ -d "hw1-template/examples/r_example" ] && echo -e "${GREEN}    ✓${NC} R 示例"
    fi
    
else
    echo -e "${RED}✗${NC} hw1-template 目录不存在"
    ALL_OK=false
fi

echo ""

# ============================================================
# 4. 检查 hw1-tests 仓库
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔒 4. 检查 hw1-tests 隐藏测试仓库"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "hw1-tests" ]; then
    echo -e "${GREEN}✓${NC} hw1-tests 目录存在"
    
    if [ -d "hw1-tests/python/tests" ]; then
        HIDDEN_TEST_COUNT=$(find hw1-tests/python/tests -name "test_*.py" | wc -l)
        echo -e "${GREEN}  ✓${NC} 隐藏测试: $HIDDEN_TEST_COUNT 个文件"
    else
        echo -e "${YELLOW}  ⚠${NC} 隐藏测试目录为空"
    fi
    
    if [ -f "hw1-tests/python/data/breast_cancer_hidden.csv" ]; then
        echo -e "${GREEN}  ✓${NC} 隐藏数据集存在"
    else
        echo -e "${YELLOW}  ⚠${NC} 隐藏数据集不存在"
    fi
else
    echo -e "${YELLOW}⚠${NC} hw1-tests 目录不存在（可选，但建议创建）"
fi

echo ""

# ============================================================
# 6. 检查脚本和工具
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛠️  6. 检查管理脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

declare -a scripts=(
    "scripts/create_users.py:批量创建用户"
    "scripts/generate_repos.py:生成学生仓库"
    "scripts/add_collaborators.sh:添加协作者"
    "scripts/collect_grades.py:收集成绩"
    "scripts/quick_collect.sh:快速收集成绩"
    "scripts/create_course_template.py:创建课程模板"
    "scripts/update_workflows_all_branches.py:更新 Workflow"
)

for entry in "${scripts[@]}"; do
    IFS=: read -r script desc <<< "$entry"
    if [ -f "$script" ]; then
        if [ -x "$script" ] || [[ "$script" == *.py ]]; then
            echo -e "${GREEN}  ✓${NC} $script - $desc"
        else
            echo -e "${YELLOW}  ⚠${NC} $script 存在但不可执行"
        fi
    else
        echo -e "${RED}  ✗${NC} $script 缺失"
        ALL_OK=false
    fi
done

echo ""

# ============================================================
# 7. 检查学生列表
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "👥 7. 检查学生信息"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

STUDENTS_PATH="scripts/${STUDENTS_FILE:-students.txt}"
if [ -f "$STUDENTS_PATH" ]; then
    STUDENT_COUNT=$(wc -l < "$STUDENTS_PATH")
    echo -e "${GREEN}✓${NC} 学生列表: $STUDENTS_PATH ($STUDENT_COUNT 个学生)"
    
    # 显示前 3 个学生
    echo "  示例:"
    head -n 3 "$STUDENTS_PATH" | while read line; do
        echo "    $line"
    done
else
    echo -e "${YELLOW}⚠${NC} 学生列表文件不存在: $STUDENTS_PATH"
    echo -e "${YELLOW}  → 创建示例: scripts/students.txt${NC}"
fi

echo ""

# ============================================================
# 8. 检查 Python 依赖
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 8. 检查 Python 依赖"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

declare -a python_deps=("requests" "python-dotenv")

for dep in "${python_deps[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        VERSION=$(python3 -c "import $dep; print(getattr($dep, '__version__', 'unknown'))" 2>/dev/null)
        echo -e "${GREEN}  ✓${NC} $dep ($VERSION)"
    else
        echo -e "${RED}  ✗${NC} $dep 未安装"
        echo -e "${YELLOW}    → 安装: pip3 install $dep${NC}"
        ALL_OK=false
    fi
done

echo ""

# ============================================================
# 总结
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 检查总结"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✅ 所有检查通过！系统可以直接使用${NC}"
    echo ""
    echo "🚀 下一步:"
    echo "  1. 确保 hw1-template 已推送到 Gitea 并标记为模板"
    echo "  2. 确保 hw1-tests 已推送到 Gitea 并设置为私有"
    echo "  3. 运行: cd scripts && python3 generate_repos.py"
    echo "  4. 运行: cd scripts && ./add_collaborators.sh"
    echo ""
else
    echo -e "${RED}❌ 发现问题，请根据上面的提示修复${NC}"
    echo ""
    echo "📝 常见解决方案:"
    echo "  • 配置问题: export GITEA_URL / GITEA_ADMIN_TOKEN 等环境变量"
    echo "  • Token 问题: 在 Gitea 中重新生成 Token"
    echo "  • 依赖问题: pip3 install requests python-dotenv"
    echo "  • 文件缺失: 检查是否正确克隆了仓库"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 相关文档:"
echo "  • COURSE_TEMPLATE_GUIDE.md - 课程模板使用指南"
echo "  • SCRIPTS_INDEX.md - 脚本详细说明"
echo "  • ENV_SETUP_GUIDE.md - 环境变量配置说明"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

