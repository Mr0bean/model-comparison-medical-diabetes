# JieKou AI Chat Client

基于 JieKou AI API 的功能完善的 Python Chat 客户端，支持流式和非流式对话、多会话管理、丰富的参数配置等功能。

## 特性

- ✨ **流式和非流式输出**：支持实时流式响应和完整响应两种模式
- 💬 **对话历史管理**：自动管理对话上下文，支持多轮对话
- 🎛️ **丰富的参数配置**：支持 temperature、max_tokens、top_p、penalties 等参数
- 🔄 **多会话管理**：通过 ConversationManager 管理多个独立的对话会话
- 🛡️ **错误处理和日志**：完善的错误处理和日志记录
- ⚙️ **配置管理**：基于 pydantic-settings 的配置管理，支持 .env 文件
- 🎨 **交互式界面**：提供美观的命令行交互界面（使用 rich 库）

## 安装

### 1. 克隆或下载项目

```bash
cd chat
```

### 2. 创建虚拟环境（推荐）

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 或使用 conda
conda create -n chat-client python=3.9
conda activate chat-client
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API Key

复制 `.env.example` 为 `.env` 并填入你的 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
JIEKOU_API_KEY=your_actual_api_key_here
JIEKOU_BASE_URL=https://api.jiekou.ai/openai
DEFAULT_MODEL=deepseek/deepseek-r1
```

## 快速开始

### 基础使用

```python
from chat_client import ChatClient

# 创建客户端
client = ChatClient(
    system_prompt="你是一个专业的AI助手。"
)

# 非流式对话
response = client.chat(
    message="你好！",
    stream=False
)
print(response)

# 流式对话
for chunk in client.chat(message="介绍一下Python", stream=True):
    print(chunk, end="", flush=True)
```

### 交互式聊天

运行交互式聊天程序：

```bash
cd examples
python interactive_chat.py
```

支持的命令：
- `/help` - 显示帮助信息
- `/clear` - 清空对话历史
- `/history` - 显示对话历史
- `/system <msg>` - 添加系统消息
- `/model <name>` - 切换模型
- `/temp <value>` - 设置 temperature
- `/tokens <num>` - 设置 max_tokens
- `/quit` 或 `/exit` - 退出程序

## 使用示例

项目提供了多个示例文件，展示各种使用场景：

### 1. 基础使用 (basic_usage.py)

```bash
cd examples
python basic_usage.py
```

展示：
- 非流式对话
- 流式对话
- 对话历史管理

### 2. 高级使用 (advanced_usage.py)

```bash
cd examples
python advanced_usage.py
```

展示：
- Temperature 参数调优
- Max Tokens 控制输出长度
- Frequency/Presence Penalty 减少重复
- Stop Sequence 控制停止条件
- 多轮连续对话

### 3. 会话管理 (session_manager_usage.py)

```bash
cd examples
python session_manager_usage.py
```

展示：
- 创建多个独立会话
- 不同会话使用不同角色
- 会话历史管理
- 会话的创建和删除

## API 文档

### ChatClient

主要的聊天客户端类。

#### 初始化

```python
client = ChatClient(
    api_key=None,           # API密钥，不提供则从配置读取
    base_url=None,          # API基础URL
    model=None,             # 默认模型
    system_prompt=None      # 系统提示词
)
```

#### 方法

##### chat()

发送消息并获取回复。

```python
response = client.chat(
    message="你的消息",
    stream=False,                    # 是否流式输出
    temperature=0.7,                 # 温度参数 (0-2)
    max_tokens=2048,                 # 最大token数
    top_p=None,                      # 核采样参数
    frequency_penalty=None,          # 频率惩罚 (-2.0 到 2.0)
    presence_penalty=None,           # 存在惩罚 (-2.0 到 2.0)
    stop=None,                       # 停止序列
    model=None,                      # 使用的模型
    save_to_history=True             # 是否保存到历史
)
```

**返回值：**
- `stream=False`: 返回完整回复字符串
- `stream=True`: 返回迭代器，逐块返回内容

##### simple_chat()

简单对话，不保存历史。

```python
response = client.simple_chat(
    message="你的消息",
    system_prompt=None,     # 临时系统提示词
    **kwargs                # 其他参数同 chat()
)
```

##### 历史管理方法

```python
# 添加消息
client.add_system_message("系统消息")
client.add_user_message("用户消息")
client.add_assistant_message("助手消息")

# 获取历史
history = client.get_history()

# 清空历史
client.clear_history(keep_system=True)  # 保留系统消息
```

### ConversationManager

多会话管理器。

```python
manager = ConversationManager()

# 创建会话
session = manager.create_session(
    session_id="session_1",
    model="deepseek/deepseek-r1",
    system_prompt="你是一个Python专家"
)

# 获取会话
session = manager.get_session("session_1")

# 删除会话
manager.delete_session("session_1")

# 列出所有会话
sessions = manager.list_sessions()

# 清空所有会话
manager.clear_all()
```

### Message

消息构建类。

```python
from chat_client import Message

# 创建消息
system_msg = Message.system("系统提示")
user_msg = Message.user("用户消息")
assistant_msg = Message.assistant("助手回复")

# 转换为字典
msg_dict = message.to_dict()
```

## 参数说明

### Temperature

控制输出的随机性和创造性。

- **范围**: 0.0 - 2.0
- **低值 (0.1-0.5)**: 输出更确定、一致，适合事实性任务
- **中值 (0.6-0.9)**: 平衡创造性和一致性
- **高值 (1.0-2.0)**: 输出更随机、有创意，适合创作任务

### Max Tokens

控制输出的最大长度。

- **范围**: > 0
- **建议**: 根据需求设置，一般对话用 512-2048

### Top P (核采样)

另一种控制随机性的方法，与 temperature 二选一使用。

- **范围**: 0.0 - 1.0
- **建议**: 使用 temperature 或 top_p，不要同时使用

### Frequency Penalty

减少模型重复使用相同的词语。

- **范围**: -2.0 - 2.0
- **正值**: 减少重复
- **负值**: 增加重复

### Presence Penalty

鼓励模型谈论新话题。

- **范围**: -2.0 - 2.0
- **正值**: 鼓励新话题
- **负值**: 允许重复话题

### Stop Sequence

指定停止生成的字符串。

- **类型**: 字符串或字符串列表
- **示例**: `stop=["END", "\n\n"]`

## 配置文件

`.env` 文件支持的配置项：

```env
# API 配置
JIEKOU_API_KEY=your_api_key
JIEKOU_BASE_URL=https://api.jiekou.ai/openai

# 默认模型设置
DEFAULT_MODEL=deepseek/deepseek-r1
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2048
DEFAULT_STREAM=true

# 日志级别
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 错误处理

客户端会自动处理常见错误：

```python
from chat_client import ChatClient

try:
    client = ChatClient()
    response = client.chat("你好")
except ValueError as e:
    print(f"配置错误: {e}")
except Exception as e:
    print(f"请求失败: {e}")
```

## 最佳实践

### 1. 使用系统提示词

为不同任务设置合适的系统提示词：

```python
# 代码助手
client = ChatClient(
    system_prompt="你是一个专业的Python编程助手，精通代码优化和最佳实践。"
)

# 翻译助手
client = ChatClient(
    system_prompt="你是一个专业的中英文翻译，翻译要准确、流畅、符合语言习惯。"
)
```

### 2. 合理使用流式输出

- **流式**: 适合长文本生成，提供实时反馈
- **非流式**: 适合需要完整响应后处理的场景

```python
# 流式 - 用户体验更好
for chunk in client.chat("写一篇文章", stream=True):
    print(chunk, end="", flush=True)

# 非流式 - 便于后处理
response = client.chat("总结这段文字", stream=False)
process_response(response)
```

### 3. 多会话管理

对于不同任务，使用独立的会话：

```python
manager = ConversationManager()

# 代码审查会话
code_review = manager.create_session(
    "code_review",
    system_prompt="你是代码审查专家"
)

# 文档写作会话
doc_writer = manager.create_session(
    "doc_writer",
    system_prompt="你是技术文档写作专家"
)
```

### 4. 参数调优

根据任务类型调整参数：

```python
# 事实性任务 - 低 temperature
client.chat("什么是Python?", temperature=0.3)

# 创作任务 - 高 temperature
client.chat("写一首诗", temperature=1.2)

# 减少重复 - frequency_penalty
client.chat("列举10个...", frequency_penalty=1.0)
```

### 5. 控制成本

合理设置 max_tokens：

```python
# 简短回答
client.chat("是或否", max_tokens=10)

# 详细解释
client.chat("详细介绍...", max_tokens=2000)
```

## 支持的模型

JieKou AI 支持多种模型，常用的包括：

- `deepseek/deepseek-r1` - 推理增强模型
- 更多模型请查看: https://jiekou.ai/#model-library

切换模型：

```python
# 初始化时指定
client = ChatClient(model="deepseek/deepseek-r1")

# 运行时切换
client.model = "other-model"

# 单次请求指定
client.chat("你好", model="specific-model")
```

## 日志

项目使用 Python 标准 logging 模块，通过 `.env` 配置日志级别：

```env
LOG_LEVEL=DEBUG  # 显示详细信息
LOG_LEVEL=INFO   # 显示一般信息（默认）
LOG_LEVEL=WARNING # 只显示警告和错误
```

## 故障排查

### API Key 错误

```
ValueError: API Key未配置
```

**解决方案**: 确保 `.env` 文件中正确设置了 `JIEKOU_API_KEY`

### 连接错误

```
Connection error
```

**解决方案**:
1. 检查网络连接
2. 确认 API 基础 URL 正确
3. 检查防火墙设置

### 参数错误

```
Invalid parameter value
```

**解决方案**: 检查参数范围，参考本文档的参数说明部分

## 项目结构

```
chat/
├── chat_client.py          # 核心客户端实现
├── config.py               # 配置管理
├── requirements.txt        # 依赖包
├── .env.example           # 配置文件示例
├── .env                   # 实际配置（不提交到git）
├── .gitignore            # Git忽略文件
├── README.md             # 本文档
└── examples/             # 示例代码
    ├── basic_usage.py           # 基础使用
    ├── advanced_usage.py        # 高级使用
    ├── session_manager_usage.py # 会话管理
    └── interactive_chat.py      # 交互式聊天
```

## 依赖

- `openai>=1.0.0` - OpenAI API 客户端
- `python-dotenv>=1.0.0` - 环境变量管理
- `pydantic>=2.0.0` - 数据验证
- `pydantic-settings>=2.0.0` - 配置管理
- `rich>=13.0.0` - 终端美化（仅交互式界面需要）

## 许可

本项目仅供学习和参考使用。

## 相关链接

- [JieKou AI 官网](https://jiekou.ai/)
- [JieKou AI 文档](https://docs.jiekou.ai/)
- [模型列表](https://jiekou.ai/#model-library)

## 更新日志

### v1.0.0 (2025-01-15)

- 初始版本发布
- 支持流式和非流式对话
- 完整的参数配置支持
- 多会话管理
- 交互式聊天界面
- 完善的示例和文档
