#!/bin/bash
# 持续监控评估进度 - 每30秒自动更新

echo "🔄 启动持续监控模式 (每30秒更新一次)"
echo "按 Ctrl+C 停止监控"
echo ""

INTERVAL=30
LAST_COUNT=0

while true; do
    clear
    echo "=================================="
    echo "📊 交叉评估持续监控"
    echo "=================================="
    echo "⏰ 更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    # 检查进程状态
    PID=$(pgrep -f "run_cross_evaluation.py")
    if [ -n "$PID" ]; then
        echo "✅ 评估进程运行中 (PID: $PID)"
    else
        echo "⚠️  评估进程已停止"
    fi

    echo ""

    # 统计评估数量
    EVAL_NOW=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')
    EVAL_MISSING=$((640 - EVAL_NOW))

    # 计算本次变化
    if [ $LAST_COUNT -gt 0 ]; then
        DELTA=$((EVAL_NOW - LAST_COUNT))
        if [ $DELTA -gt 0 ]; then
            echo "📈 进度变化: +$DELTA 个新评估"
        else
            echo "⏸️  暂无新进展"
        fi
    fi
    LAST_COUNT=$EVAL_NOW

    echo ""
    echo "📊 总体进度:"
    echo "   完成: $EVAL_NOW / 640"
    echo "   待完成: $EVAL_MISSING"
    COMPLETION=$(python3 -c "print(f'{$EVAL_NOW/640*100:.1f}')")
    echo "   完成率: ${COMPLETION}%"

    # 进度条
    BARS=$((EVAL_NOW * 50 / 640))
    printf "   ["
    for i in $(seq 1 $BARS); do printf "█"; done
    for i in $(seq $((BARS + 1)) 50); do printf " "; done
    printf "] ${COMPLETION}%%\n"

    echo ""
    echo "📋 按患者统计:"
    for patient in output/cross_evaluation_results/患者*; do
        if [ -d "$patient" ]; then
            name=$(basename "$patient")
            count=$(find "$patient/evaluations" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
            if [ $count -eq 64 ]; then
                echo "   ✓ $name: $count/64"
            else
                echo "   ⏳ $name: $count/64 (还缺 $((64-count)) 个)"
            fi
        fi
    done

    echo ""

    # 如果进程停止且完成率达到100%,退出监控
    if [ -z "$PID" ] && [ $EVAL_NOW -eq 640 ]; then
        echo "🎉 完成! 已达到 640/640 (100%)"
        echo ""
        break
    fi

    # 如果进程停止,显示提示
    if [ -z "$PID" ]; then
        echo "ℹ️  进程已停止,但未达到100%"
        echo "   当前: $EVAL_NOW/640 (${COMPLETION}%)"
        echo ""
        echo "是否需要继续重试?"
        break
    fi

    echo "⏰ 下次更新: ${INTERVAL}秒后..."
    sleep $INTERVAL
done

echo "监控结束"
