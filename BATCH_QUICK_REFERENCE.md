# 分批执行快速参考

## 🚀 快速开始

```bash
# 交互式执行
python run_batch_evaluation.py
```

---

## 📋 预设批次

| 批次 | 患者 | API调用 | 耗时 |
|------|------|---------|------|
| 第一批 | 患者2,3,4 | 192次 | ~45分钟 |
| 第二批 | 患者5,6,7 | 192次 | ~45分钟 |
| 第三批 | 患者8,9,10 | 192次 | ~45分钟 |

---

## 🎯 执行模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| **1** | 全部执行（3批） | 夜间/周末一次性完成 |
| **2** | 仅第一批 | 分时段执行 |
| **3** | 仅第二批 | 分时段执行 |
| **4** | 仅第三批 | 分时段执行 |
| **5** | 试运行 | 测试/调试 |

---

## 📝 完整流程

```bash
# 1. 测试验证
python run_cross_evaluation.py --test-mode

# 2. 分批收集原始响应
python run_batch_evaluation.py  # 选择模式

# 3. 解析响应
python parse_raw_responses.py

# 4. 生成矩阵
python run_cross_evaluation.py --skip-evaluation
```

---

## ⏱️ 时间预估

- **单批**: 40-50分钟
- **全部3批**: 2-2.5小时
- **解析**: 5-10分钟
- **生成矩阵**: 1-2分钟

---

## 🔄 中断恢复

```bash
# 重新执行自动跳过已完成的
python run_batch_evaluation.py
# 选择中断的批次继续
```

---

## 📊 监控进度

```bash
# 查看已完成数量
find output/cross_evaluation_results -name "*.json" -path "*/raw/*" | wc -l

# 预期总数: 576
```

---

## 💾 数据备份

```bash
# 定期备份raw目录
tar -czf raw_backup_$(date +%Y%m%d).tar.gz \
    output/cross_evaluation_results/*/*/raw/
```
