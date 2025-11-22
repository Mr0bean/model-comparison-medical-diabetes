#!/bin/bash
# 持续监控评估进度

LOG_FILE="continue_evaluation_20251119_044811.log"

while true; do
    clear
    echo "=================================="
    echo "📊 评估进度实时监控"
    echo "=================================="
    echo ""

    # 检查进程状态
    PID=$(pgrep -f "run_cross_evaluation.py")
    if [ -n "$PID" ]; then
        echo "✅ 评估进程运行中 (PID: $PID)"
    else
        echo "⚠️  评估进程已停止"
        break
    fi

    echo ""

    # 统计完成数
    EVAL_COUNT=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')
    RAW_COUNT=$(find output/cross_evaluation_results -name "*.json" -path "*/raw/*" 2>/dev/null | wc -l | tr -d ' ')
    TOTAL=640

    PERCENTAGE=$(echo "scale=1; $EVAL_COUNT * 100 / $TOTAL" | bc)

    echo "📈 当前进度:"
    echo "   Evaluations: $EVAL_COUNT / $TOTAL ($PERCENTAGE%)"
    echo "   Raw文件: $RAW_COUNT"
    echo "   待完成: $((TOTAL - EVAL_COUNT))"

    echo ""
    echo "=================================="
    echo "📋 最近30行日志"
    echo "=================================="
    tail -30 "$LOG_FILE" | grep -E "患者|完成|失败|Error|Balance|✓|✗|%\|"

    echo ""
    echo "按Ctrl+C退出监控..."

    sleep 5
done

echo ""
echo "✨ 评估进程已完成！"
