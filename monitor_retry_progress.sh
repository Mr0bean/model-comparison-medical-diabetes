#!/bin/bash
# 监控重试评估进度

LOG_FILE=$(ls -t retry_evaluation_fixed_*.log 2>/dev/null | head -1)

if [ -z "$LOG_FILE" ]; then
    echo "❌ 未找到日志文件"
    exit 1
fi

echo "=================================="
echo "📊 重试评估进度监控"
echo "=================================="
echo ""
echo "📝 日志文件: $LOG_FILE"
echo ""

# 检查进程状态
PID=$(pgrep -f "run_cross_evaluation.py")
if [ -n "$PID" ]; then
    echo "✅ 评估进程运行中 (PID: $PID)"
else
    echo "⚠️  评估进程未运行"
fi

echo ""

# 统计完成数
EVAL_BEFORE=517
RAW_BEFORE=534

EVAL_NOW=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')
RAW_NOW=$(find output/cross_evaluation_results -name "*.json" -path "*/raw/*" 2>/dev/null | wc -l | tr -d ' ')

EVAL_NEW=$((EVAL_NOW - EVAL_BEFORE))
RAW_NEW=$((RAW_NOW - RAW_BEFORE))

EVAL_MISSING=$((640 - EVAL_NOW))
RAW_MISSING=$((640 - RAW_NOW))

echo "📈 当前进度:"
echo "   Evaluations: $EVAL_NOW / 640 (新增: $EVAL_NEW, 待完成: $EVAL_MISSING)"
echo "   Raw文件: $RAW_NOW / 640 (新增: $RAW_NEW, 待完成: $RAW_MISSING)"
echo ""

# 统计日志中的成功和失败
SUCCESS_COUNT=$(grep -c "✓ 完成:" "$LOG_FILE" 2>/dev/null || echo "0")
FAIL_COUNT=$(grep -c "✗ 失败:" "$LOG_FILE" 2>/dev/null || echo "0")
ERROR_COUNT=$(grep -c "Error code:" "$LOG_FILE" 2>/dev/null || echo "0")

echo "📋 执行统计:"
echo "   成功: $SUCCESS_COUNT"
echo "   失败: $FAIL_COUNT"
echo "   错误: $ERROR_COUNT"

echo ""
echo "=================================="
echo "📋 最近日志"
echo "=================================="
tail -30 "$LOG_FILE" | grep -v "^📋"

echo ""
echo "=================================="
