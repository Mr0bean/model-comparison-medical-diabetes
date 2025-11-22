# 配置概览

## 快速参考

### 环境配置 (.env)

```bash
# API配置
JIEKOU_API_KEY=your_api_key_here          # 必填: JieKou AI API密钥
JIEKOU_BASE_URL=https://api.jiekou.ai/openai  # API基础URL

# 默认模型设置
DEFAULT_MODEL=gpt-5.1                     # 默认使用的模型
DEFAULT_TEMPERATURE=None                  # 温度参数 (0.0-2.0，None表示不设置)
DEFAULT_MAX_TOKENS=2048                   # 最大token数
DEFAULT_STREAM=True                       # 是否使用流式输出

# 日志配置
LOG_LEVEL=INFO                            # 日志级别: DEBUG, INFO, WARNING, ERROR
```

### 评测维度配置

| 维度 | 名称 | 权重 | 说明 |
|------|------|------|------|
| accuracy | 准确性 | 1.0 | 医学信息的准确性 |
| completeness | 完整性 | 1.0 | 信息的完整程度 |
| format | 格式规范 | 1.0 | 病历书写规范 |
| language | 语言表达 | 1.0 | 专业术语使用 |
| logic | 逻辑性 | 1.0 | 结构和逻辑清晰度 |

### 评分标准

```
评分范围: 1-5分
1 - 非常差
2 - 较差
3 - 一般
4 - 良好
5 - 优秀
```

### API调用配置

```python
API_CONFIG = {
    "temperature": 0.0,      # 固定为0提高评估一致性
    "max_retries": 3,        # 最大重试次数
    "retry_delay": 2,        # 重试延迟(秒)
    "timeout": 60            # 超时时间(秒)
}
```

### 评估流程配置

```python
EVALUATION_CONFIG = {
    "include_self_evaluation": True,     # 是否包含模型自我评估
    "save_intermediate_results": True,   # 是否保存中间结果
    "batch_size": 5,                     # 批量处理大小
    "enable_caching": True,              # 是否启用缓存
    "verbose_logging": False             # 是否显示详细日志
}
```

### 输出目录配置

```python
OUTPUT_CONFIG = {
    "base_dir": "output/cross_evaluation_results",  # 基础输出目录
    "evaluations_dir": "evaluations",               # 评测结果目录
    "matrices_dir": "matrices",                     # 矩阵数据目录
    "summary_dir": "summary"                        # 汇总数据目录
}
```

## 模型配置参考

### OpenAI系列

```python
{
    "name": "gpt-5.1",
    "api_endpoint": "https://api.jiekou.ai/openai/v1",
    "model_id": "gpt-5.1",
    "supports_streaming": True,
    "max_tokens": 4096
}
```

### 阿里通义系列

```python
{
    "name": "qwen3-max",
    "api_endpoint": "https://api.jiekou.ai/openai/v1",
    "model_id": "qwen3-max",
    "supports_streaming": True,
    "max_tokens": 8192
}
```

### DeepSeek系列

```python
{
    "name": "deepseek-seed",
    "api_endpoint": "https://api.jiekou.ai/openai/v1",
    "model_id": "deepseek/deepseek-v3.1",
    "supports_streaming": True,
    "max_tokens": 4096
}
```

## 批量配置模板

### 基础模板 (batch_config.json)

```json
{
  "description": "默认批量评测配置",
  "models": [
    "gpt-5.1",
    "qwen3-max",
    "deepseek-seed"
  ],
  "patients": [
    "患者1",
    "患者2",
    "患者3",
    "患者4",
    "患者5"
  ],
  "conversations": [1, 2, 3, 4, 5],
  "settings": {
    "batch_size": 5,
    "parallel": true,
    "max_workers": 3,
    "retry_on_failure": true,
    "save_intermediate": true
  }
}
```

### 单厂商模板 (batch_config_qwen.json)

```json
{
  "description": "通义千问系列批量评测",
  "models": [
    "qwen3-max",
    "qwen3-72b",
    "qwen3-14b",
    "qwen3-7b"
  ],
  "patients": ["患者1", "患者2", "患者3"],
  "conversations": [1, 2, 3],
  "settings": {
    "batch_size": 3,
    "parallel": false
  }
}
```

## 配置优先级

配置加载的优先级（从高到低）：

1. **代码中直接设置的参数**
   ```python
   run_evaluation(model="gpt-5.1", temperature=0.5)  # 最高优先级
   ```

2. **环境变量**
   ```bash
   export DEFAULT_MODEL=qwen3-max
   ```

3. **`.env` 文件**
   ```bash
   DEFAULT_MODEL=gpt-5.1
   ```

4. **配置文件默认值**
   ```python
   DEFAULT_MODEL = "gpt-5.1"  # settings.py中的默认值
   ```

## 配置检查清单

### 首次部署

- [ ] 复制 `.env.example` 为 `.env`
- [ ] 填写 `JIEKOU_API_KEY`
- [ ] 验证API连接: `python test_model_connectivity.py`
- [ ] 检查MongoDB配置 (`server/.env`)
- [ ] 验证模型注册: `python -c "from config import get_model_registry; print(get_model_registry().list_models())"`

### 日常检查

- [ ] API密钥是否有效
- [ ] 模型列表是否最新
- [ ] 批量配置是否正确
- [ ] 输出目录是否可写
- [ ] 日志级别是否合适

### 生产环境

- [ ] 使用环境变量而非 `.env` 文件
- [ ] 设置合适的 `batch_size`
- [ ] 启用 `enable_caching`
- [ ] 关闭 `verbose_logging`
- [ ] 设置合理的 `max_retries` 和 `timeout`

## 性能调优建议

### CPU密集型任务

```python
EVALUATION_CONFIG = {
    "batch_size": 10,        # 增加批量大小
    "enable_caching": True,   # 启用缓存
    "parallel": True,         # 启用并行
    "max_workers": 4          # 增加工作线程
}
```

### API限流场景

```python
API_CONFIG = {
    "max_retries": 5,        # 增加重试次数
    "retry_delay": 5,        # 增加重试延迟
    "timeout": 120,          # 增加超时时间
    "rate_limit": 10         # 限制每秒请求数
}
```

### 内存优化

```python
EVALUATION_CONFIG = {
    "batch_size": 3,                    # 减少批量大小
    "save_intermediate_results": False,  # 不保存中间结果
    "enable_caching": False              # 禁用缓存
}
```

## 故障排查

### API调用失败

```python
# 检查配置
from config import settings
print(f"API Key: {settings.jiekou_api_key[:10]}...")
print(f"Base URL: {settings.jiekou_base_url}")

# 测试连接
python test_model_connectivity.py
```

### 模型未找到

```python
# 检查模型注册
from config import get_model_registry
registry = get_model_registry()
print("已注册模型:", registry.list_models())

# 注册新模型
registry.register_model(
    name="new-model",
    api_endpoint="https://api.example.com/v1",
    api_key="your-key"
)
```

### 评测结果异常

```python
# 启用详细日志
EVALUATION_CONFIG['verbose_logging'] = True

# 降低批量大小
EVALUATION_CONFIG['batch_size'] = 1

# 禁用缓存
EVALUATION_CONFIG['enable_caching'] = False
```

## 安全建议

1. **API密钥管理**
   - 不要提交 `.env` 到Git
   - 定期轮换API密钥
   - 使用专用密钥管理服务

2. **权限控制**
   - 限制配置文件访问权限
   - 审计配置修改记录
   - 使用只读配置（生产环境）

3. **数据保护**
   - 加密敏感配置
   - 使用HTTPS传输
   - 定期备份配置

---

**维护者**: 项目团队
**最后更新**: 2024-11-21
