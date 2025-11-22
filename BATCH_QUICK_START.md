# 分批执行快速上手

## 🎯 三种方式任选

### 方式1️⃣ : 预设批次（最简单）

```bash
python run_batch_evaluation.py
```

选择执行模式：
- `1` → 全部执行（患者2-10）
- `2` → 第一批（患者2,3,4）
- `3` → 第二批（患者5,6,7）
- `4` → 第三批（患者8,9,10）
- `5` → 试运行

---

### 方式2️⃣ : 灵活分批（最强大）

```bash
# 每2个患者一批
python run_flexible_batch.py --batch-size 2

# 只执行第1批
python run_flexible_batch.py --batch-size 3 --batch-index 1

# 指定患者和模型
python run_flexible_batch.py \
  --patients 患者1 患者2 \
  --models gpt-5.1 deepseek/deepseek-v3.1 \
  --batch-size 1
```

---

### 方式3️⃣ : 手动控制（最精确）

```bash
# 单独评估某些患者
python run_cross_evaluation.py --patients 患者1 患者2 患者3

# 指定模型
python run_cross_evaluation.py \
  --patients 患者1 \
  --models gpt-5.1 deepseek/deepseek-v3.1
```

---

## ⚡ 常用命令

### 快速测试（10分钟）

```bash
python run_flexible_batch.py \
  --patients 患者1 患者2 \
  --models gpt-5.1 deepseek/deepseek-v3.1 \
  --batch-size 1
```

### 后台执行

```bash
nohup python run_batch_evaluation.py > batch.log 2>&1 &

# 查看进度
tail -f batch.log
```

### 监控进度

```bash
# 查看已完成数量
find output/cross_evaluation_results -name "*.json" -path "*/evaluations/*" | wc -l

# 预期总数: 640 (10患者 × 8模型 × 8评估者)
```

### 查看某个患者的进度

```bash
ls output/cross_evaluation_results/患者1/evaluations/ | wc -l
# 每个患者应有64个评估文件
```

---

## 📊 批次规划参考

| 场景 | 命令 | 时间 |
|------|------|------|
| **快速测试** | `--batch-size 1 --patients 患者1` | 10分钟 |
| **短时执行** | `--batch-size 2` | 每批15-20分钟 |
| **标准分批** | `--batch-size 3` | 每批25-30分钟 |
| **完整执行** | `run_batch_evaluation.py` 选择1 | 1.5-2小时 |

---

## 🔍 故障排查

### 查看哪些患者已完成

```bash
for i in {1..10}; do
    count=$(find output/cross_evaluation_results/患者$i/evaluations/ -name "*.json" 2>/dev/null | wc -l)
    echo "患者$i: $count/64"
done
```

### 继续未完成的患者

```bash
# 假设患者1-3已完成，从患者4开始
python run_flexible_batch.py \
  --patients 患者4 患者5 患者6 患者7 患者8 患者9 患者10 \
  --batch-size 3
```

---

## 💡 建议流程

1. **先试运行**
   ```bash
   python run_flexible_batch.py --batch-size 3 --dry-run
   ```

2. **执行第一批**
   ```bash
   python run_flexible_batch.py --batch-size 3 --batch-index 1
   ```

3. **检查结果**
   ```bash
   ls output/cross_evaluation_results/患者*/evaluations/
   ```

4. **继续执行**
   ```bash
   python run_flexible_batch.py --batch-size 3
   ```

---

**提示**：所有脚本都支持断点续传，已完成的评估会自动跳过！✅
