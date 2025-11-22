#!/bin/bash
# 监控最后10个评估的重试进度

LOG_FILE=$(ls -t retry_last10_*.log 2>/dev/null | head -1)

if [ -z "$LOG_FILE" ]; then
    echo "❌ 未找到日志文件"
    exit 1
fi

echo "=================================="
echo "📊 最后10个评估重试监控"
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
EVAL_BEFORE=630
EVAL_NOW=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')
EVAL_NEW=$((EVAL_NOW - EVAL_BEFORE))
EVAL_MISSING=$((640 - EVAL_NOW))

echo "📈 当前进度:"
echo "   总评估: $EVAL_NOW / 640"
echo "   本轮新增: $EVAL_NEW"
echo "   待完成: $EVAL_MISSING"
echo "   完成率: $(python3 -c "print(f'{$EVAL_NOW/640*100:.1f}%')")"
echo ""

# 患者9和患者10的详细进度
echo "📋 目标患者进度:"
echo -n "   患者9: "
count9=$(find output/cross_evaluation_results/患者9/evaluations -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
echo "$count9/64 (还缺 $((64-count9)) 个)"

echo -n "   患者10: "
count10=$(find output/cross_evaluation_results/患者10/evaluations -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
echo "$count10/64 (还缺 $((64-count10)) 个)"

echo ""
echo "=================================="
echo "📋 最近日志 (最后20行)"
echo "=================================="
tail -20 "$LOG_FILE"

echo ""
echo "=================================="
