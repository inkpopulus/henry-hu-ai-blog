from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str  # "system", "user", "assistant"
    content: str


class AIProvider(ABC):
    @abstractmethod
    async def stream_chat(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        ...


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, base_url: str | None = None, extra_body: dict | None = None):
        import openai
        self.client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.extra_body = extra_body

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        kwargs = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if self.extra_body:
            kwargs["extra_body"] = self.extra_body
        stream = await self.client.chat.completions.create(**kwargs)
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str, base_url: str | None = None):
        import anthropic
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = anthropic.AsyncAnthropic(**kwargs)

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        # Anthropic requires system message separate from messages
        system_text = ""
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system_text = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        kwargs = {
            "model": model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_text:
            kwargs["system"] = system_text

        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text


class DashScopeProvider(OpenAIProvider):
    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def __init__(self, api_key: str, base_url: str | None = None):
        super().__init__(api_key=api_key, base_url=base_url or self.BASE_URL)


PROVIDER_REGISTRY: dict[str, type[AIProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "dashscope": DashScopeProvider,
}


def get_provider(name: str, api_key: str, base_url: str | None = None, extra_body: dict | None = None) -> AIProvider:
    cls = PROVIDER_REGISTRY.get(name)
    if not cls:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDER_REGISTRY.keys())}")
    if cls is OpenAIProvider or issubclass(cls, OpenAIProvider):
        return cls(api_key=api_key, base_url=base_url, extra_body=extra_body)
    return cls(api_key=api_key, base_url=base_url)
