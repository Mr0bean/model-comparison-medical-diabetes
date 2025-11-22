#!/bin/bash
# 监控最后3个评估

LOG_FILE=$(ls -t retry_final3_*.log 2>/dev/null | head -1)

echo "=================================="
echo "📊 最后3个评估监控 (冲刺100%!)"
echo "=================================="
echo ""

if [ -n "$LOG_FILE" ]; then
    echo "📝 日志文件: $LOG_FILE"
else
    echo "❌ 未找到日志文件"
fi
echo ""

# 检查进程
PID=$(pgrep -f "run_cross_evaluation.py")
if [ -n "$PID" ]; then
    echo "✅ 评估进程运行中 (PID: $PID)"
else
    echo "⚠️  评估进程未运行"
fi

echo ""

# 统计
EVAL_NOW=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')
MISSING=$((640 - EVAL_NOW))

echo "📈 进度:"
echo "   总评估: $EVAL_NOW / 640"
echo "   待完成: $MISSING"
echo "   完成率: $(python3 -c "print(f'{$EVAL_NOW/640*100:.1f}%')")"

if [ $EVAL_NOW -eq 640 ]; then
    echo ""
    echo "🎉🎉🎉 完美!已达到 100% (640/640)! 🎉🎉🎉"
fi

echo ""

# 患者10详情
count10=$(find output/cross_evaluation_results/患者10/evaluations -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
echo "📋 患者10: $count10/64"

if [ -n "$LOG_FILE" ]; then
    echo ""
    echo "=================================="
    echo "📋 最近日志"
    echo "=================================="
    tail -20 "$LOG_FILE"
fi

echo ""
echo "=================================="
