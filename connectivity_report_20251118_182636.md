# 模型连通性测试报告
**测试时间**: 2025-11-18T18:26:01.004584
**测试模型数**: 11
**成功**: 8 | **失败**: 3

## 详细结果
| 模型 | 提供商 | API状态 | 响应时间 | 备注 |
|------|--------|---------|----------|------|
| Baichuan-M2 | 百川智能 | ✅ | 0.59s | 连接正常 |
| deepseek/deepseek-v3.1 | JieKou API | ✅ | 4.56s | 连接正常 |
| doubao-seed-1-6-251015 | 豆包 (火山引擎) | ✅ | 1.92s | 连接正常 |
| gemini-2.5-pro | JieKou API | ✅ | 4.83s | 连接正常 |
| gpt-5.1 | JieKou API | ✅ | 2.63s | 连接正常 |
| grok-4-0709 | JieKou API | ✅ | 8.31s | 连接正常 |
| moonshot-v1-128k | Kimi (月之暗面) | ❌ | N/A | 连接失败 |
| moonshot-v1-32k | Kimi (月之暗面) | ❌ | N/A | 连接失败 |
| moonshot-v1-8k | Kimi (月之暗面) | ❌ | N/A | 连接失败 |
| moonshotai/kimi-k2-0905 | Kimi (月之暗面) via JieKou | ✅ | 3.59s | 连接正常 |
| qwen3-max | 通义千问 (阿里云) | ✅ | 0.6s | 连接正常 |

## 问题诊断

### 失败的模型:
- **moonshot-v1-128k** (Kimi (月之暗面)):
  - 问题: 缺少API密钥
  - 解决: 在对应的配置文件中设置API密钥

- **moonshot-v1-32k** (Kimi (月之暗面)):
  - 问题: 缺少API密钥
  - 解决: 在对应的配置文件中设置API密钥

- **moonshot-v1-8k** (Kimi (月之暗面)):
  - 问题: 缺少API密钥
  - 解决: 在对应的配置文件中设置API密钥

