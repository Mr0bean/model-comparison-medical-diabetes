#!/bin/bash
# 监控最终重试进度

LOG_FILE=$(ls -t retry_final_*.log 2>/dev/null | head -1)

if [ -z "$LOG_FILE" ]; then
    echo "❌ 未找到日志文件"
    exit 1
fi

echo "=================================="
echo "📊 最终重试进度监控"
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
EVAL_BEFORE=622

EVAL_NOW=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')

EVAL_NEW=$((EVAL_NOW - EVAL_BEFORE))
EVAL_MISSING=$((640 - EVAL_NOW))

echo "📈 当前进度:"
echo "   Evaluations: $EVAL_NOW / 640 (新增: $EVAL_NEW, 待完成: $EVAL_MISSING)"
echo "   完成率: $(python3 -c "print(f'{$EVAL_NOW/640*100:.1f}%')")"
echo ""

# 按患者统计
echo "📋 按患者统计:"
for patient in output/cross_evaluation_results/患者*; do
    name=$(basename "$patient")
    count=$(find "$patient/evaluations" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    if [ $count -eq 64 ]; then
        echo "   ✓ $name: $count/64"
    else
        echo "   ✗ $name: $count/64"
    fi
done

echo ""
echo "=================================="
echo "📋 最近日志 (最后30行)"
echo "=================================="
tail -30 "$LOG_FILE" | grep -E "(完成|失败|Error|评估|患者|%)"

echo ""
echo "=================================="
