#!/bin/bash
echo "🔄 开始监控零分评估重试 (每30秒更新)"
echo "按 Ctrl+C 停止"
echo ""

INTERVAL=30
LAST_VALID=562

while true; do
    clear
    echo "======================================"
    echo "📊 零分评估重试实时监控"
    echo "======================================"
    echo "⏰ $(date '+%H:%M:%S')"
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
        echo "⚠️  进程已停止"
    fi

    echo ""

    # 统计评估数
    EVAL_NOW=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')
    VALID_COUNT=0
    ZERO_COUNT=0

    for eval_file in $(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null); do
        score=$(python3 -c "import json; print(json.load(open('$eval_file')).get('average_score', -1))" 2>/dev/null)
        if [ "$score" = "0.0" ]; then
            ZERO_COUNT=$((ZERO_COUNT + 1))
        elif [ "$score" != "-1" ]; then
            VALID_COUNT=$((VALID_COUNT + 1))
        fi
    done

    # 变化
    if [ $VALID_COUNT -gt $LAST_VALID ]; then
        DELTA=$((VALID_COUNT - LAST_VALID))
        echo "🎉 新增有效评估: +$DELTA!"
        LAST_VALID=$VALID_COUNT
    fi

    echo "📈 进度:"
    echo "   总文件数: $EVAL_NOW / 640"
    echo "   有效评估: $VALID_COUNT / 640 ($(python3 -c "print(f'{$VALID_COUNT/640*100:.1f}%')"))"
    echo "   零分评估: $ZERO_COUNT"
    echo "   待重试: $((640 - VALID_COUNT - ZERO_COUNT))"

    # 进度条 (基于有效评估)
    BARS=$((VALID_COUNT * 50 / 640))
    printf "\n["
    for i in $(seq 1 $BARS); do printf "█"; done
    for i in $(seq $((BARS + 1)) 50); do printf " "; done
    printf "]\n"

    echo ""

    # 完成检查
    if [ $VALID_COUNT -eq 640 ]; then
        echo "🎉🎉🎉 完美! 所有640个评估都有有效分数! 🎉🎉🎉"
        echo ""
        break
    fi

    # 进程停止检查
    if [ -z "$RETRY_PID" ] && [ -z "$EVAL_PID" ]; then
        echo "ℹ️  进程已停止"
        if [ $VALID_COUNT -lt 640 ]; then
            echo "   当前有效评估: $VALID_COUNT/640"
            echo "   零分评估: $ZERO_COUNT"
            echo "   还差 $((640 - VALID_COUNT)) 个有效评估"
        fi
        break
    fi

    # 显示最近的日志
    LOG_FILE=$(ls -t retry_zero_scores_*.log 2>/dev/null | head -1)
    if [ -n "$LOG_FILE" ]; then
        echo "📋 最近活动:"
        tail -5 "$LOG_FILE" | grep -E "(✓|完成|患者)" | tail -3 || echo "   评估进行中..."
    fi

    echo ""
    echo "⏰ 下次更新: ${INTERVAL}秒后..."
    sleep $INTERVAL
done

echo ""
echo "监控结束"
