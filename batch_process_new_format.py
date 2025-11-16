"""
批量处理脚本 - 新输出格式
输出：./output/raw/{model}-{people}.json
"""
import json
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from chat_client import ChatClient
import logging

logger = logging.getLogger(__name__)


def load_config(config_file: str = "batch_config.json") -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        config_file: 配置文件路径（默认：batch_config.json）

    Returns:
        配置字典
    """
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


def setup_logging(log_file: str = "batch_process_new.log", log_level: str = "INFO"):
    """
    配置日志

    Args:
        log_file: 日志文件名
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


class NewFormatBatchProcessor:
    """新格式批量处理器"""

    def __init__(
        self,
        prompts_file: str,
        records_dir: str,
        output_dir: str = "./output/raw",
        models: List[str] = None,
        max_retries: int = 3,
        max_tokens: int = 2000
    ):
        """
        初始化处理器

        Args:
            prompts_file: Prompt文件路径
            records_dir: 患者记录目录
            output_dir: 输出目录（默认：./output/raw）
            models: 模型列表
            max_retries: 最大重试次数（默认：3）
            max_tokens: 最大Token数（默认：2000）
        """
        self.prompts_file = prompts_file
        self.records_dir = records_dir
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.max_tokens = max_tokens

        # 默认模型列表
        self.models = models or [
            "gemini-2.5-pro",
            "deepseek/deepseek-v3.1",
            "moonshotai/kimi-k2-0905",
            "grok-4-0709"
        ]

        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"初始化新格式批量处理器")
        logger.info(f"  Prompts文件: {prompts_file}")
        logger.info(f"  患者记录目录: {records_dir}")
        logger.info(f"  输出目录: {output_dir}")
        logger.info(f"  使用模型: {', '.join(self.models)}")
        logger.info(f"  最大重试次数: {max_retries}")
        logger.info(f"  最大Token数: {max_tokens}")

    def load_prompts(self) -> List[str]:
        """加载所有Prompts"""
        logger.info(f"正在加载Prompts文件: {self.prompts_file}")

        with open(self.prompts_file, 'r', encoding='utf-8') as f:
            prompts = json.load(f)

        logger.info(f"成功加载 {len(prompts)} 个Prompts")
        return prompts

    def load_patient_records(self) -> List[Dict[str, Any]]:
        """加载所有患者记录"""
        logger.info(f"正在扫描患者记录目录: {self.records_dir}")

        records = []
        records_path = Path(self.records_dir)

        for file_path in sorted(records_path.glob("*.txt")):
            logger.info(f"  发现患者文件: {file_path.name}")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取患者编号：去掉"_问答记录.txt"
            patient_name = file_path.stem.replace('_问答记录', '')

            records.append({
                'people': patient_name,
                'file_path': str(file_path),
                'chat': content
            })

        logger.info(f"成功加载 {len(records)} 个患者记录")
        return records

    async def process_single_conversation(
        self,
        prompt: str,
        prompt_index: int,
        patient_chat: str,
        patient_name: str,
        model: str
    ) -> Dict[str, Any]:
        """
        处理单个对话（一个Prompt），支持自动重试

        Args:
            prompt: Prompt内容
            prompt_index: Prompt索引（0-based，会转换为1-based）
            patient_chat: 患者问答记录
            patient_name: 患者编号
            model: 模型名称

        Returns:
            对话记录字典
        """
        conversation_num = str(prompt_index + 1)  # 转换为1-based字符串

        logger.info(f"[{model}][{patient_name}] 开始处理对话 {conversation_num}")

        # 构造Input：prompt + chat
        user_input = f"{prompt} \n {patient_chat}"

        # 重试逻辑
        for attempt in range(self.max_retries):
            try:
                start_time = datetime.now()

                # 创建客户端
                client = ChatClient(model=model)

                # 调用API
                response = client.chat(
                    message=user_input,
                    stream=False,
                    max_tokens=self.max_tokens,
                    model=model,
                    temperature=None,
                    top_p=None,
                    frequency_penalty=None,
                    presence_penalty=None
                )

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                if attempt > 0:
                    logger.info(f"[{model}][{patient_name}] 对话 {conversation_num} 重试成功 (第{attempt+1}次尝试，耗时: {duration:.2f}秒)")
                else:
                    logger.info(f"[{model}][{patient_name}] 完成对话 {conversation_num} (耗时: {duration:.2f}秒)")

                return {
                    'index': conversation_num,
                    'data': {
                        'model': model,
                        'prompt': prompt,
                        'people': patient_name,
                        'chat': patient_chat,
                        'Input': user_input,
                        'Output': response
                    },
                    'status': 'success',
                    'attempts': attempt + 1
                }

            except Exception as e:
                error_msg = str(e)

                if attempt < self.max_retries - 1:
                    # 还有重试机会
                    wait_time = 2 ** attempt  # 指数退避：1秒、2秒、4秒
                    logger.warning(f"[{model}][{patient_name}] 对话 {conversation_num} 失败 (第{attempt+1}次尝试): {error_msg}")
                    logger.info(f"[{model}][{patient_name}] 将在 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    # 已用完所有重试机会
                    logger.error(f"[{model}][{patient_name}] 对话 {conversation_num} 最终失败 (已重试{self.max_retries}次): {error_msg}")

                    return {
                        'index': conversation_num,
                        'data': {
                            'model': model,
                            'prompt': prompt,
                            'people': patient_name,
                            'chat': patient_chat,
                            'Input': user_input,
                            'Output': f"ERROR: {error_msg}"
                        },
                        'status': 'failed',
                        'attempts': self.max_retries,
                        'error': error_msg
                    }

    async def process_model_patient(
        self,
        model: str,
        patient: Dict[str, Any],
        prompts: List[str]
    ) -> Dict[str, Any]:
        """
        处理一个模型对一个患者的所有对话

        Args:
            model: 模型名称
            patient: 患者记录
            prompts: 所有Prompts

        Returns:
            完整的JSON结构
        """
        patient_name = patient['people']
        patient_chat = patient['chat']

        logger.info(f"[{model}][{patient_name}] 开始处理，共 {len(prompts)} 个对话")
        start_time = datetime.now()

        # 顺序处理所有对话（不并发）
        results = []
        for idx, prompt in enumerate(prompts):
            result = await self.process_single_conversation(
                prompt, idx, patient_chat, patient_name, model
            )
            results.append(result)

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        # 按照index排序（确保顺序）
        results = sorted(results, key=lambda x: int(x['index']))

        # 构建conversations对象
        conversations = {}
        outputs = []

        for result in results:
            idx = result['index']
            conversations[idx] = result['data']
            outputs.append(result['data']['Output'])

        # 拼接result：用换行分隔
        result_text = '\n'.join(outputs)

        # 构建最终JSON结构
        output_data = {
            'model': model,
            'people': patient_name,
            'conversations': conversations,
            'result': result_text
        }

        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = len(results) - success_count

        logger.info(f"[{model}][{patient_name}] 处理完成 (成功: {success_count}/{len(results)}, 耗时: {total_duration:.2f}秒)")

        return output_data

    async def process_all(self) -> List[Dict[str, Any]]:
        """处理所有模型和患者的组合"""
        prompts = self.load_prompts()
        patients = self.load_patient_records()

        total_tasks = len(self.models) * len(patients)
        logger.info(f"开始批量处理: {len(self.models)} 个模型 × {len(patients)} 个患者 = {total_tasks} 个文件")

        # 顺序处理所有(模型, 患者)组合（不并发）
        results = []
        for model in self.models:
            for patient in patients:
                result = await self.process_model_patient(model, patient, prompts)
                results.append(result)

        logger.info(f"所有任务处理完成，共生成 {len(results)} 个文件")

        return results

    def save_results(self, results: List[Dict[str, Any]]):
        """保存结果到独立的JSON文件"""
        logger.info(f"开始保存结果文件到: {self.output_dir}")

        for result in results:
            model = result['model']
            people = result['people']

            # 替换模型名称中的特殊字符（避免路径问题）
            safe_model = model.replace('/', '_').replace('\\', '_')

            # 文件名：{model}-{people}.json
            filename = f"{safe_model}-{people}.json"
            filepath = os.path.join(self.output_dir, filename)

            # 保存JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            logger.info(f"  已保存: {filename}")

        logger.info(f"所有结果已保存到: {self.output_dir}")

    async def run(self):
        """运行批量处理"""
        logger.info("=" * 80)
        logger.info("开始批量处理任务（新格式）")
        logger.info("=" * 80)

        total_start = datetime.now()

        # 处理所有任务
        results = await self.process_all()

        # 保存结果
        self.save_results(results)

        total_end = datetime.now()
        total_duration = (total_end - total_start).total_seconds()

        logger.info("=" * 80)
        logger.info("批量处理任务完成")
        logger.info(f"生成文件数: {len(results)}")
        logger.info(f"总耗时: {total_duration:.2f}秒")
        logger.info(f"输出目录: {self.output_dir}")
        logger.info("=" * 80)

        return results


async def main(config_file: str = "batch_config.json"):
    """
    主函数

    Args:
        config_file: 配置文件路径（默认：batch_config.json）
    """
    # 加载配置
    config = load_config(config_file)

    # 配置日志
    setup_logging(
        log_file=config.get("log_file", "batch_process_new.log"),
        log_level=config.get("log_level", "INFO")
    )

    print("\n" + "=" * 80)
    print("批量处理系统 - 新输出格式")
    print("=" * 80 + "\n")

    print(f"配置信息:")
    print(f"  配置文件: {config_file}")
    print(f"  Prompts文件: {config['prompts_file']}")
    print(f"  患者记录目录: {config['records_dir']}")
    print(f"  输出目录: {config['output_dir']}")
    print(f"  使用模型: {', '.join(config['models'])}")
    print(f"  最大重试次数: {config.get('max_retries', 3)}")
    print(f"  最大Token数: {config.get('max_tokens', 2000)}")
    print()

    # 创建处理器
    processor = NewFormatBatchProcessor(
        prompts_file=config['prompts_file'],
        records_dir=config['records_dir'],
        output_dir=config['output_dir'],
        models=config['models'],
        max_retries=config.get('max_retries', 3),
        max_tokens=config.get('max_tokens', 2000)
    )

    # 运行处理
    results = await processor.run()

    print("\n" + "=" * 80)
    print("处理完成！")
    print(f"共生成 {len(results)} 个JSON文件")
    print(f"输出目录: /")
    print("\n生成的文件：")
    for result in results:
        print(f"  - {result['model']}-{result['people']}.json")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
