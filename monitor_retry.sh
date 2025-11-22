#!/bin/bash
# 监控零分评估重试进度

LOG_FILE=$(ls -t retry_zero_scores_*.log 2>/dev/null | head -1)

echo "======================================"
echo "📊 零分评估重试监控"
echo "======================================"
echo ""

if [ -n "$LOG_FILE" ]; then
    echo "📝 日志文件: $LOG_FILE"
else
    echo "❌ 未找到日志文件"
fi
echo ""

# 检查进程
RETRY_PID=$(pgrep -f "retry_zero_scores.py")
EVAL_PID=$(pgrep -f "run_cross_evaluation.py")

if [ -n "$RETRY_PID" ]; then
    echo "✅ 重试进程运行中 (PID: $RETRY_PID)"
fi

if [ -n "$EVAL_PID" ]; then
    echo "✅ 评估进程运行中 (PID: $EVAL_PID)"
fi

if [ -z "$RETRY_PID" ] && [ -z "$EVAL_PID" ]; then
    echo "⚠️  进程未运行"
fi

echo ""

# 统计当前评估数
EVAL_NOW=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')
VALID_COUNT=0
ZERO_COUNT=0

# 统计零分评估
for eval_file in $(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null); do
    score=$(python3 -c "import json; print(json.load(open('$eval_file')).get('average_score', -1))" 2>/dev/null)
    if [ "$score" = "0.0" ]; then
        ZERO_COUNT=$((ZERO_COUNT + 1))
    elif [ "$score" != "-1" ]; then
        VALID_COUNT=$((VALID_COUNT + 1))
    fi
done

echo "📈 当前状态:"
echo "   总评估数: $EVAL_NOW / 640"
echo "   有效评估: $VALID_COUNT"
echo "   零分评估: $ZERO_COUNT"
echo "   完成率: $(python3 -c "print(f'{$VALID_COUNT/640*100:.1f}%')")"

if [ $ZERO_COUNT -eq 0 ] && [ $EVAL_NOW -eq 640 ]; then
    echo ""
    echo "🎉🎉🎉 完美! 所有640个评估都有有效分数! 🎉🎉🎉"
fi

echo ""

if [ -n "$LOG_FILE" ]; then
    echo "======================================"
    echo "📋 最近日志 (最后30行)"
    echo "======================================"
    tail -30 "$LOG_FILE" | grep -E "(✓|✗|⚠️|完成|失败|患者|步骤)" || tail -30 "$LOG_FILE"
fi

echo ""
echo "======================================"
