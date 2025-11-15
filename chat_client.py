"""
JieKou AI Chat 客户端
支持流式和非流式对话，提供丰富的参数配置选项
"""
import logging
from typing import List, Dict, Optional, Iterator, Union, Literal
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from config import settings


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Message:
    """消息类，用于构建对话消息"""

    def __init__(
        self,
        role: Literal["system", "user", "assistant"],
        content: str
    ):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            "role": self.role,
            "content": self.content
        }

    @classmethod
    def system(cls, content: str) -> "Message":
        """创建系统消息"""
        return cls("system", content)

    @classmethod
    def user(cls, content: str) -> "Message":
        """创建用户消息"""
        return cls("user", content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        """创建助手消息"""
        return cls("assistant", content)


class ChatClient:
    """
    JieKou AI Chat 客户端

    支持功能：
    - 流式和非流式对话
    - 对话历史管理
    - 多种参数配置
    - 错误处理和重试
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        """
        初始化 Chat 客户端

        Args:
            api_key: API密钥，如果不提供则从配置文件读取
            base_url: API基础URL，如果不提供则从配置文件读取
            model: 默认使用的模型
            system_prompt: 系统提示词
        """
        # 验证API Key
        self.api_key = api_key or settings.jiekou_api_key
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError(
                "API Key未配置。请在.env文件中设置JIEKOU_API_KEY或通过参数传入"
            )

        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url or settings.jiekou_base_url,
            timeout=60.0  # 增加超时时间到60秒
        )

        # 默认配置
        self.model = model or settings.default_model
        self.conversation_history: List[Dict[str, str]] = []

        # 如果提供了系统提示词，添加到对话历史
        if system_prompt:
            self.add_system_message(system_prompt)

        logger.info(f"ChatClient initialized with model: {self.model}")

    def add_system_message(self, content: str) -> None:
        """添加系统消息"""
        message = Message.system(content)
        self.conversation_history.append(message.to_dict())
        logger.debug(f"Added system message: {content[:50]}...")

    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        message = Message.user(content)
        self.conversation_history.append(message.to_dict())
        logger.debug(f"Added user message: {content[:50]}...")

    def add_assistant_message(self, content: str) -> None:
        """添加助手消息"""
        message = Message.assistant(content)
        self.conversation_history.append(message.to_dict())
        logger.debug(f"Added assistant message: {content[:50]}...")

    def clear_history(self, keep_system: bool = True) -> None:
        """
        清空对话历史

        Args:
            keep_system: 是否保留系统消息
        """
        if keep_system:
            self.conversation_history = [
                msg for msg in self.conversation_history
                if msg["role"] == "system"
            ]
        else:
            self.conversation_history = []
        logger.info("Conversation history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.conversation_history.copy()

    def chat(
        self,
        message: str,
        stream: Optional[bool] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = 10000,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        model: Optional[str] = None,
        save_to_history: bool = True
    ) -> Union[str, Iterator[str]]:
        """
        发送消息并获取回复

        Args:
            message: 用户消息
            stream: 是否使用流式输出，None时使用默认配置
            temperature: 温度参数(0-2)，控制随机性
            max_tokens: 最大token数
            top_p: 核采样参数(0-1)
            frequency_penalty: 频率惩罚(-2.0到2.0)
            presence_penalty: 存在惩罚(-2.0到2.0)
            stop: 停止序列
            model: 使用的模型，None时使用默认模型
            save_to_history: 是否保存到对话历史

        Returns:
            如果stream=False，返回完整回复字符串
            如果stream=True，返回迭代器，每次返回一个片段
        """
        # 添加用户消息到历史
        if save_to_history:
            self.add_user_message(message)

        # 准备消息列表
        messages = self.conversation_history.copy()
        if not save_to_history:
            # 如果不保存历史，临时添加用户消息
            messages.append(Message.user(message).to_dict())

        # 准备参数
        use_stream = stream if stream is not None else settings.default_stream
        use_model = model or self.model

        params = {
            "model": use_model,
            "messages": messages,
            "stream": use_stream,
        }

        # 添加可选参数
        if temperature is not None:
            params["temperature"] = temperature
        elif settings.default_temperature is not None:
            params["temperature"] = settings.default_temperature

        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        elif settings.default_max_tokens is not None:
            params["max_tokens"] = settings.default_max_tokens

        if top_p is not None:
            params["top_p"] = top_p

        if frequency_penalty is not None:
            params["frequency_penalty"] = frequency_penalty

        if presence_penalty is not None:
            params["presence_penalty"] = presence_penalty

        if stop is not None:
            params["stop"] = stop

        logger.info(f"Sending chat request: model={use_model}, stream={use_stream}")

        try:
            response = self.client.chat.completions.create(**params)

            if use_stream:
                return self._handle_stream_response(response, save_to_history)
            else:
                return self._handle_normal_response(response, save_to_history)

        except Exception as e:
            logger.error(f"Chat request failed: {str(e)}")
            raise

    def _handle_normal_response(
        self,
        response: ChatCompletion,
        save_to_history: bool
    ) -> str:
        """处理非流式响应"""
        content = response.choices[0].message.content or ""

        if save_to_history:
            self.add_assistant_message(content)

        logger.info(f"Received response: {len(content)} characters")
        return content

    def _handle_stream_response(
        self,
        response: Iterator[ChatCompletionChunk],
        save_to_history: bool
    ) -> Iterator[str]:
        """处理流式响应"""
        full_content = []

        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    content = delta.content
                    full_content.append(content)
                    yield content

        # 流式输出结束后，保存完整回复到历史
        if save_to_history:
            complete_content = "".join(full_content)
            self.add_assistant_message(complete_content)
            logger.info(f"Stream completed: {len(complete_content)} characters")

    def simple_chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """
        简单对话，不保存历史

        Args:
            message: 用户消息
            system_prompt: 系统提示词
            **kwargs: 其他参数传递给chat方法

        Returns:
            模型回复
        """
        messages = []
        if system_prompt:
            messages.append(Message.system(system_prompt).to_dict())
        messages.append(Message.user(message).to_dict())

        use_stream = kwargs.get('stream', settings.default_stream)
        use_model = kwargs.get('model', self.model)

        params = {
            "model": use_model,
            "messages": messages,
            "stream": use_stream,
        }

        # 添加其他参数
        for key in ['temperature', 'max_tokens', 'top_p', 'frequency_penalty',
                    'presence_penalty', 'stop']:
            if key in kwargs:
                params[key] = kwargs[key]

        logger.info(f"Simple chat request: model={use_model}, stream={use_stream}")

        try:
            response = self.client.chat.completions.create(**params)

            if use_stream:
                return self._stream_simple_response(response)
            else:
                return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"Simple chat request failed: {str(e)}")
            raise

    def _stream_simple_response(
        self,
        response: Iterator[ChatCompletionChunk]
    ) -> Iterator[str]:
        """处理简单对话的流式响应"""
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content


class ConversationManager:
    """对话管理器，支持多个对话会话"""

    def __init__(self):
        self.sessions: Dict[str, ChatClient] = {}
        logger.info("ConversationManager initialized")

    def create_session(
        self,
        session_id: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ChatClient:
        """
        创建新的对话会话

        Args:
            session_id: 会话ID
            model: 使用的模型
            system_prompt: 系统提示词
            **kwargs: 其他参数传递给ChatClient

        Returns:
            ChatClient实例
        """
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists, will be replaced")

        client = ChatClient(
            model=model,
            system_prompt=system_prompt,
            **kwargs
        )
        self.sessions[session_id] = client
        logger.info(f"Created session: {session_id}")
        return client

    def get_session(self, session_id: str) -> Optional[ChatClient]:
        """获取指定会话"""
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """删除指定会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def list_sessions(self) -> List[str]:
        """列出所有会话ID"""
        return list(self.sessions.keys())

    def clear_all(self) -> None:
        """清空所有会话"""
        self.sessions.clear()
        logger.info("All sessions cleared")
