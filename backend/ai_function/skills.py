from abc import ABC, abstractmethod

from .providers import ChatMessage


class AISkill(ABC):
    name: str
    description: str

    @abstractmethod
    def build_messages(self, **kwargs) -> list[ChatMessage]:
        ...

    def post_process(self, raw_output: str) -> str:
        return raw_output


class ContinueWritingSkill(AISkill):
    name = "continue_writing"
    description = "续写/扩写：根据已有内容，AI 帮你继续写下去"

    def build_messages(self, **kwargs) -> list[ChatMessage]:
        content = kwargs.get("content", "")
        selected_text = kwargs.get("selected_text", "")

        if selected_text:
            context = f"以下是文章的完整内容，用户选中了其中一段，请从选中位置继续写下去：\n\n{content}\n\n---\n选中的位置（从这里继续）：\n{selected_text}"
        else:
            context = f"以下是一篇正在写的文章，请从末尾自然地继续写下去：\n\n{content}"

        return [
            ChatMessage(
                role="system",
                content=(
                    "你是一个写作助手。请继续以下文本，保持相同的语气、风格和格式。"
                    "直接输出续写内容，不要加任何解释、前缀或总结。"
                    "使用 Markdown 格式。"
                ),
            ),
            ChatMessage(role="user", content=context),
        ]


class PolishSkill(AISkill):
    name = "polish"
    description = "润色/改写：选中文字后让 AI 润色、改变语气或风格"

    def build_messages(self, **kwargs) -> list[ChatMessage]:
        selected_text = kwargs.get("selected_text", "")
        instruction = kwargs.get("instruction", "")

        if not selected_text:
            raise ValueError("selected_text is required for polish skill")

        if instruction:
            prompt = f"请根据以下指令改写这段文字：「{instruction}」\n\n原文：\n{selected_text}"
        else:
            prompt = f"请润色以下文字，使其更流畅、专业，保持原意不变：\n\n{selected_text}"

        return [
            ChatMessage(
                role="system",
                content=(
                    "你是一个文字润色助手。请改写用户提供的文字，保持原意但提升表达质量。"
                    "直接输出改写后的文字，不要加任何解释、前缀或总结。"
                    "保持原文的 Markdown 格式。"
                ),
            ),
            ChatMessage(role="user", content=prompt),
        ]


class GenerateArticleSkill(AISkill):
    name = "generate_article"
    description = "生成全文：给一个主题或大纲，AI 生成整篇博客初稿"

    def build_messages(self, **kwargs) -> list[ChatMessage]:
        topic = kwargs.get("topic", "")
        outline = kwargs.get("outline", "")

        if not topic:
            raise ValueError("topic is required for generate_article skill")

        prompt = f"主题：{topic}"
        if outline:
            prompt += f"\n\n大纲：\n{outline}"

        return [
            ChatMessage(
                role="system",
                content=(
                    "你是一个博客写作助手。请根据用户提供的主题和可选大纲，写一篇完整的博客文章。"
                    "要求：\n"
                    "1. 文章以 # 标题开头\n"
                    "2. 使用 Markdown 格式\n"
                    "3. 内容充实、有深度、条理清晰\n"
                    "4. 语言自然流畅\n"
                    "5. 直接输出文章内容，不要加任何解释"
                ),
            ),
            ChatMessage(role="user", content=prompt),
        ]

    def post_process(self, raw_output: str) -> str:
        # Strip leading/trailing whitespace but preserve structure
        return raw_output.strip()


SKILL_REGISTRY: dict[str, type[AISkill]] = {
    "continue_writing": ContinueWritingSkill,
    "polish": PolishSkill,
    "generate_article": GenerateArticleSkill,
}


def get_skill(name: str) -> AISkill:
    cls = SKILL_REGISTRY.get(name)
    if not cls:
        raise ValueError(f"Unknown skill: {name}. Available: {list(SKILL_REGISTRY.keys())}")
    return cls()


def list_skills() -> list[dict[str, str]]:
    return [
        {"name": cls.name, "description": cls.description}
        for cls in SKILL_REGISTRY.values()
    ]
