"""
统一批量处理器 - Universal Batch Processor
使用通用模型服务进行批量处理,支持所有模型

特性:
- 基于 UniversalModelService 的统一接口
- 支持所有注册的模型(JieKou、百川、豆包、Kimi等)
- 统一的配置格式
- 自动模型路由
- 完整的错误处理和重试机制
"""
import json
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from src.core.model_service import UniversalModelService

logger = logging.getLogger(__name__)


def setup_logging(log_file: str = "unified_batch.log", log_level: str = "INFO"):
    """配置日志"""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ],
        force=True
    )


class UnifiedBatchProcessor:
    """统一批量处理器 - 支持所有模型的通用处理器"""

    def __init__(
        self,
        prompts_file: str,
        records_dir: str,
        output_dir: str = "./output/unified",
        models: List[str] = None,
        max_retries: int = 3,
        max_tokens: int = 2000,
        temperature: float = 0.3,
        model_registry_file: str = "model_registry.json"
    ):
        """
        初始化统一批量处理器

        Args:
            prompts_file: Prompt文件路径
            records_dir: 患者记录目录
            output_dir: 输出目录
            models: 要使用的模型列表(模型名称)
            max_retries: 最大重试次数
            max_tokens: 最大Token数
            temperature: 温度参数
            model_registry_file: 模型注册表文件
        """
        self.prompts_file = prompts_file
        self.records_dir = records_dir
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.max_tokens = max_tokens
        self.temperature = temperature

        # 创建通用模型服务
        self.service = UniversalModelService(model_registry_file)

        # 验证模型
        if models:
            available_models = self.service.list_models()
            for model in models:
                if model not in available_models:
                    raise ValueError(
                        f"模型 '{model}' 未注册。\n"
                        f"可用模型: {', '.join(available_models[:5])}..."
                    )
            self.models = models
        else:
            # 默认使用JieKou的几个模型
            self.models = self.service.list_models("jiekou")[:4]

        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"统一批量处理器已初始化")
        logger.info(f"  Prompts文件: {prompts_file}")
        logger.info(f"  患者记录目录: {records_dir}")
        logger.info(f"  输出目录: {output_dir}")
        logger.info(f"  使用模型: {', '.join(self.models)}")
        logger.info(f"  最大重试次数: {max_retries}")
        logger.info(f"  最大Token数: {max_tokens}")
        logger.info(f"  温度: {temperature}")

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
        处理单个对话

        Args:
            prompt: 提示词
            prompt_index: 提示词索引
            patient_chat: 患者对话记录
            patient_name: 患者名称
            model: 模型名称

        Returns:
            处理结果字典
        """
        conversation_num = str(prompt_index + 1)
        logger.info(f"[{model}][{patient_name}] 开始处理对话 {conversation_num}")

        user_input = f"{prompt} \n {patient_chat}"

        attempt = 0
        while True:  # 无限重试直到获得非空结果
            try:
                start_time = datetime.now()

                # 使用统一模型服务调用
                response = self.service.call(
                    model=model,
                    prompt=user_input,
                    stream=False,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                # 如果返回为空，记录警告并重试
                if not response or response.strip() == "":
                    logger.warning(
                        f"[{model}][{patient_name}] 对话 {conversation_num} "
                        f"返回空内容 (第{attempt+1}次尝试)，将重试..."
                    )
                    wait_time = min(2 ** attempt, 10)  # 最多等待10秒
                    await asyncio.sleep(wait_time)
                    attempt += 1
                    continue  # 继续重试

                # 获得非空结果，成功
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                if attempt > 0:
                    logger.info(
                        f"[{model}][{patient_name}] 对话 {conversation_num} "
                        f"重试成功 (第{attempt+1}次尝试，耗时: {duration:.2f}秒)"
                    )
                else:
                    logger.info(
                        f"[{model}][{patient_name}] 完成对话 {conversation_num} "
                        f"(耗时: {duration:.2f}秒)"
                    )

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

                # 异常情况：达到最大重试次数后才报错
                if attempt < self.max_retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    logger.warning(
                        f"[{model}][{patient_name}] 对话 {conversation_num} "
                        f"失败 (第{attempt+1}次尝试): {error_msg}"
                    )
                    logger.info(
                        f"[{model}][{patient_name}] 将在 {wait_time} 秒后重试..."
                    )
                    await asyncio.sleep(wait_time)
                    attempt += 1
                else:
                    logger.error(
                        f"[{model}][{patient_name}] 对话 {conversation_num} "
                        f"最终失败 (已重试{self.max_retries}次): {error_msg}"
                    )
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
        """处理一个模型对一个患者的所有对话"""
        patient_name = patient['people']
        patient_chat = patient['chat']

        logger.info(f"[{model}][{patient_name}] 开始处理，共 {len(prompts)} 个对话")
        start_time = datetime.now()

        # 顺序处理所有对话
        results = []
        for idx, prompt in enumerate(prompts):
            result = await self.process_single_conversation(
                prompt, idx, patient_chat, patient_name, model
            )
            results.append(result)

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        # 排序并整合结果
        results = sorted(results, key=lambda x: int(x['index']))

        conversations = {}
        outputs = []
        for result in results:
            idx = result['index']
            conversations[idx] = result['data']
            outputs.append(result['data']['Output'])

        result_text = '\n'.join(outputs)

        output_data = {
            'model': model,
            'people': patient_name,
            'conversations': conversations,
            'result': result_text
        }

        success_count = sum(1 for r in results if r['status'] == 'success')
        logger.info(
            f"[{model}][{patient_name}] 处理完成 "
            f"(成功: {success_count}/{len(results)}, 耗时: {total_duration:.2f}秒)"
        )

        return output_data

    async def process_all(self) -> List[Dict[str, Any]]:
        """处理所有模型和患者的组合"""
        prompts = self.load_prompts()
        patients = self.load_patient_records()

        total_tasks = len(self.models) * len(patients)
        logger.info(
            f"开始批量处理: {len(self.models)} 个模型 × "
            f"{len(patients)} 个患者 = {total_tasks} 个文件"
        )

        # 顺序处理所有(模型, 患者)组合
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
            # 文件名使用安全的格式
            safe_model_name = model.replace('/', '_')
            filename = f"{safe_model_name}-{people}.json"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            logger.info(f"  已保存: {filename}")

        logger.info(f"所有结果已保存到: {self.output_dir}")

    async def run(self):
        """运行批量处理"""
        logger.info("=" * 80)
        logger.info("开始统一批量处理任务")
        logger.info("=" * 80)

        total_start = datetime.now()
        results = await self.process_all()
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


def load_config(config_file: str = "unified_batch_config.json") -> Dict[str, Any]:
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


async def main(config_file: str = "unified_batch_config.json"):
    """主函数"""
    config = load_config(config_file)

    setup_logging(
        log_file=config.get("log_file", "unified_batch.log"),
        log_level=config.get("log_level", "INFO")
    )

    print("\n" + "=" * 80)
    print("统一批量处理系统 - Universal Batch Processor")
    print("=" * 80 + "\n")

    print(f"配置信息:")
    print(f"  配置文件: {config_file}")
    print(f"  Prompts文件: {config['prompts_file']}")
    print(f"  患者记录目录: {config['records_dir']}")
    print(f"  输出目录: {config['output_dir']}")
    print(f"  使用模型: {', '.join(config['models'])}")
    print(f"  最大重试次数: {config.get('max_retries', 3)}")
    print(f"  最大Token数: {config.get('max_tokens', 2000)}")
    print(f"  温度: {config.get('temperature', 0.3)}")
    print()

    processor = UnifiedBatchProcessor(
        prompts_file=config['prompts_file'],
        records_dir=config['records_dir'],
        output_dir=config['output_dir'],
        models=config['models'],
        max_retries=config.get('max_retries', 3),
        max_tokens=config.get('max_tokens', 2000),
        temperature=config.get('temperature', 0.3),
        model_registry_file=config.get('model_registry_file', 'model_registry.json')
    )

    results = await processor.run()

    print("\n" + "=" * 80)
    print("处理完成！")
    print(f"共生成 {len(results)} 个JSON文件")
    print(f"输出目录: {config['output_dir']}/")
    print("\n生成的文件：")
    for result in results:
        safe_model = result['model'].replace('/', '_')
        print(f"  - {safe_model}-{result['people']}.json")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
