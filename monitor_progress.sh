#!/bin/bash
# 监控评估进度脚本

echo "=================================="
echo "📊 评估进度监控"
echo "=================================="
echo ""

# 查找最新的日志文件
LOG_FILE=$(ls -t continue_evaluation_*.log 2>/dev/null | head -1)

if [ -z "$LOG_FILE" ]; then
    echo "❌ 未找到日志文件"
    exit 1
fi

echo "📝 日志文件: $LOG_FILE"
echo ""

# 显示进程状态
PID=$(pgrep -f "run_cross_evaluation.py")
if [ -n "$PID" ]; then
    echo "✅ 评估进程运行中 (PID: $PID)"
else
    echo "⚠️  评估进程未运行"
fi

echo ""
echo "=================================="
echo "📈 当前进度"
echo "=================================="

# 统计已完成数量
EVAL_COUNT=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')
RAW_COUNT=$(find output/cross_evaluation_results -name "*.json" -path "*/raw/*" 2>/dev/null | wc -l | tr -d ' ')
TOTAL=640

PERCENTAGE=$(echo "scale=1; $EVAL_COUNT * 100 / $TOTAL" | bc)

echo "Evaluations: $EVAL_COUNT / $TOTAL ($PERCENTAGE%)"
echo "Raw文件: $RAW_COUNT"
echo "待完成: $((TOTAL - EVAL_COUNT))"

echo ""
echo "=================================="
echo "📋 最近日志 (最后20行)"
echo "=================================="
tail -20 "$LOG_FILE"

echo ""
echo "=================================="
echo "💡 监控命令"
echo "=================================="
echo "实时查看日志: tail -f $LOG_FILE"
echo "查看进程: ps aux | grep run_cross_evaluation"
echo "停止评估: kill $PID"
echo "=================================="
