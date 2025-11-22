#!/bin/bash
echo "🔄 开始监控最后3个评估 (每30秒更新)"
echo "按 Ctrl+C 停止"
echo ""

INTERVAL=30
LAST_COUNT=637

while true; do
    clear
    echo "=================================="
    echo "📊 冲刺100% - 最后3个评估监控"
    echo "=================================="
    echo "⏰ $(date '+%H:%M:%S')"
    echo ""
    
    # 检查进程
    PID=$(pgrep -f "run_cross_evaluation.py")
    if [ -n "$PID" ]; then
        echo "✅ 进程运行中 (PID: $PID)"
    else
        echo "⚠️  进程已停止"
    fi
    
    echo ""
    
    # 统计
    EVAL_NOW=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')
    MISSING=$((640 - EVAL_NOW))
    
    # 变化
    if [ $EVAL_NOW -gt $LAST_COUNT ]; then
        DELTA=$((EVAL_NOW - LAST_COUNT))
        echo "🎉 新增: +$DELTA 个评估!"
        LAST_COUNT=$EVAL_NOW
    fi
    
    echo "📈 总进度: $EVAL_NOW / 640 ($(python3 -c "print(f'{$EVAL_NOW/640*100:.1f}%')"))"
    echo "📋 患者10: $(find output/cross_evaluation_results/患者10/evaluations -name "*.json" 2>/dev/null | wc -l | tr -d ' ')/64"
    echo "🎯 剩余: $MISSING 个"
    
    # 进度条
    BARS=$((EVAL_NOW * 50 / 640))
    printf "\n["
    for i in $(seq 1 $BARS); do printf "█"; done
    for i in $(seq $((BARS + 1)) 50); do printf " "; done
    printf "]\n"
    
    echo ""
    
    # 完成检查
    if [ $EVAL_NOW -eq 640 ]; then
        echo "🎉🎉🎉 完美!已达到 100%! 🎉🎉🎉"
        echo ""
        break
    fi
    
    # 进程停止检查
    if [ -z "$PID" ]; then
        echo "ℹ️  进程已停止"
        if [ $EVAL_NOW -lt 640 ]; then
            echo "   当前: $EVAL_NOW/640,还差 $MISSING 个"
        fi
        break
    fi
    
    echo "⏰ 下次更新: ${INTERVAL}秒后..."
    sleep $INTERVAL
done

echo ""
echo "监控结束"
