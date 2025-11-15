"""
批量处理脚本 - 豆包 (火山引擎) 基座
API文档: https://www.volcengine.com/docs/82379/1263482
输出：./output/raw_doubao/{model}-{people}.json
"""
import json
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


def load_config(config_file: str = "batch_config_doubao.json") -> Dict[str, Any]:
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


def setup_logging(log_file: str = "batch_process_doubao.log", log_level: str = "INFO"):
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


class DoubaoBatchProcessor:
    """豆包基座批量处理器"""

    def __init__(
        self,
        prompts_file: str,
        records_dir: str,
        output_dir: str = "./output/raw_doubao",
        models: List[str] = None,
        max_retries: int = 3,
        max_tokens: int = 2000,
        api_key: Optional[str] = None,
        base_url: str = "https://ark.cn-beijing.volces.com/api/v3",
        endpoint_id: Optional[str] = None
    ):
        self.prompts_file = prompts_file
        self.records_dir = records_dir
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.max_tokens = max_tokens
        self.api_key = api_key or os.getenv("ARK_API_KEY") or os.getenv("DOUBAO_API_KEY")
        self.base_url = base_url
        self.endpoint_id = endpoint_id

        # 默认模型列表（实际使用时需要替换为endpoint ID）
        self.models = models or [
            "doubao-pro-4k",
            "doubao-pro-32k",
            "doubao-pro-128k"
        ]

        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 创建客户端
        if not self.api_key:
            raise ValueError("豆包 API Key 未配置，请设置 ARK_API_KEY 或 DOUBAO_API_KEY 环境变量")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )

        logger.info(f"初始化豆包批量处理器")
        logger.info(f"  API 地址: {base_url}")
        logger.info(f"  Endpoint ID: {endpoint_id or '使用模型名称'}")
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
        """处理单个对话（一个Prompt），支持自动重试"""
        conversation_num = str(prompt_index + 1)
        logger.info(f"[{model}][{patient_name}] 开始处理对话 {conversation_num}")

        user_input = f"{prompt} \n {patient_chat}"

        # 如果设置了 endpoint_id，使用它替代模型名
        actual_model = self.endpoint_id if self.endpoint_id else model

        for attempt in range(self.max_retries):
            try:
                start_time = datetime.now()

                # 调用豆包 API
                completion = self.client.chat.completions.create(
                    model=actual_model,
                    messages=[
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=0.3
                )

                response = completion.choices[0].message.content

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
                    wait_time = 2 ** attempt
                    logger.warning(f"[{model}][{patient_name}] 对话 {conversation_num} 失败 (第{attempt+1}次尝试): {error_msg}")
                    logger.info(f"[{model}][{patient_name}] 将在 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
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
        """处理一个模型对一个患者的所有对话"""
        patient_name = patient['people']
        patient_chat = patient['chat']

        logger.info(f"[{model}][{patient_name}] 开始处理，共 {len(prompts)} 个对话")
        start_time = datetime.now()

        tasks = [
            self.process_single_conversation(
                prompt, idx, patient_chat, patient_name, model
            )
            for idx, prompt in enumerate(prompts)
        ]

        results = await asyncio.gather(*tasks)

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

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
        logger.info(f"[{model}][{patient_name}] 处理完成 (成功: {success_count}/{len(results)}, 耗时: {total_duration:.2f}秒)")

        return output_data

    async def process_all(self) -> List[Dict[str, Any]]:
        """处理所有模型和患者的组合"""
        prompts = self.load_prompts()
        patients = self.load_patient_records()

        total_tasks = len(self.models) * len(patients)
        logger.info(f"开始批量处理: {len(self.models)} 个模型 × {len(patients)} 个患者 = {total_tasks} 个文件")

        tasks = []
        for model in self.models:
            for patient in patients:
                tasks.append(
                    self.process_model_patient(model, patient, prompts)
                )

        results = await asyncio.gather(*tasks)
        logger.info(f"所有任务处理完成，共生成 {len(results)} 个文件")
        return results

    def save_results(self, results: List[Dict[str, Any]]):
        """保存结果到独立的JSON文件"""
        logger.info(f"开始保存结果文件到: {self.output_dir}")

        for result in results:
            model = result['model']
            people = result['people']
            filename = f"{model}-{people}.json"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            logger.info(f"  已保存: {filename}")

        logger.info(f"所有结果已保存到: {self.output_dir}")

    async def run(self):
        """运行批量处理"""
        logger.info("=" * 80)
        logger.info("开始批量处理任务（豆包基座）")
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


async def main(config_file: str = "batch_config_doubao.json"):
    """主函数"""
    config = load_config(config_file)

    setup_logging(
        log_file=config.get("log_file", "batch_process_doubao.log"),
        log_level=config.get("log_level", "INFO")
    )

    print("\n" + "=" * 80)
    print("批量处理系统 - 豆包 (火山引擎) 基座")
    print("=" * 80 + "\n")

    api_config = config.get("api_config", {})

    print(f"配置信息:")
    print(f"  配置文件: {config_file}")
    print(f"  API地址: {api_config.get('base_url', 'https://ark.cn-beijing.volces.com/api/v3')}")
    print(f"  Endpoint ID: {api_config.get('endpoint_id', '使用模型名称')}")
    print(f"  Prompts文件: {config['prompts_file']}")
    print(f"  患者记录目录: {config['records_dir']}")
    print(f"  输出目录: {config['output_dir']}")
    print(f"  使用模型: {', '.join(config['models'])}")
    print(f"  最大重试次数: {config.get('max_retries', 3)}")
    print(f"  最大Token数: {config.get('max_tokens', 2000)}")
    print()

    processor = DoubaoBatchProcessor(
        prompts_file=config['prompts_file'],
        records_dir=config['records_dir'],
        output_dir=config['output_dir'],
        models=config['models'],
        max_retries=config.get('max_retries', 3),
        max_tokens=config.get('max_tokens', 2000),
        api_key=api_config.get('api_key'),
        base_url=api_config.get('base_url', 'https://ark.cn-beijing.volces.com/api/v3'),
        endpoint_id=api_config.get('endpoint_id')
    )

    results = await processor.run()

    print("\n" + "=" * 80)
    print("处理完成！")
    print(f"共生成 {len(results)} 个JSON文件")
    print(f"输出目录: {config['output_dir']}/")
    print("\n生成的文件：")
    for result in results:
        print(f"  - {result['model']}-{result['people']}.json")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
