#!/bin/bash
# 后台监控脚本 - 定期记录进度到文件

LOG_FILE="progress_monitor_$(date +%Y%m%d_%H%M%S).log"
INTERVAL=30

echo "启动后台监控,日志文件: $LOG_FILE" | tee -a "$LOG_FILE"
echo "监控间隔: ${INTERVAL}秒" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

while true; do
    {
        echo "=================================="
        echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
        echo "=================================="

        # 检查进程
        PID=$(pgrep -f "run_cross_evaluation.py")
        if [ -n "$PID" ]; then
            echo "✅ 进程运行中 (PID: $PID)"
        else
            echo "⚠️  进程已停止"
        fi

        # 统计进度
        EVAL_NOW=$(find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" 2>/dev/null | wc -l | tr -d ' ')
        echo "📊 完成: $EVAL_NOW/640 ($(python3 -c "print(f'{$EVAL_NOW/640*100:.1f}%')"))"

        # 患者10进度
        count10=$(find output/cross_evaluation_results/患者10/evaluations -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
        echo "📋 患者10: $count10/64"

        echo ""

        # 如果进程停止或完成,退出
        if [ -z "$PID" ] || [ $EVAL_NOW -eq 640 ]; then
            if [ $EVAL_NOW -eq 640 ]; then
                echo "🎉 评估完成! 640/640"
            else
                echo "ℹ️  进程已停止,当前: $EVAL_NOW/640"
            fi
            break
        fi

    } >> "$LOG_FILE"

    sleep $INTERVAL
done

echo "监控结束" | tee -a "$LOG_FILE"
