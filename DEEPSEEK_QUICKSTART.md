# DeepSeek官方API 快速开始

## 🎯 快速配置（3步搞定）

### 步骤1: 安装依赖
```bash
pip install openai
```

### 步骤2: 配置API密钥
```bash
# 方法A: 使用配置向导（推荐）
python scripts/setup_deepseek.py

# 方法B: 手动配置
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY=sk-your-key-here
```

### 步骤3: 测试连接
```bash
python test_deepseek.py
```

## 📝 基础使用

### 最简示例
```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "Hello"}
    ]
)

print(response.choices[0].message.content)
```

### 使用配置类
```python
from config import deepseek_settings, is_deepseek_configured
from openai import OpenAI

# 检查配置
if not is_deepseek_configured():
    print("请先配置API密钥")
    exit(1)

# 创建客户端
client = OpenAI(
    api_key=deepseek_settings.api_key,
    base_url=deepseek_settings.base_url
)

# 使用配置参数
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hi"}],
    **deepseek_settings.get_model_config()
)
```

## 📚 完整示例

运行完整示例查看所有功能：
```bash
python examples/deepseek_official_example.py
```

示例包括：
- ✅ 基础对话
- ✅ 流式输出
- ✅ 医疗助手
- ✅ 多轮对话
- ✅ 配置类使用
- ✅ 错误处理

## 🔧 配置文件

| 文件 | 说明 |
|------|------|
| `config/deepseek.py` | DeepSeek配置类 |
| `config/DEEPSEEK_GUIDE.md` | 完整使用指南 |
| `.env` | 环境变量配置 |

## 🧪 测试工具

| 脚本 | 功能 |
|------|------|
| `python test_deepseek.py` | 测试配置和连接 |
| `python scripts/setup_deepseek.py` | 配置向导 |
| `python examples/deepseek_official_example.py` | 完整示例 |

## 🆘 常见问题

**Q: API调用失败？**
```bash
# 1. 检查配置
python test_deepseek.py

# 2. 重新配置
python scripts/setup_deepseek.py
```

**Q: 如何获取API密钥？**
访问 https://platform.deepseek.com/ 注册并申请

**Q: 支持哪些模型？**
- deepseek-chat (通用对话)
- deepseek-coder (代码专用)
- deepseek-reasoner (推理增强)

## 📖 完整文档

详细使用指南: [config/DEEPSEEK_GUIDE.md](config/DEEPSEEK_GUIDE.md)

---

**提示**: 请妥善保管您的API密钥，不要提交到代码仓库！
